from calendar import monthrange
from datetime import date
from decimal import (
    Decimal,
    DecimalException,
    ROUND_HALF_UP,
)

from apps.attendance.models import Attendance
from apps.companies.models import CompanySetting
from apps.leave_management.models import LeaveRequest


DEFAULT_WORKING_DAYS = Decimal("26.00")

DEFAULT_LOP_DIVISOR = Decimal("30.00")

DEFAULT_BONUS_AMOUNT = Decimal("0.00")

TWO_PLACES = Decimal("0.01")

BONUS_DEPARTMENTS = {
    "cnc",
    "grinding",
    "rolling",
    "final inspection",
}

BONUS_EXCLUDED_NAMES = {
    "renuga",
    "sala sambal",
    "poonkodi",
}


def money(value):
    return Decimal(str(value or 0)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP,
    )


def get_setting(company, group, key, default):
    """Return a company-scoped setting value, falling back to ``default``."""
    try:
        setting = CompanySetting.objects.get(
            company=company,
            group=group,
            key=key,
        )

        value = Decimal(str(setting.value or ""))

        if value > 0:
            return value

    except (
        CompanySetting.DoesNotExist,
        DecimalException,
    ):
        pass

    return default


def get_working_days(payroll_run):
    """Return the working-days value for a payroll run.

    Dynamically calculated: calendar days minus Sundays minus holidays.
    Falls back to the configured ``payroll.working_days`` setting (default 26)
    only when no attendance records exist for the month.
    """
    from apps.attendance.models import Holiday

    year = payroll_run.year
    month = payroll_run.month

    calendar_days = monthrange(year, month)[1]

    sundays = sum(
        1
        for day in range(1, calendar_days + 1)
        if date(year, month, day).weekday() == 6
    )

    holidays = Holiday.objects.filter(
        company=payroll_run.company,
        date__year=year,
        date__month=month,
        is_active=True,
    ).count()

    computed = Decimal(str(calendar_days - sundays - holidays))

    if computed > 0:
        return computed

    return get_setting(
        payroll_run.company,
        "payroll",
        "working_days",
        (
            money(payroll_run.working_days)
            if payroll_run.working_days
            and payroll_run.working_days > 0
            else DEFAULT_WORKING_DAYS
        ),
    )


def get_ot_rate(company):
    """Return the configured hourly OT rate, or None to use the fallback.

    The fallback derives an hourly rate from the basic salary
    (basic / working days / 12). Configure ``payroll.ot_rate`` in company
    settings to override it.
    """
    return get_setting(
        company,
        "payroll",
        "ot_rate",
        Decimal("0.00"),
    )


def get_lop_divisor(company):
    """Divisor used to convert monthly earnings into a per-day loss of pay.

    Configurable per company via ``payroll.lop_divisor``; the default of 30
    treats a month as 30 payable days.
    """
    return get_setting(
        company,
        "payroll",
        "lop_divisor",
        DEFAULT_LOP_DIVISOR,
    )


def compute_overtime_amount(
    basic_salary,
    working_days,
    approved_ot_hours,
):
    """Fallback OT Amount = (Basic / Working Days / 12) * Approved OT Hours."""
    basic = money(basic_salary)
    ot_hours = money(approved_ot_hours)

    if (
        basic <= 0
        or ot_hours <= 0
    ):
        return Decimal("0.00")

    divisor = money(working_days)

    if divisor <= 0:
        return Decimal("0.00")

    return (
        basic
        / divisor
        / Decimal(12)
        * ot_hours
    ).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP,
    )


def compute_lop_deduction(
    monthly_earnings,
    lop_days,
    divisor,
):
    """Per-day loss of pay = monthly earnings / LOP divisor.

    ``monthly_earnings`` is the pay treated as pro-ratable (basic plus
    allowances; bonus and OT are excluded).
    """
    earnings = money(monthly_earnings)
    days = money(lop_days)

    if (
        earnings <= 0
        or days <= 0
    ):
        return Decimal("0.00")

    divisor = money(divisor)

    if divisor <= 0:
        return Decimal("0.00")

    return (
        earnings
        / divisor
        * days
    ).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP,
    )


def _leave_stats(company, year, month):
    """Return approved paid/unpaid leave days per employee for the month."""
    start = date(year, month, 1)

    end = date(
        year,
        month,
        monthrange(year, month)[1],
    )

    requests = (
        LeaveRequest.objects
        .select_related("leave_type")
        .filter(
            employee__company=company,
            status=LeaveRequest.Status.APPROVED,
            start_date__lte=end,
            end_date__gte=start,
        )
    )

    stats = {
        "paid_leave_days": Decimal("0.00"),
        "unpaid_leave_days": Decimal("0.00"),
    }

    result = {}

    for request in requests:
        overlap_start = max(
            request.start_date,
            start,
        )

        overlap_end = min(
            request.end_date,
            end,
        )

        days = (
            overlap_end - overlap_start
        ).days + 1

        employee_id = request.employee_id

        entry = result.setdefault(
            employee_id,
            dict(stats),
        )

        key = (
            "paid_leave_days"
            if request.leave_type.is_paid
            else "unpaid_leave_days"
        )

        entry[key] += Decimal(
            str(max(days, 0))
        )

    return {
        employee_id: {
            key: money(value)
            for key, value in entry.items()
        }
        for employee_id, entry in result.items()
    }


def monthly_attendance_stats(
    company,
    year,
    month
):
    """Return attendance aggregates per employee for the month.

    ``present_days`` counts PRESENT plus half of every HALF_DAY.
    PRESENT on a Sunday (week off worked) does NOT count as a present
    day, but its OT hours are still included in ``ot_hours``.
    ``absent_days`` counts ABSENT plus half of every HALF_DAY.
    ``leave_days`` counts ON_LEAVE records.
    ``half_days``, ``holidays`` and ``week_offs`` count their statuses.
    ``calendar_days`` is the total days in the month.
    ``ot_hours`` sums approved OT hours.
    Paid/unpaid leave comes from approved leave requests.
    """
    start = date(year, month, 1)

    end = date(
        year,
        month,
        monthrange(year, month)[1],
    )

    records = (
        Attendance.objects
        .filter(
            employee__company=company,
            date__range=(start, end),
        )
        .values(
            "employee_id",
            "date",
            "status",
            "approved_ot_hours",
        )
    )

    stats = {}

    for record in records:
        employee_id = record["employee_id"]

        entry = stats.setdefault(
            employee_id,
            {
                "present_days": Decimal("0.00"),
                "absent_days": Decimal("0.00"),
                "leave_days": Decimal("0.00"),
                "half_days": Decimal("0.00"),
                "holidays": Decimal("0.00"),
                "week_offs": Decimal("0.00"),
                "ot_hours": Decimal("0.00"),
            },
        )

        status = record["status"]

        if status == Attendance.Status.PRESENT:
            is_sunday = (
                record["date"].weekday() == 6
            )

            if not is_sunday:
                entry["present_days"] += Decimal("1")
        elif status == Attendance.Status.ABSENT:
            entry["absent_days"] += Decimal("1")
        elif status == Attendance.Status.ON_LEAVE:
            entry["leave_days"] += Decimal("1")
        elif status == Attendance.Status.HALF_DAY:
            entry["present_days"] += Decimal("0.5")
            entry["absent_days"] += Decimal("0.5")
            entry["half_days"] += Decimal("1")
        elif status == Attendance.Status.HOLIDAY:
            entry["holidays"] += Decimal("1")
        elif status == Attendance.Status.WEEK_OFF:
            entry["week_offs"] += Decimal("1")

        entry["ot_hours"] += (
            Decimal(
                str(record["approved_ot_hours"] or 0)
            )
        )

    leave_stats = _leave_stats(
        company,
        year,
        month,
    )

    calendar_days = monthrange(
        year,
        month,
    )[1]

    for employee_id, entry in stats.items():
        leave = leave_stats.get(
            employee_id,
            {
                "paid_leave_days": Decimal("0.00"),
                "unpaid_leave_days": Decimal("0.00"),
            },
        )

        entry["paid_leave_days"] = leave[
            "paid_leave_days"
        ]
        entry["unpaid_leave_days"] = leave[
            "unpaid_leave_days"
        ]

    for employee_id, leave in leave_stats.items():
        if employee_id not in stats:
            entry = leave.copy()

            entry.update(
                {
                    "present_days": Decimal("0.00"),
                    "absent_days": Decimal("0.00"),
                    "leave_days": Decimal("0.00"),
                    "half_days": Decimal("0.00"),
                    "holidays": Decimal("0.00"),
                    "week_offs": Decimal("0.00"),
                    "ot_hours": Decimal("0.00"),
                }
            )

            stats[employee_id] = entry

    return {
        employee_id: {
            key: money(value)
            for key, value in entry.items()
        }
        for employee_id, entry in stats.items()
    }


def _bonus_eligible(employee, stats):
    """Award bonus only in eligible departments to non-excluded
    employees with full attendance (no absence, leave or half day)."""
    department = (
        employee.department.name
        if employee.department_id
        else ""
    )

    if department.lower().strip() not in BONUS_DEPARTMENTS:
        return False

    full_name = (
        f"{employee.first_name} "
        f"{employee.last_name}"
    ).strip().casefold()

    if (
        full_name in BONUS_EXCLUDED_NAMES
        or employee.last_name.casefold() in BONUS_EXCLUDED_NAMES
        or employee.first_name.casefold() in BONUS_EXCLUDED_NAMES
    ):
        return False

    return (
        money(stats["absent_days"]) == 0
        and money(stats["leave_days"]) == 0
        and money(stats["half_days"]) == 0
    )


def _default_stats():
    return {
        "present_days": Decimal("0.00"),
        "absent_days": Decimal("0.00"),
        "leave_days": Decimal("0.00"),
        "paid_leave_days": Decimal("0.00"),
        "unpaid_leave_days": Decimal("0.00"),
        "half_days": Decimal("0.00"),
        "holidays": Decimal("0.00"),
        "week_offs": Decimal("0.00"),
        "ot_hours": Decimal("0.00"),
    }


def _snapshot_from_salary(salary):
    """Build a snapshot dict of the salary structure fields."""
    return {
        "basic_salary": money(salary.basic_salary),
        "bonus": money(salary.bonus),
        "dearness_allowance": money(salary.dearness_allowance),
        "conveyance_allowance": money(salary.conveyance_allowance),
        "medical_allowance": money(salary.medical_allowance),
        "special_allowance": money(salary.special_allowance),
        "other_allowance": money(salary.other_allowance),
        "pf": money(salary.pf),
        "esi": money(salary.esi),
        "professional_tax": money(salary.professional_tax),
        "tds": money(salary.tds),
        "other_deduction": (
            money(salary.other_deduction)
            + money(salary.deductions)
        ),
    }


def calculate_payroll_run(payroll_run):
    """Compute payslips for a payroll run and transition it to CALCULATED.

    Payslips are snapshotted at calculation time; recalculation updates
    snapshots in place (no data is deleted for active salaries).
    """
    from .models import EmployeeSalary, PayrollRun, Payslip

    working_days = get_working_days(payroll_run)

    ot_rate = get_ot_rate(payroll_run.company)

    bonus_amount = money(
        get_setting(
            payroll_run.company,
            "payroll",
            "bonus_amount",
            DEFAULT_BONUS_AMOUNT,
        )
    )

    lop_divisor = get_lop_divisor(payroll_run.company)

    calendar_days = monthrange(
        payroll_run.year,
        payroll_run.month,
    )[1]

    stats = monthly_attendance_stats(
        payroll_run.company,
        payroll_run.year,
        payroll_run.month,
    )

    salaries = (
        EmployeeSalary.objects
        .select_related("employee")
        .filter(
            employee__company=payroll_run.company,
            is_active=True,
        )
        .order_by("-effective_from")
    )

    seen_employees = set()

    unique_salaries = []

    for salary in salaries:
        if salary.employee_id in seen_employees:
            continue

        seen_employees.add(
            salary.employee_id
        )

        unique_salaries.append(
            salary
        )

    count = 0
    active_employee_ids = set()

    for salary in unique_salaries:
        active_employee_ids.add(
            salary.employee_id
        )

        snapshot = _snapshot_from_salary(salary)

        basic = snapshot["basic_salary"]

        employee_stats = stats.get(
            salary.employee_id,
            _default_stats(),
        )

        bonus = (
            bonus_amount
            if _bonus_eligible(
                salary.employee,
                employee_stats,
            )
            else Decimal("0.00")
        )

        snapshot["bonus"] = bonus

        present = money(employee_stats["present_days"])

        total_monthly = (
            basic
            + money(snapshot["dearness_allowance"])
        )

        per_day = (
            total_monthly / working_days
            if working_days > 0
            else Decimal("0.00")
        )

        earned = (per_day * present).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )

        gross = earned + bonus

        ot_hours = money(
            employee_stats["ot_hours"]
        )

        ot_per_hour = (
            (total_monthly / working_days / Decimal("8"))
            if working_days > 0
            else Decimal("0.00")
        )

        if ot_rate > 0:
            overtime_amount = (
                ot_rate * ot_hours
            ).quantize(
                TWO_PLACES,
                rounding=ROUND_HALF_UP,
            )

            applied_ot_rate = ot_rate

        else:
            overtime_amount = (
                (ot_per_hour * ot_hours)
                .quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
            )

            applied_ot_rate = Decimal("0.00")

        lop_days = money(
            employee_stats["unpaid_leave_days"]
        ) + money(
            employee_stats["absent_days"]
        )

        lop_deduction = compute_lop_deduction(
            earned,
            lop_days,
            lop_divisor,
        )

        fixed_deductions = [
            snapshot["pf"],
            snapshot["esi"],
            snapshot["professional_tax"],
            snapshot["tds"],
            snapshot["other_deduction"],
        ]

        deductions = (
            sum(fixed_deductions)
            + lop_deduction
        )

        net_salary = (
            gross
            + overtime_amount
            - deductions
        )

        defaults = dict(
            snapshot,
            working_days=working_days,
            calendar_days=calendar_days,
            present_days=present,
            no_of_days=present,
            total_monthly=total_monthly,
            per_day_rate=per_day.quantize(TWO_PLACES),
            absent_days=money(employee_stats["absent_days"]),
            leave_days=money(employee_stats["leave_days"]),
            paid_leave_days=money(employee_stats["paid_leave_days"]),
            unpaid_leave_days=money(employee_stats["unpaid_leave_days"]),
            half_days=money(employee_stats["half_days"]),
            holidays=int(money(employee_stats["holidays"])),
            week_offs=int(money(employee_stats["week_offs"])),
            ot_hours=ot_hours,
            ot_rate=applied_ot_rate,
            lop_days=lop_days,
            lop_deduction=lop_deduction,
            gross_salary=gross,
            overtime_amount=overtime_amount,
            deductions=deductions,
            net_salary=net_salary,
        )

        Payslip.objects.update_or_create(
            payroll_run=payroll_run,
            employee=salary.employee,
            defaults=defaults,
        )

        count += 1

    Payslip.objects.filter(
        payroll_run=payroll_run,
    ).exclude(
        employee_id__in=active_employee_ids,
    ).delete()

    payroll_run.status = PayrollRun.Status.CALCULATED

    payroll_run.working_days = working_days

    payroll_run.save(
        update_fields=[
            "status",
            "working_days",
        ]
    )

    return count
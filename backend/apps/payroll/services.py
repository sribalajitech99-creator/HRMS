from calendar import monthrange
from datetime import date
from decimal import (
    Decimal,
    DecimalException,
    ROUND_HALF_UP,
)

from apps.attendance.models import Attendance
from apps.companies.models import CompanySetting


DEFAULT_WORKING_DAYS = Decimal("26.00")

TWO_PLACES = Decimal("0.01")


def money(value):
    return Decimal(str(value or 0)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP,
    )


def get_working_days(payroll_run):
    """Return the working-days value for a payroll run.

    The value comes from the company settings key ``payroll.working_days``
    (defaulting to 26). HR can configure it per company.

    BUSINESS RULE TO CONFIRM: the fraction of the month treated as payable
    working days. The OT formula below divides by this value.
    """
    try:
        setting = (
            CompanySetting.objects
            .get(
                company=payroll_run.company,
                group="payroll",
                key="working_days",
            )
        )

        value = Decimal(
            str(setting.value or "")
        )

        if value > 0:
            return value

    except (
        CompanySetting.DoesNotExist,
        DecimalException,
    ):
        pass

    if payroll_run.working_days and payroll_run.working_days > 0:
        return money(payroll_run.working_days)

    return DEFAULT_WORKING_DAYS


def monthly_attendance_stats(
    company,
    year,
    month
):
    """Return attendance aggregates per employee for the month.

    present_days counts PRESENT plus half of every HALF_DAY.
    absent_days counts ABSENT plus half of every HALF_DAY.
    leave_days counts ON_LEAVE records.
    ot_hours sums approved OT hours.
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
        .values("employee_id", "status", "approved_ot_hours")
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
                "ot_hours": Decimal("0.00"),
            },
        )

        status = record["status"]

        if status == Attendance.Status.PRESENT:
            entry["present_days"] += Decimal("1")
        elif status == Attendance.Status.ABSENT:
            entry["absent_days"] += Decimal("1")
        elif status == Attendance.Status.ON_LEAVE:
            entry["leave_days"] += Decimal("1")
        elif status == Attendance.Status.HALF_DAY:
            entry["present_days"] += Decimal("0.5")
            entry["absent_days"] += Decimal("0.5")

        entry["ot_hours"] += (
            Decimal(
                str(record["approved_ot_hours"] or 0)
            )
        )

    return {
        employee_id: {
            key: money(value)
            for key, value in entry.items()
        }
        for employee_id, entry in stats.items()
    }


def compute_overtime_amount(
    basic_salary,
    working_days,
    approved_ot_hours,
):
    """OT Amount = (Basic Salary / Working Days / 12) * Approved OT Hours.

    BUSINESS RULE TO CONFIRM: the working-days divisor (default 26) and the
    /12 (monthly pro-rating) were provided as confirmed requirements.
    """
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

    per_day = (
        basic
        / divisor
        / Decimal(12)
    )

    return (
        per_day
        * ot_hours
    ).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP,
    )


def calculate_payroll_run(payroll_run):
    """Compute payslips for a payroll run and transition it to CALCULATED."""
    from .models import PayrollRun, Payslip

    Payslip.objects.filter(
        payroll_run=payroll_run
    ).delete()

    working_days = get_working_days(payroll_run)

    stats = monthly_attendance_stats(
        payroll_run.company,
        payroll_run.year,
        payroll_run.month,
    )

    from .models import EmployeeSalary

    salaries = (
        EmployeeSalary.objects
        .select_related("employee")
        .filter(
            employee__company=payroll_run.company,
            is_active=True,
        )
    )

    count = 0

    for salary in salaries:
        basic = money(salary.basic_salary)
        hra = money(salary.hra)
        allowance = money(salary.allowance)
        deductions = money(salary.deductions)

        gross = basic + hra + allowance

        employee_stats = stats.get(
            salary.employee_id,
            {
                "present_days": Decimal("0.00"),
                "absent_days": Decimal("0.00"),
                "leave_days": Decimal("0.00"),
                "ot_hours": Decimal("0.00"),
            },
        )

        ot_hours = money(
            employee_stats["ot_hours"]
        )

        overtime_amount = compute_overtime_amount(
            basic,
            working_days,
            ot_hours,
        )

        net_salary = (
            gross
            + overtime_amount
            - deductions
        )

        Payslip.objects.create(
            payroll_run=payroll_run,
            employee=salary.employee,
            basic_salary=basic,
            hra=hra,
            allowance=allowance,
            working_days=working_days,
            present_days=money(
                employee_stats["present_days"]
            ),
            absent_days=money(
                employee_stats["absent_days"]
            ),
            leave_days=money(
                employee_stats["leave_days"]
            ),
            ot_hours=ot_hours,
            gross_salary=gross,
            overtime_amount=overtime_amount,
            deductions=deductions,
            net_salary=net_salary,
        )

        count += 1

    payroll_run.status = PayrollRun.Status.CALCULATED

    payroll_run.save(
        update_fields=[
            "status",
            "working_days",
        ]
    )

    return count
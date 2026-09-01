from calendar import monthrange
from datetime import date

from django.db.models import Count, Q, Sum

from apps.attendance.models import Attendance
from apps.companies.models import Company
from apps.employees.models import Employee
from apps.leave_management.models import LeaveRequest, LeaveType
from apps.payroll.models import Payslip
from apps.payroll.services import (
    compute_overtime_amount,
    get_working_days,
    money,
)
from apps.recruitment.models import Candidate, JobOpening


FULL_ACCESS_ROLES = {"SUPER_ADMIN"}


def int_param(params, name, default=None):
    value = params.get(name)

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def date_param(params, name, default=None):
    value = params.get(name)

    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return default


def _fmt_name(employee):
    return (
        f"{employee.first_name} {employee.last_name}"
    ).strip()


def _money_str(value):
    return str(
        money(value)
        if value is not None
        else "0.00"
    )


def _company_qs(user, model=None):
    from apps.accounts.permissions import visible_company_ids

    ids = visible_company_ids(user)

    if ids is None:
        return Company.objects.filter(is_active=True)

    return Company.objects.filter(
        id__in=ids,
        is_active=True,
    )


def employee_master(params, user):
    qs = (
        Employee.objects
        .select_related(
            "company",
            "department",
            "designation",
        )
    )

    company_id = int_param(params, "company")
    department_id = int_param(params, "department")
    designation_id = int_param(params, "designation")
    status = params.get("status")
    search = params.get("search")

    if company_id:
        qs = qs.filter(company_id=company_id)
    if department_id:
        qs = qs.filter(department_id=department_id)
    if designation_id:
        qs = qs.filter(designation_id=designation_id)
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(
            employee_code__icontains=search
        )

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    rows = []

    for emp in qs.order_by("employee_code"):
        rows.append([
            emp.employee_code,
            _fmt_name(emp),
            emp.company.name if emp.company else "",
            emp.department.name if emp.department else "",
            emp.designation.name if emp.designation else "",
            emp.mobile,
            emp.work_email,
            emp.joining_date,
            emp.get_status_display(),
            emp.employment_type,
        ])

    return {
        "title": "Employee Master Report",
        "period": "All employees",
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Department",
            "Designation",
            "Mobile",
            "Work Email",
            "Joining Date",
            "Status",
            "Employment Type",
        ],
        "rows": rows,
        "totals": {"records": len(rows)},
    }


def employee_company_wise(params, user):
    qs = Employee.objects.filter(
        company__in=_company_qs(user),
    )

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    data = (
        qs.values(
            "company__code",
            "company__name",
        )
        .annotate(
            total=Count("id"),
            active=Count(
                "id",
                filter=Q(
                    status="ACTIVE"
                ),
            ),
            exited=Count(
                "id",
                filter=Q(
                    status="EXITED"
                ),
            ),
        )
        .order_by("company__code")
    )

    rows = [
        [
            item["company__code"],
            item["company__name"],
            item["total"],
            item["active"],
            item["exited"],
        ]
        for item in data
    ]

    return {
        "title": "Company-wise Employees",
        "period": "Current",
        "columns": [
            "Company Code",
            "Company",
            "Total",
            "Active",
            "Exited",
        ],
        "rows": rows,
        "totals": {
            "total": sum(r[2] for r in rows),
        },
    }


def employee_department_wise(params, user):
    qs = Employee.objects.filter(
        company__in=_company_qs(user),
    )

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    data = (
        qs.values(
            "company__code",
            "department__name",
        )
        .annotate(total=Count("id"))
        .order_by("company__code", "department__name")
    )

    rows = [
        [
            item["company__code"],
            item["department__name"] or "Unassigned",
            item["total"],
        ]
        for item in data
    ]

    return {
        "title": "Department-wise Employees",
        "period": "Current",
        "columns": [
            "Company",
            "Department",
            "Employees",
        ],
        "rows": rows,
        "totals": {"employees": sum(r[2] for r in rows)},
    }


def employee_designation_wise(params, user):
    qs = Employee.objects.filter(
        company__in=_company_qs(user),
    )

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    data = (
        qs.values(
            "company__code",
            "designation__name",
        )
        .annotate(total=Count("id"))
        .order_by("company__code", "designation__name")
    )

    rows = [
        [
            item["company__code"],
            item["designation__name"] or "Unassigned",
            item["total"],
        ]
        for item in data
    ]

    return {
        "title": "Designation-wise Employees",
        "period": "Current",
        "columns": [
            "Company",
            "Designation",
            "Employees",
        ],
        "rows": rows,
        "totals": {"employees": sum(r[2] for r in rows)},
    }


def _employee_by_status(params, user, label):
    qs = Employee.objects.filter(
        company__in=_company_qs(user),
    )

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    if label == "ACTIVE":
        qs = qs.filter(status="ACTIVE")
    elif label == "INACTIVE":
        qs = qs.filter(status="INACTIVE")
    elif label == "EXITED":
        qs = qs.filter(status="EXITED")

    rows = [
        [
            emp.employee_code,
            _fmt_name(emp),
            emp.company.name if emp.company else "",
            emp.department.name if emp.department else "",
            emp.joining_date,
            emp.get_status_display(),
        ]
        for emp in qs.select_related("company", "department")
        .order_by("employee_code")
    ]

    title = {
        "ACTIVE": "Active Employees",
        "INACTIVE": "Inactive Employees",
        "EXITED": "Exited Employees",
    }[label]

    return {
        "title": title,
        "period": "Current",
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Department",
            "Joining Date",
            "Status",
        ],
        "rows": rows,
        "totals": {"records": len(rows)},
    }


def attendance_daily(params, user):
    day = date_param(params, "date", date.today())

    qs = Attendance.objects.select_related(
        "employee",
        "employee__company",
        "employee__department",
        "shift",
        "holiday",
    ).filter(date=day)

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    department_id = int_param(params, "department")

    if department_id:
        qs = qs.filter(employee__department_id=department_id)

    rows = [
        [
            rec.employee.employee_code,
            _fmt_name(rec.employee),
            rec.employee.company.code,
            rec.employee.department.name if rec.employee.department else "",
            rec.get_status_display(),
            rec.shift.name if rec.shift else "",
            (
                rec.check_in_time.strftime("%H:%M")
                if rec.check_in_time
                else ""
            ),
            (
                rec.check_out_time.strftime("%H:%M")
                if rec.check_out_time
                else ""
            ),
            _money_str(rec.working_hours),
            _money_str(rec.approved_ot_hours),
            rec.remarks,
        ]
        for rec in qs.order_by("employee__employee_code")
    ]

    return {
        "title": "Daily Attendance Report",
        "period": day.strftime("%d %b %Y"),
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Department",
            "Status",
            "Shift",
            "Check In",
            "Check Out",
            "Working Hours",
            "Approved OT",
            "Remarks",
        ],
        "rows": rows,
        "totals": {
            "present": sum(
                1 for r in rows if r[4] == "Present"
            ),
            "total": len(rows),
        },
    }


def _month_dates(year, month):
    last = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last)


def attendance_monthly_register(params, user):
    year = int_param(params, "year", date.today().year)
    month = int_param(params, "month", date.today().month)

    start, end = _month_dates(year, month)

    employees = Employee.objects.filter(
        company__in=_company_qs(user),
    )

    company_id = int_param(params, "company")

    if company_id:
        employees = employees.filter(company_id=company_id)

    department_id = int_param(params, "department")

    if department_id:
        employees = employees.filter(department_id=department_id)

    employee_id = int_param(params, "employee")

    if employee_id:
        employees = employees.filter(pk=employee_id)

    records = (
        Attendance.objects
        .filter(
            date__range=(start, end),
        )
        .select_related("employee", "shift")
    )

    ids = visible_company_ids(user)

    if ids is not None:
        records = records.filter(company_id__in=ids)

    if company_id:
        records = records.filter(company_id=company_id)
    if department_id:
        records = records.filter(employee__department_id=department_id)
    if employee_id:
        records = records.filter(employee_id=employee_id)

    by_employee = {}

    for rec in records:
        by_employee.setdefault(
            rec.employee_id,
            {},
        )[rec.date.day] = rec

    codes = {
        "PRESENT": "P",
        "ABSENT": "A",
        "ON_LEAVE": "L",
        "HALF_DAY": "HD",
        "HOLIDAY": "H",
        "WEEK_OFF": "W",
    }

    day_columns = []

    for day in range(1, monthrange(year, month)[1] + 1):
        day_columns.append(str(day))

    columns = (
        ["Code", "Name", "Company", "Department"]
        + day_columns
        + ["Present", "OT Hrs"]
    )

    rows = []

    for emp in employees.order_by("employee_code"):
        days = by_employee.get(emp.id, {})

        day_values = []

        present = 0

        ot = 0.0

        for day in range(1, monthrange(year, month)[1] + 1):
            rec = days.get(day)

            if not rec:
                day_values.append("")
                continue

            day_values.append(
                codes.get(rec.status, "?")
            )

            if rec.status in ("PRESENT", "HALF_DAY"):
                present += 1

            ot += float(rec.approved_ot_hours or 0)

        rows.append(
            [
                emp.employee_code,
                _fmt_name(emp),
                emp.company.code,
                emp.department.name if emp.department else "",
            ]
            + day_values
            + [
                present,
                round(ot, 2),
            ]
        )

    return {
        "title": "Monthly Attendance Register",
        "period": f"{month:02d}-{year}",
        "columns": columns,
        "rows": rows,
        "totals": {"employees": len(rows)},
    }


def attendance_employee_history(params, user):
    employee_id = int_param(params, "employee")

    if not employee_id:
        return None

    start = date_param(
        params,
        "from_date",
        date.today().replace(day=1),
    )

    end = date_param(
        params,
        "to_date",
        date.today(),
    )

    qs = Attendance.objects.filter(
        employee_id=employee_id,
        date__range=(start, end),
    ).select_related("shift", "holiday")

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    rows = [
        [
            rec.date,
            rec.get_status_display(),
            rec.shift.name if rec.shift else "",
            (
                rec.check_in_time.strftime("%H:%M")
                if rec.check_in_time
                else ""
            ),
            (
                rec.check_out_time.strftime("%H:%M")
                if rec.check_out_time
                else ""
            ),
            _money_str(rec.working_hours),
            _money_str(rec.calculated_ot_hours),
            _money_str(rec.approved_ot_hours),
            rec.remarks,
        ]
        for rec in qs.order_by("date")
    ]

    return {
        "title": "Employee Attendance History",
        "period": f"{start} to {end}",
        "columns": [
            "Date",
            "Status",
            "Shift",
            "Check In",
            "Check Out",
            "Working Hours",
            "Calculated OT",
            "Approved OT",
            "Remarks",
        ],
        "rows": rows,
        "totals": {"records": len(rows)},
    }


def attendance_by_status(params, user, label):
    year = int_param(params, "year", date.today().year)
    month = int_param(params, "month", date.today().month)

    start, end = _month_dates(year, month)

    status_map = {
        "present": Attendance.Status.PRESENT,
        "absent": Attendance.Status.ABSENT,
        "leave": Attendance.Status.ON_LEAVE,
        "half_day": Attendance.Status.HALF_DAY,
    }

    status = status_map.get(label)

    qs = (
        Attendance.objects
        .filter(
            date__range=(start, end),
        )
        .select_related("employee", "employee__company", "shift")
    )

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    if status:
        qs = qs.filter(status=status)

    rows = [
        [
            rec.date,
            rec.employee.employee_code,
            _fmt_name(rec.employee),
            rec.employee.company.code,
            rec.get_status_display(),
            rec.shift.name if rec.shift else "",
        ]
        for rec in qs.order_by("date", "employee__employee_code")
    ]

    title = {
        "present": "Present Report",
        "absent": "Absent Report",
        "leave": "Leave Report",
        "half_day": "Half-Day Report",
    }[label]

    return {
        "title": title,
        "period": f"{month:02d}-{year}",
        "columns": [
            "Date",
            "Employee Code",
            "Name",
            "Company",
            "Status",
            "Shift",
        ],
        "rows": rows,
        "totals": {"records": len(rows)},
    }


def _special_working(params, user, field):
    year = int_param(params, "year", date.today().year)
    month = int_param(params, "month", date.today().month)

    start, end = _month_dates(year, month)

    qs = (
        Attendance.objects
        .filter(
            date__range=(start, end),
            **{field: True},
        )
        .select_related("employee", "employee__company", "holiday", "shift")
    )

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    rows = [
        [
            rec.date,
            rec.employee.employee_code,
            _fmt_name(rec.employee),
            rec.employee.company.code,
            rec.holiday.name if rec.holiday else "Week Off",
            _money_str(rec.working_hours),
            _money_str(rec.approved_ot_hours),
        ]
        for rec in qs.order_by("date", "employee__employee_code")
    ]

    is_holiday = field == "worked_on_holiday"

    return {
        "title": (
            "Holiday Working Report"
            if is_holiday
            else "Week-Off Working Report"
        ),
        "period": f"{month:02d}-{year}",
        "columns": [
            "Date",
            "Employee Code",
            "Name",
            "Company",
            "Working For",
            "Working Hours",
            "Approved OT",
        ],
        "rows": rows,
        "totals": {"records": len(rows)},
    }


def attendance_shift_wise(params, user):
    year = int_param(params, "year", date.today().year)
    month = int_param(params, "month", date.today().month)

    start, end = _month_dates(year, month)

    qs = Attendance.objects.filter(
        date__range=(start, end),
    )

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    data = (
        qs.values(
            "company__code",
            "shift__name",
        )
        .annotate(
            total=Count("id"),
            present=Count(
                "id",
                filter=Q(status="PRESENT"),
            ),
        )
        .order_by("company__code", "shift__name")
    )

    rows = [
        [
            item["company__code"],
            item["shift__name"] or "No Shift",
            item["present"],
            item["total"],
        ]
        for item in data
    ]

    return {
        "title": "Shift-wise Attendance",
        "period": f"{month:02d}-{year}",
        "columns": [
            "Company",
            "Shift",
            "Present",
            "Records",
        ],
        "rows": rows,
        "totals": {"records": sum(r[3] for r in rows)},
    }


def attendance_working_hours(params, user):
    year = int_param(params, "year", date.today().year)
    month = int_param(params, "month", date.today().month)

    start, end = _month_dates(year, month)

    qs = Attendance.objects.filter(
        date__range=(start, end),
    )

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    department_id = int_param(params, "department")

    if department_id:
        qs = qs.filter(employee__department_id=department_id)

    data = (
        qs.values(
            "employee_id",
            "employee__employee_code",
            "employee__first_name",
            "employee__last_name",
            "employee__company__code",
        )
        .annotate(
            working_hours=Sum("working_hours"),
            ot_hours=Sum("approved_ot_hours"),
        )
        .order_by("employee__employee_code")
    )

    rows = [
        [
            item["employee__employee_code"],
            (
                f"{item['employee__first_name']} "
                f"{item['employee__last_name']}"
            ).strip(),
            item["employee__company__code"],
            _money_str(item["working_hours"]),
            _money_str(item["ot_hours"]),
        ]
        for item in data
    ]

    return {
        "title": "Working Hours Report",
        "period": f"{month:02d}-{year}",
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Working Hours",
            "Approved OT Hours",
        ],
        "rows": rows,
        "totals": {"employees": len(rows)},
    }


def ot_daily(params, user):
    day = date_param(params, "date", date.today())

    qs = Attendance.objects.filter(
        date=day,
    ).select_related("employee", "employee__company", "shift")

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    department_id = int_param(params, "department")

    if department_id:
        qs = qs.filter(employee__department_id=department_id)

    rows = [
        [
            rec.employee.employee_code,
            _fmt_name(rec.employee),
            rec.employee.company.code,
            rec.employee.department.name if rec.employee.department else "",
            rec.shift.name if rec.shift else "",
            rec.get_status_display(),
            _money_str(rec.working_hours),
            _money_str(rec.calculated_ot_hours),
            _money_str(rec.approved_ot_hours),
        ]
        for rec in qs.order_by("employee__employee_code")
    ]

    return {
        "title": "Daily OT Report",
        "period": day.strftime("%d %b %Y"),
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Department",
            "Shift",
            "Status",
            "Working Hours",
            "Calculated OT",
            "Approved OT",
        ],
        "rows": rows,
        "totals": {"records": len(rows)},
    }


def _base_ot_attendance(params, user):
    year = int_param(params, "year", date.today().year)
    month = int_param(params, "month", date.today().month)

    start, end = _month_dates(year, month)

    qs = Attendance.objects.filter(
        date__range=(start, end),
    )

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    department_id = int_param(params, "department")

    if department_id:
        qs = qs.filter(employee__department_id=department_id)

    employee_id = int_param(params, "employee")

    if employee_id:
        qs = qs.filter(employee_id=employee_id)

    data = (
        qs.values(
            "employee_id",
            "employee__employee_code",
            "employee__first_name",
            "employee__last_name",
            "employee__company__code",
            "employee__company__name",
            "employee__department__name",
        )
        .annotate(
            calc_ot=Sum("calculated_ot_hours"),
            appr_ot=Sum("approved_ot_hours"),
        )
        .order_by("employee__employee_code")
    )

    return (
        list(data),
        f"{month:02d}-{year}",
    )


def ot_monthly(params, user):
    data, period = _base_ot_attendance(params, user)

    rows = [
        [
            item["employee__employee_code"],
            (
                f"{item['employee__first_name']} "
                f"{item['employee__last_name']}"
            ).strip(),
            item["employee__company__code"],
            item["employee__department__name"] or "",
            _money_str(item["calc_ot"]),
            _money_str(item["appr_ot"]),
        ]
        for item in data
    ]

    return {
        "title": "Monthly OT Report",
        "period": period,
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Department",
            "Calculated OT",
            "Approved OT",
        ],
        "rows": rows,
        "totals": {"employees": len(rows)},
    }


def ot_salary(params, user):
    """OT salary using confirmed formula.

    OT Amount = (Basic Salary / Working Days / 12) x Approved OT Hours
    """
    year = int_param(params, "year", date.today().year)
    month = int_param(params, "month", date.today().month)

    company_id = int_param(params, "company")

    data, period = _base_ot_attendance(params, user)

    ot_map = {item["employee_id"]: item for item in data}

    from apps.payroll.models import EmployeeSalary

    salaries = (
        EmployeeSalary.objects
        .select_related(
            "employee",
            "employee__company",
        )
        .filter(
            is_active=True,
        )
    )

    ids = visible_company_ids(user)

    if ids is not None:
        salaries = salaries.filter(
            employee__company_id__in=ids
        )

    if company_id:
        salaries = salaries.filter(
            employee__company_id=company_id
        )

    working_days_override = None

    if company_id:
        run = (
            PayrollRun.objects
            .filter(
                company_id=company_id,
                year=year,
                month=month,
            )
            .first()
        )

    rows = []

    for salary in salaries:
        employee_id = salary.employee_id

        ot_item = ot_map.get(employee_id, {})

        ot_hours = money(ot_item.get("appr_ot") or 0)

        working_days = (
            working_days_override
        )

        basic = money(salary.basic_salary)

        if working_days is None:
            if run:
                working_days = run.working_days
            else:
                working_days = None

        ot_amount = compute_overtime_amount(
            basic,
            working_days or 26.0,
            ot_hours,
        )

        rows.append([
            salary.employee.employee_code,
            _fmt_name(salary.employee),
            salary.employee.company.code,
            salary.employee.department.name if salary.employee.department else "",
            _money_str(basic),
            _money_str(ot_hours),
            _money_str(ot_amount),
        ])

    return {
        "title": "OT Salary Report",
        "period": period,
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Department",
            "Basic Salary",
            "Approved OT Hours",
            "OT Amount",
        ],
        "rows": rows,
        "totals": {"employees": len(rows)},
    }


def _payslip_qs(params, user):
    year = int_param(params, "year", date.today().year)
    month = int_param(params, "month", date.today().month)

    qs = Payslip.objects.filter(
        payroll_run__year=year,
        payroll_run__month=month,
    )

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(employee__company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(payroll_run__company_id=company_id)

    department_id = int_param(params, "department")

    if department_id:
        qs = qs.filter(employee__department_id=department_id)

    employee_id = int_param(params, "employee")

    if employee_id:
        qs = qs.filter(employee_id=employee_id)

    return qs, f"{month:02d}-{year}"


def payroll_monthly_salary_register(params, user):
    qs, period = _payslip_qs(params, user)

    rows = [
        [
            slip.employee.employee_code,
            _fmt_name(slip.employee),
            slip.payroll_run.company.code,
            slip.employee.department.name if slip.employee.department else "",
            _money_str(slip.basic_salary),
            _money_str(slip.hra),
            _money_str(slip.allowance),
            _money_str(slip.gross_salary),
            _money_str(slip.ot_hours),
            _money_str(slip.overtime_amount),
            _money_str(slip.deductions),
            _money_str(slip.net_salary),
        ]
        for slip in qs.select_related(
            "employee",
            "employee__department",
            "payroll_run",
            "payroll_run__company",
        ).order_by("employee__employee_code")
    ]

    return {
        "title": "Monthly Salary Register",
        "period": period,
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Department",
            "Basic",
            "HRA",
            "Allowance",
            "Gross",
            "OT Hours",
            "OT Amount",
            "Deductions",
            "Net Salary",
        ],
        "rows": rows,
        "totals": {
            "gross": _money_str(
                sum(float(r[7]) for r in rows)
            ),
            "net": _money_str(
                sum(float(r[11]) for r in rows)
            ),
        },
    }


def _payroll_aggregate(params, user, group_by):
    qs, period = _payslip_qs(params, user)

    if group_by == "company":
        values = [
            "payroll_run__company__code",
            "payroll_run__company__name",
        ]
    elif group_by == "department":
        values = [
            "employee__company__code",
            "employee__department__name",
        ]
    else:
        return None

    data = (
        qs.values(*values)
        .annotate(
            gross_sum=Sum("gross_salary"),
            ot_sum=Sum("overtime_amount"),
            deduction_sum=Sum("deductions"),
            net_sum=Sum("net_salary"),
        )
        .order_by(*values)
    )

    if group_by == "company":
        rows = [
            [
                item["payroll_run__company__code"],
                item["payroll_run__company__name"],
                _money_str(item["gross_sum"]),
                _money_str(item["ot_sum"]),
                _money_str(item["deduction_sum"]),
                _money_str(item["net_sum"]),
            ]
            for item in data
        ]

        columns = [
            "Company Code",
            "Company",
            "Gross",
            "OT Amount",
            "Deductions",
            "Net",
        ]
    else:
        rows = [
            [
                item["employee__company__code"],
                item["employee__department__name"] or "Unassigned",
                _money_str(item["gross_sum"]),
                _money_str(item["ot_sum"]),
                _money_str(item["deduction_sum"]),
                _money_str(item["net_sum"]),
            ]
            for item in data
        ]

        columns = [
            "Company",
            "Department",
            "Gross",
            "OT Amount",
            "Deductions",
            "Net",
        ]

    return {
        "title": (
            "Company Salary Register"
            if group_by == "company"
            else "Department Salary Register"
        ),
        "period": period,
        "columns": columns,
        "rows": rows,
        "totals": {
            "net": _money_str(
                sum(float(r[-1]) for r in rows)
            ),
        },
    }


def payroll_company_register(params, user):
    return _payroll_aggregate(params, user, "company")


def payroll_department_register(params, user):
    return _payroll_aggregate(params, user, "department")


def payroll_earnings(params, user):
    qs, period = _payslip_qs(params, user)

    rows = [
        [
            slip.employee.employee_code,
            _fmt_name(slip.employee),
            slip.payroll_run.company.code,
            _money_str(slip.basic_salary),
            _money_str(slip.hra),
            _money_str(slip.allowance),
            _money_str(slip.overtime_amount),
            _money_str(slip.gross_salary + slip.overtime_amount),
        ]
        for slip in qs.select_related(
            "employee", "payroll_run", "payroll_run__company"
        ).order_by("employee__employee_code")
    ]

    return {
        "title": "Earnings Report",
        "period": period,
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Basic",
            "HRA",
            "Allowance",
            "OT Amount",
            "Total Earnings",
        ],
        "rows": rows,
        "totals": {
            "earnings": _money_str(
                sum(float(r[7]) for r in rows)
            ),
        },
    }


def payroll_deductions(params, user):
    qs, period = _payslip_qs(params, user)

    rows = [
        [
            slip.employee.employee_code,
            _fmt_name(slip.employee),
            slip.payroll_run.company.code,
            _money_str(slip.deductions),
        ]
        for slip in qs.select_related(
            "employee", "payroll_run", "payroll_run__company"
        ).order_by("employee__employee_code")
    ]

    return {
        "title": "Deduction Report",
        "period": period,
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Deductions",
        ],
        "rows": rows,
        "totals": {
            "deductions": _money_str(
                sum(float(r[3]) for r in rows)
            ),
        },
    }


def payroll_net_salary(params, user):
    qs, period = _payslip_qs(params, user)

    rows = [
        [
            slip.employee.employee_code,
            _fmt_name(slip.employee),
            slip.payroll_run.company.code,
            slip.employee.company.name if slip.employee.company else "",
            _money_str(slip.gross_salary),
            _money_str(slip.overtime_amount),
            _money_str(slip.deductions),
            _money_str(slip.net_salary),
        ]
        for slip in qs.select_related(
            "employee",
            "employee__company",
            "payroll_run",
            "payroll_run__company",
        ).order_by("employee__employee_code")
    ]

    return {
        "title": "Net Salary Report",
        "period": period,
        "columns": [
            "Employee Code",
            "Name",
            "Company",
            "Company Name",
            "Gross",
            "OT Amount",
            "Deductions",
            "Net Salary",
        ],
        "rows": rows,
        "totals": {
            "net": _money_str(
                sum(float(r[7]) for r in rows)
            ),
        },
    }


def payroll_payslip_register(params, user):
    qs, period = _payslip_qs(params, user)

    rows = [
        [
            slip.id,
            slip.employee.employee_code,
            _fmt_name(slip.employee),
            slip.payroll_run.company.code,
            _money_str(slip.basic_salary),
            _money_str(slip.gross_salary),
            _money_str(slip.overtime_amount),
            _money_str(slip.deductions),
            _money_str(slip.net_salary),
            slip.payroll_run.get_status_display(),
        ]
        for slip in qs.select_related(
            "employee", "payroll_run", "payroll_run__company"
        ).order_by("employee__employee_code")
    ]

    return {
        "title": "Payslip Register",
        "period": period,
        "columns": [
            "Payslip #",
            "Employee Code",
            "Name",
            "Company",
            "Basic",
            "Gross",
            "OT Amount",
            "Deductions",
            "Net",
            "Payroll Status",
        ],
        "rows": rows,
        "totals": {"payslips": len(rows)},
    }


def leave_employee_history(params, user):
    employee_id = int_param(params, "employee")

    if not employee_id:
        return None

    qs = LeaveRequest.objects.filter(
        employee_id=employee_id,
    )

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    rows = [
        [
            lr.leave_type.name,
            lr.start_date,
            lr.end_date,
            lr.total_days,
            lr.get_status_display(),
            lr.reason,
        ]
        for lr in qs.select_related("leave_type").order_by("-start_date")
    ]

    return {
        "title": "Employee Leave History",
        "period": "All time",
        "columns": [
            "Leave Type",
            "Start",
            "End",
            "Days",
            "Status",
            "Reason",
        ],
        "rows": rows,
        "totals": {"requests": len(rows)},
    }


def leave_monthly(params, user):
    year = int_param(params, "year", date.today().year)
    month = int_param(params, "month", date.today().month)

    start, end = _month_dates(year, month)

    qs = LeaveRequest.objects.filter(
        start_date__lte=end,
        end_date__gte=start,
    )

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    rows = [
        [
            lr.employee.employee_code,
            _fmt_name(lr.employee),
            lr.leave_type.name,
            lr.start_date,
            lr.end_date,
            lr.total_days,
            lr.get_status_display(),
        ]
        for lr in qs.select_related(
            "employee",
            "leave_type",
        ).order_by("-start_date")
    ]

    return {
        "title": "Monthly Leave Report",
        "period": f"{month:02d}-{year}",
        "columns": [
            "Employee Code",
            "Name",
            "Leave Type",
            "Start",
            "End",
            "Days",
            "Status",
        ],
        "rows": rows,
        "totals": {"requests": len(rows)},
    }


def leave_balance(params, user):
    qs = Employee.objects.filter(
        company__in=_company_qs(user),
    )

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    employee_id = int_param(params, "employee")

    if employee_id:
        qs = qs.filter(pk=employee_id)

    rows = []

    approved = set(
        LeaveRequest.objects.filter(
            status=LeaveRequest.Status.APPROVED,
        ).values_list("employee_id", "leave_type_id")
    )

    for emp in qs.select_related("company").order_by("employee_code"):
        for lt in LeaveType.objects.filter(
            company=emp.company,
            is_active=True,
        ):
            allocated = lt.annual_allocation or 0

            usage = (
                LeaveRequest.objects
                .filter(
                    employee=emp,
                    leave_type=lt,
                    status=LeaveRequest.Status.APPROVED,
                )
                .values("total_days")
            )

            used = sum(
                float(item["total_days"] or 0)
                for item in usage
            )

            rows.append([
                emp.company.code,
                emp.employee_code,
                _fmt_name(emp),
                lt.name,
                _money_str(allocated),
                _money_str(used),
                _money_str(allocated - used),
            ])

    return {
        "title": "Leave Balance Report",
        "period": "Current",
        "columns": [
            "Company",
            "Employee Code",
            "Name",
            "Leave Type",
            "Allocated",
            "Used",
            "Balance",
        ],
        "rows": rows,
        "totals": {"rows": len(rows)},
    }


def leave_type_usage(params, user):
    qs = LeaveRequest.objects.all()

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    data = (
        qs.values(
            "company__code",
            "leave_type__name",
        )
        .annotate(total=Count("id"))
        .order_by("company__code", "leave_type__name")
    )

    rows = [
        [
            item["company__code"],
            item["leave_type__name"],
            item["total"],
        ]
        for item in data
    ]

    return {
        "title": "Leave Type Report",
        "period": "All time",
        "columns": [
            "Company",
            "Leave Type",
            "Requests",
        ],
        "rows": rows,
        "totals": {"requests": sum(r[2] for r in rows)},
    }


def holiday_calendar(params, user):
    year = int_param(params, "year", date.today().year)

    from apps.attendance.models import Holiday

    qs = Holiday.objects.filter(
        date__year=year,
        is_active=True,
    )

    ids = visible_company_ids(user)

    if ids is not None:
        qs = qs.filter(company_id__in=ids)

    company_id = int_param(params, "company")

    if company_id:
        qs = qs.filter(company_id=company_id)

    rows = [
        [
            h.company.code,
            h.date,
            h.name,
            h.get_holiday_type_display(),
            "Optional" if h.is_optional else "Mandatory",
        ]
        for h in qs.select_related("company").order_by("date")
    ]

    return {
        "title": "Holiday Calendar",
        "period": str(year),
        "columns": [
            "Company",
            "Date",
            "Holiday",
            "Type",
            "Applicability",
        ],
        "rows": rows,
        "totals": {"holidays": len(rows)},
    }


REPORTS = {
    "employee_master": employee_master,
    "employee_company_wise": employee_company_wise,
    "employee_department_wise": employee_department_wise,
    "employee_designation_wise": employee_designation_wise,
    "employee_active": lambda p, u: _employee_by_status(p, u, "ACTIVE"),
    "employee_inactive": lambda p, u: _employee_by_status(p, u, "INACTIVE"),
    "employee_exited": lambda p, u: _employee_by_status(p, u, "EXITED"),
    "attendance_daily": attendance_daily,
    "attendance_monthly_register": attendance_monthly_register,
    "attendance_employee_history": attendance_employee_history,
    "attendance_present": lambda p, u: attendance_by_status(p, u, "present"),
    "attendance_absent": lambda p, u: attendance_by_status(p, u, "absent"),
    "attendance_leave": lambda p, u: attendance_by_status(p, u, "leave"),
    "attendance_half_day": lambda p, u: attendance_by_status(p, u, "half_day"),
    "attendance_holiday_working": lambda p, u: _special_working(p, u, "worked_on_holiday"),
    "attendance_weekoff_working": lambda p, u: _special_working(p, u, "worked_on_week_off"),
    "attendance_shift_wise": attendance_shift_wise,
    "attendance_working_hours": attendance_working_hours,
    "ot_daily": ot_daily,
    "ot_monthly": ot_monthly,
    "ot_employee": ot_monthly,
    "ot_salary": ot_salary,
    "payroll_monthly_salary_register": payroll_monthly_salary_register,
    "payroll_company_register": payroll_company_register,
    "payroll_department_register": payroll_department_register,
    "payroll_earnings": payroll_earnings,
    "payroll_deductions": payroll_deductions,
    "payroll_net_salary": payroll_net_salary,
    "payroll_payslip_register": payroll_payslip_register,
    "payroll_attendance_summary": payroll_monthly_salary_register,
    "leave_employee_history": leave_employee_history,
    "leave_monthly": leave_monthly,
    "leave_balance": leave_balance,
    "leave_type_usage": leave_type_usage,
    "holiday_calendar": holiday_calendar,
    "holiday_working": lambda p, u: _special_working(p, u, "worked_on_holiday"),
}
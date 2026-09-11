from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from openpyxl import load_workbook

from apps.companies.models import Company
from apps.employees.models import Employee
from apps.payroll.models import PayrollRun, Payslip


def normalize_name(value):
    return " ".join(value.split()).casefold()


def as_decimal(value):
    try:
        return Decimal(str(value or 0)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


def find_employee(company_id, source_name):
    """Exact normalized full-name match within a company.

    Returns (employee, status) where status is matched/unmatched/ambiguous.
    """
    name_key = normalize_name(source_name)
    employees = Employee.objects.filter(company_id=company_id).only(
        "id", "employee_code", "first_name", "last_name"
    )

    exact = [
        employee
        for employee in employees
        if normalize_name(f"{employee.first_name} {employee.last_name}") == name_key
    ]
    if len(exact) == 1:
        return exact[0], "matched"
    if len(exact) > 1:
        return None, "ambiguous"

    source_tokens = {t for t in name_key.split() if len(t) >= 2}
    if source_tokens:
        order_insensitive = [
            employee
            for employee in employees
            if source_tokens
            <= {
                t for t in normalize_name(
                    f"{employee.first_name} {employee.last_name}"
                ).split()
                if len(t) >= 2
            }
        ]
        if len(order_insensitive) == 1:
            return order_insensitive[0], "matched"
        if len(order_insensitive) > 1:
            return None, "ambiguous"

    return None, "unmatched"


SHEET_COMPANY = {
    "SRINIVASA": "ST",
    "SUDHARSHAN": "SUT",
    "SBT": "SBT",
}

PAYROLL_YEAR = 2026
PAYROLL_MONTH = 7
CALENDAR_DAYS = 27
PAY_DATE = date(2026, 7, 31)


class Command(BaseCommand):
    help = (
        "Import July 2026 payout figures from the JULY 2026_ST workbook as "
        "one PayrollRun + Payslips per company (safe matches only)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--workbook",
            default=str(Path(settings.BASE_DIR).parent / "JULY 2026_ST.xlsx"),
            help="Salary workbook path",
        )
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Actually write records (default is dry run)",
        )

    def handle(self, *args, **options):
        workbook_path = options["workbook"]
        path = Path(workbook_path)
        if not path.is_file():
            raise CommandError(f"Workbook does not exist: {path}")

        try:
            workbook = load_workbook(path, data_only=True, read_only=True)
        except Exception as exc:
            raise CommandError(f"Could not read workbook: {path}") from exc

        companies = {}
        for code in set(SHEET_COMPANY.values()):
            try:
                companies[code] = Company.objects.get(code=code)
            except Company.DoesNotExist as exc:
                raise CommandError(f"Required company code does not exist: {code}") from exc

        parsed_rows = self._parse_workbook(workbook)

        planned = []
        skips = []
        for company_code, name, fields in parsed_rows:
            company_id = companies[company_code].id
            employee, status = find_employee(company_id, name)
            if status == "matched":
                planned.append(
                    {
                        "company_code": company_code,
                        "employee": employee,
                        **fields,
                    }
                )
            else:
                skips.append(
                    {
                        "company_code": company_code,
                        "name": name,
                        "status": status,
                    }
                )

        for skip in skips:
            self.stdout.write(
                f"SKIP ({skip['status']}): {skip['company_code']} | {skip['name']}"
            )

        self.stdout.write("")
        self.stdout.write(f"PLANNED payslips: {len(planned)}")
        self.stdout.write(f"SKIPPED rows: {len(skips)}")

        per_company = {}
        for row in planned:
            per_company.setdefault(row["company_code"], []).append(row)

        for company_code, rows in per_company.items():
            self.stdout.write(
                f"\n== {company_code} PayrollRun Jul-{PAYROLL_YEAR}: {len(rows)} payslips =="
            )
            for row in rows:
                self.stdout.write(
                    f"  {row['employee'].employee_code} | basic={row['basic_salary']} "
                    f"wd={row['working_days']} ot={row['ot_hours']} "
                    f"otamt={row['overtime_amount']} bonus={row['bonus']} "
                    f"gross={row['gross_salary']} net={row['net_salary']}"
                )

        if not options["commit"]:
            self.stdout.write(self.style.WARNING("\nDRY RUN: no database changes made. Use --commit to write."))
            return

        with transaction.atomic():
            for company_code, rows in per_company.items():
                payroll, _ = PayrollRun.objects.get_or_create(
                    company=companies[company_code],
                    year=PAYROLL_YEAR,
                    month=PAYROLL_MONTH,
                    defaults={
                        "pay_date": PAY_DATE,
                        "working_days": Decimal("27.00"),
                        "status": PayrollRun.Status.CALCULATED,
                    },
                )
                for row in rows:
                    Payslip.objects.update_or_create(
                        payroll_run=payroll,
                        employee=row["employee"],
                        defaults={
                            "basic_salary": row["basic_salary"],
                            "bonus": row["bonus"],
                            "working_days": row["working_days"],
                            "present_days": row["working_days"],
                            "calendar_days": CALENDAR_DAYS,
                            "ot_hours": row["ot_hours"],
                            "overtime_amount": row["overtime_amount"],
                            "gross_salary": row["gross_salary"],
                            "deductions": row["deductions"],
                            "net_salary": row["net_salary"],
                        },
                    )
            self.stdout.write(self.style.SUCCESS("Payroll import committed successfully"))

    def _parse_workbook(self, workbook):
        rows = []
        for sheet_name, company_code in SHEET_COMPANY.items():
            if sheet_name not in workbook.sheetnames:
                raise CommandError(f"Required workbook sheet does not exist: {sheet_name}")
            sheet = workbook[sheet_name]
            for row in sheet.iter_rows(values_only=True):
                parsed = self._extract(sheet_name, row)
                if parsed:
                    name, fields = parsed
                    rows.append((company_code, name, fields))
        return rows

    @staticmethod
    def _extract(sheet_name, row):
        """Return (name, fields) for an employee data row, else None.

        Fields: basic_salary, working_days, ot_hours, overtime_amount,
        bonus, gross_salary, deductions, net_salary.
        """
        def cell(idx):
            return row[idx] if idx < len(row) else None

        def num(idx):
            value = cell(idx)
            if value is None:
                return None
            if isinstance(value, str):
                return None
            return as_decimal(value)

        if sheet_name in ("SRINIVASA", "SUDHARSHAN"):
            # B=SNo C=Name D=WD1 E=WD2 F=Salary G=Att H=OT I=PerDay J=OTsal K=Total
            name = cell(2)
            if not isinstance(name, str) or not name.strip():
                return None
            salary = cell(5)
            if not isinstance(salary, (int, float, Decimal)):
                return None
            basic = as_decimal(salary)
            working_days = num(4)
            ot_hours = num(7) or Decimal("0.00")
            overtime_amount = num(9) or Decimal("0.00")
            bonus = num(6) or Decimal("0.00")
            net_salary = num(10)
            if net_salary is None:
                net_salary = basic + bonus
        else:
            # SBT: A=SL B=Name C=WD D=Salary E=OT F=OTsal G=Total H=Att I=OneDay J=RoundOff SALARY
            name = cell(1)
            if not isinstance(name, str) or not name.strip():
                return None
            salary = cell(3)
            if not isinstance(salary, (int, float, Decimal)):
                return None
            basic = as_decimal(salary)
            working_days = num(2)
            ot_hours = num(4) or Decimal("0.00")
            overtime_amount = num(5) or Decimal("0.00")
            bonus = num(7) or Decimal("0.00")
            net_salary = num(9)
            if net_salary is None:
                net_salary = num(6)  # TOTAL SALARY fallback
            if net_salary is None:
                net_salary = basic + bonus

        if working_days is None:
            working_days = Decimal("0.00")

        gross_salary = basic + bonus
        deductions = (gross_salary + overtime_amount - net_salary)
        if deductions < 0:
            deductions = Decimal("0.00")

        return (
            name.strip(),
            {
                "basic_salary": basic,
                "working_days": working_days,
                "ot_hours": ot_hours,
                "overtime_amount": overtime_amount,
                "bonus": bonus,
                "gross_salary": gross_salary,
                "deductions": deductions,
                "net_salary": net_salary,
            },
        )

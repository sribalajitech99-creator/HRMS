from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.companies.models import (
    Company,
    Department,
    Designation,
)

from apps.employees.models import Employee


class Command(BaseCommand):
    help = "Import employees for SBT, ST and SUT"

    # IMPORTANT:
    # Source files do not contain real joining dates.
    # This is only a temporary placeholder.
    DEFAULT_JOINING_DATE = date(2026, 8, 1)

    def split_name(self, full_name):
        """
        Preserve the original name while splitting it
        into first_name and last_name.
        """

        full_name = full_name.strip()

        parts = full_name.split()

        if len(parts) == 1:
            return parts[0], ""

        return parts[0], " ".join(parts[1:])

    def get_department(self, company, name):
        if not name:
            return None

        department, _ = Department.objects.get_or_create(
            company=company,
            name=name,
            defaults={
                "code": self.make_department_code(name),
                "is_active": True,
            },
        )

        return department

    def make_department_code(self, name):
        mapping = {
            "Quality": "QUALITY",
            "Grinding": "GRINDING",
            "Rolling": "ROLLING",
            "Final Inspection": "FINAL",
            "CNC": "CNC",
            "Hotforging": "HOTFORGING",
        }

        return mapping.get(
            name,
            name.upper().replace(" ", "_")[:20],
        )

    def get_designation(
        self,
        company,
        department,
        name,
    ):
        if not name:
            return None

        designation, _ = Designation.objects.get_or_create(
            company=company,
            name=name,
            defaults={
                "code": self.make_designation_code(name),
                "department": department,
                "level": 1,
                "is_active": True,
            },
        )

        # If designation already exists but has no department,
        # connect it safely.
        if (
            department
            and not designation.department
        ):
            designation.department = department
            designation.save(
                update_fields=["department"]
            )

        return designation

    def make_designation_code(self, name):
        mapping = {
            "CNC Operator": "CNC_OPERATOR",
            "Final Inspector": "FINAL_INSPECTOR",
        }

        return mapping.get(
            name,
            name.upper().replace(" ", "_")[:30],
        )

    def create_employee(
        self,
        company,
        employee_code,
        full_name,
        department_name=None,
        designation_name=None,
    ):
        first_name, last_name = self.split_name(
            full_name
        )

        department = self.get_department(
            company,
            department_name,
        )

        designation = self.get_designation(
            company,
            department,
            designation_name,
        )

        employee, created = Employee.objects.update_or_create(
            employee_code=employee_code,
            defaults={
                "company": company,
                "department": department,
                "designation": designation,
                "first_name": first_name,
                "last_name": last_name,
                "joining_date": self.DEFAULT_JOINING_DATE,
                "employment_type": "Permanent",
                "status": "ACTIVE",
            },
        )

        action = "CREATED" if created else "UPDATED"

        self.stdout.write(
            f"{action}: {employee_code} - {full_name}"
        )

        return employee

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "Starting employee import..."
            )
        )

        # =====================================================
        # COMPANIES
        # =====================================================

        st = Company.objects.get(
            code="ST"
        )

        sbt = Company.objects.get(
            code="SBT"
        )

        sut = Company.objects.get(
            code="SUT"
        )

        # =====================================================
        # SRI BALAJI TECH - SBT
        # 63 EMPLOYEES
        # =====================================================

        sbt_employees = [

            # QUALITY
            (
                "Ranjith",
                "Quality",
                None,
            ),

            # GRINDING
            (
                "Luruthusamy",
                "Grinding",
                None,
            ),
            (
                "Keshap",
                "Grinding",
                None,
            ),
            (
                "Akhaya Kumar",
                "Grinding",
                None,
            ),
            (
                "Sushil",
                "Grinding",
                None,
            ),

            # ROLLING
            (
                "Saunti Maji",
                "Rolling",
                None,
            ),
            (
                "Debendra",
                "Rolling",
                None,
            ),
            (
                "Tripati",
                "Rolling",
                None,
            ),

            # FINAL INSPECTION
            (
                "Rattan",
                "Final Inspection",
                "Final Inspector",
            ),
            (
                "Chandan",
                "Final Inspection",
                "Final Inspector",
            ),
            (
                "Bharath",
                "Final Inspection",
                "Final Inspector",
            ),
            (
                "Renuga",
                "Final Inspection",
                "Final Inspector",
            ),
            (
                "Salasambae",
                "Final Inspection",
                "Final Inspector",
            ),
            (
                "Poonkondi",
                "Final Inspection",
                "Final Inspector",
            ),

            # GRINDING
            (
                "Maha",
                "Grinding",
                None,
            ),

            # FINAL INSPECTION
            (
                "Ansari",
                "Final Inspection",
                "Final Inspector",
            ),
            (
                "Kisku",
                "Final Inspection",
                "Final Inspector",
            ),
            (
                "Durugha",
                "Final Inspection",
                "Final Inspector",
            ),

            # CNC SECTOR
            (
                "Uppendhar",
                "CNC",
                None,
            ),
            (
                "Lakshmi",
                "CNC",
                None,
            ),
            (
                "Aniruth",
                "CNC",
                None,
            ),
            (
                "Kabin",
                "CNC",
                None,
            ),

            # CNC OPERATORS
            (
                "Janakiraman",
                "CNC",
                "CNC Operator",
            ),
            (
                "Ranjith",
                "CNC",
                "CNC Operator",
            ),
            (
                "Laduram",
                "CNC",
                "CNC Operator",
            ),
            (
                "Gabindo Pansing",
                "CNC",
                "CNC Operator",
            ),
            (
                "Jadop Soy",
                "CNC",
                "CNC Operator",
            ),
            (
                "Debo",
                "CNC",
                "CNC Operator",
            ),
            (
                "Rasananda",
                "CNC",
                "CNC Operator",
            ),
            (
                "Ramakrishna",
                "CNC",
                "CNC Operator",
            ),
            (
                "Sugun Soy",
                "CNC",
                "CNC Operator",
            ),
            (
                "Dulu Soy",
                "CNC",
                "CNC Operator",
            ),
            (
                "Krishna",
                "CNC",
                "CNC Operator",
            ),
            (
                "Jiten",
                "CNC",
                "CNC Operator",
            ),
            (
                "Hajan",
                "CNC",
                "CNC Operator",
            ),
            (
                "Dibara Purth",
                "CNC",
                "CNC Operator",
            ),
            (
                "Trilochar",
                "CNC",
                "CNC Operator",
            ),
            (
                "Rajinesh",
                "CNC",
                "CNC Operator",
            ),
            (
                "Anubhab",
                "CNC",
                "CNC Operator",
            ),
            (
                "Samu",
                "CNC",
                "CNC Operator",
            ),
            (
                "Mansing",
                "CNC",
                "CNC Operator",
            ),
            (
                "Beemson Paliya",
                "CNC",
                "CNC Operator",
            ),
            (
                "Kamal",
                "CNC",
                "CNC Operator",
            ),
            (
                "Vairab",
                "CNC",
                "CNC Operator",
            ),
            (
                "Rabi",
                "CNC",
                "CNC Operator",
            ),
            (
                "Somnath Soy",
                "CNC",
                "CNC Operator",
            ),
            (
                "Jaga Mohan",
                "CNC",
                "CNC Operator",
            ),
            (
                "Fakhirman",
                "CNC",
                "CNC Operator",
            ),
            (
                "Kande Ho",
                "CNC",
                "CNC Operator",
            ),
            (
                "Hindu soy",
                "CNC",
                "CNC Operator",
            ),
            (
                "Pravath",
                "CNC",
                "CNC Operator",
            ),
            (
                "kanbei",
                "CNC",
                "CNC Operator",
            ),
            (
                "Dhaasekar",
                "CNC",
                "CNC Operator",
            ),
            (
                "Ranjith II",
                "CNC",
                "CNC Operator",
            ),
            (
                "Lal Munda",
                "CNC",
                "CNC Operator",
            ),
            (
                "Ganesh",
                "CNC",
                "CNC Operator",
            ),
            (
                "Umash",
                "CNC",
                "CNC Operator",
            ),
            (
                "Sriram",
                "CNC",
                "CNC Operator",
            ),
            (
                "Sharkar",
                "CNC",
                "CNC Operator",
            ),
            (
                "Chandan Pingua",
                "CNC",
                "CNC Operator",
            ),
            (
                "Sunaram",
                "CNC",
                "CNC Operator",
            ),
            (
                "Sankar",
                "CNC",
                "CNC Operator",
            ),

            # FINAL INSPECTION
            (
                "Sahil",
                "Final Inspection",
                "Final Inspector",
            ),
        ]

        for index, employee_data in enumerate(
            sbt_employees,
            start=1,
        ):
            name, department, designation = (
                employee_data
            )

            self.create_employee(
                company=sbt,
                employee_code=f"SBT{index:03d}",
                full_name=name,
                department_name=department,
                designation_name=designation,
            )

        # =====================================================
        # SRINIVASA TECHNOLOGY - ST
        # 27 EMPLOYEES
        # =====================================================

        st_employees = [

            # Department not available in source
            ("D RAVI", None, None),
            ("C MURUGAIAN", None, None),
            ("DHANAPAL", None, None),
            ("PRABAKAR", None, None),
            ("PANDIARAJAN", None, None),
            ("V N IYYAPPAN", None, None),

            # HOTFORGING
            ("KARTHICK", "Hotforging", None),
            ("SUNDARAM", "Hotforging", None),
            ("VASU", "Hotforging", None),
            ("SEKAR", "Hotforging", None),
            ("ARUNKUMAR", "Hotforging", None),
            (
                "THULAL BINDHANI",
                "Hotforging",
                None,
            ),
            ("JOJU", "Hotforging", None),
            (
                "RAJA BINDHANI",
                "Hotforging",
                None,
            ),
            (
                "MAHENDRAN",
                "Hotforging",
                None,
            ),
            ("MANGAL", "Hotforging", None),

            # CNC
            (
                "CHINNARAJ",
                "CNC",
                "CNC Operator",
            ),
            (
                "SATHYA SELAN",
                "CNC",
                "CNC Operator",
            ),
            (
                "REGAN",
                "CNC",
                "CNC Operator",
            ),
            (
                "PAPPU",
                "CNC",
                "CNC Operator",
            ),
            (
                "AJAY",
                "CNC",
                "CNC Operator",
            ),
            (
                "JANARTHANAN BANDIA",
                "CNC",
                "CNC Operator",
            ),
            (
                "PRITHILAL",
                "CNC",
                "CNC Operator",
            ),
            (
                "SAM BIHARI",
                "CNC",
                "CNC Operator",
            ),
            (
                "ANIL",
                "CNC",
                "CNC Operator",
            ),
            (
                "RAJAN LOHAR",
                "CNC",
                "CNC Operator",
            ),
            (
                "TIRTH KARSHAL",
                "CNC",
                "CNC Operator",
            ),

            # FINAL INSPECTION
            (
                "RANJANI",
                "Final Inspection",
                "Final Inspector",
            ),
        ]

        for index, employee_data in enumerate(
            st_employees,
            start=1,
        ):
            name, department, designation = (
                employee_data
            )

            self.create_employee(
                company=st,
                employee_code=f"ST{index:03d}",
                full_name=name,
                department_name=department,
                designation_name=designation,
            )

        # =====================================================
        # SUDHARASAN TECHNOLOGY - SUT
        # 24 EMPLOYEES
        #
        # Excel does not provide department headings for
        # these employees, therefore department/designation
        # are intentionally left blank.
        # =====================================================

        sut_employees = [
            "S SUNDARAMOORTHY",
            "RAMACHANDRA",
            "CHAMPAI SOY",
            "JAYAPAL",
            "MAN SINGH",
            "RAGHUL",
            "PARAMESWAR",
            "LOL MOHAN SOY",
            "NIKIL",
            "CHOTTU",
            "DEEPAK",
            "RAM JANMA",
            "SHANKAR",
            "RADHE SHYAM",
            "RAMO",
            "PARVIN",
            "SURAP MARK",
            "Guru Charan",
            "Sukulal",
            "Bhurbadra",
            "Chandan",
            "Madhu",
            "Tintu",
            "EGAVALLI",
        ]

        for index, name in enumerate(
            sut_employees,
            start=1,
        ):
            self.create_employee(
                company=sut,
                employee_code=f"SUT{index:03d}",
                full_name=name,
                department_name=None,
                designation_name=None,
            )

        # =====================================================
        # RESULT
        # =====================================================

        sbt_count = Employee.objects.filter(
            company=sbt
        ).count()

        st_count = Employee.objects.filter(
            company=st
        ).count()

        sut_count = Employee.objects.filter(
            company=sut
        ).count()

        total_count = Employee.objects.filter(
            company__in=[
                sbt,
                st,
                sut,
            ]
        ).count()

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "=================================="
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "EMPLOYEE IMPORT COMPLETED"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "=================================="
            )
        )

        self.stdout.write(
            f"SBT Employees : {sbt_count}"
        )

        self.stdout.write(
            f"ST Employees  : {st_count}"
        )

        self.stdout.write(
            f"SUT Employees : {sut_count}"
        )

        self.stdout.write(
            f"TOTAL         : {total_count}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "=================================="
            )
        )
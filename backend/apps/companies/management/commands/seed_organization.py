from django.core.management.base import BaseCommand

from apps.companies.models import (
    Company,
    Department,
    Designation,
)


class Command(BaseCommand):
    help = "Create HRMS companies, departments and designations"

    def handle(self, *args, **options):

        companies = [
            {
                "name": "Srinivasa Technology",
                "code": "ST",
                "employee_prefix": "ST",
            },
            {
                "name": "Sri Balaji Tech",
                "code": "SBT",
                "employee_prefix": "SBT",
            },
            {
                "name": "Sudharasan Technology",
                "code": "SUT",
                "employee_prefix": "SUT",
            },
        ]

        company_objects = {}

        for item in companies:
            company, created = (
                Company.objects.update_or_create(
                    code=item["code"],
                    defaults={
                        "name": item["name"],
                        "legal_name": item["name"],
                        "employee_prefix":
                            item["employee_prefix"],
                        "country": "India",
                        "currency": "INR",
                        "is_active": True,
                    }
                )
            )

            company_objects[
                item["code"]
            ] = company

            self.stdout.write(
                f"Company ready: {company.name}"
            )

        standard_departments = [
            ("OWNER", "Owner"),
            ("PLANT_HEAD", "Plant Head"),
            ("ACCOUNTS", "Accounts"),
            ("QUALITY", "Quality"),
            ("CUTTING", "Cutting"),
            ("CENTER", "Center"),
            ("CNC", "CNC"),
            (
                "FINAL_INSPECTION",
                "Final Inspection"
            ),
            ("DISPATCH", "Dispatch"),
        ]

        st_departments = [
            (
                "HOTFORGING",
                "Hotforging"
            ),
        ]

        department_objects = {}

        for company_code, company in (
            company_objects.items()
        ):
            department_objects[
                company_code
            ] = {}

            departments = list(
                standard_departments
            )

            if company_code == "ST":
                departments += st_departments

            for code, name in departments:
                department, created = (
                    Department.objects
                    .update_or_create(
                        company=company,
                        code=code,
                        defaults={
                            "name": name,
                            "is_active": True,
                        }
                    )
                )

                department_objects[
                    company_code
                ][code] = department

        standard_designations = [
            (
                "CUTTING_OPERATOR",
                "Cutting Operator",
                "CUTTING",
            ),
            (
                "CENTER_OPERATOR",
                "Center Operator",
                "CENTER",
            ),
            (
                "CNC_OPERATOR",
                "CNC Operator",
                "CNC",
            ),
            (
                "FINAL_INSPECTOR",
                "Final Inspector",
                "FINAL_INSPECTION",
            ),
            (
                "DISPATCHER",
                "Dispatcher",
                "DISPATCH",
            ),
        ]

        st_designations = [
            (
                "HOTFORGING_SETTER",
                "Hotforging Setter",
                "HOTFORGING",
            ),
            (
                "HOTFORGING_OPERATOR",
                "Hotforging Operator",
                "HOTFORGING",
            ),
            (
                "HOTFORGING_HELPER",
                "Hotforging Helper",
                "HOTFORGING",
            ),
        ]

        for company_code, company in (
            company_objects.items()
        ):
            designations = list(
                standard_designations
            )

            if company_code == "ST":
                designations += (
                    st_designations
                )

            for (
                code,
                name,
                department_code
            ) in designations:

                Designation.objects.update_or_create(
                    company=company,
                    code=code,
                    defaults={
                        "name": name,
                        "department":
                            department_objects[
                                company_code
                            ][
                                department_code
                            ],
                        "level": 1,
                        "is_active": True,
                    }
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Organization setup completed successfully."
            )
        )
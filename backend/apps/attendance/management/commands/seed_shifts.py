from django.core.management.base import (
    BaseCommand,
)

from apps.companies.models import (
    Company,
)

from apps.attendance.models import (
    Shift,
)


class Command(BaseCommand):
    help = "Create standard HRMS shifts"

    def handle(
        self,
        *args,
        **options,
    ):
        companies = (
            Company.objects
            .filter(
                code__in=[
                    "ST",
                    "SBT",
                    "SUT",
                ]
            )
        )

        shifts = [
            {
                "code": "GENERAL-I",
                "name": "General Shift - I",
                "start_time": "09:00",
                "end_time": "17:00",
                "is_night_shift": False,
                "description":
                    "General Shift I - Final Inspection",
            },
            {
                "code": "GENERAL-II",
                "name": "General Shift - II",
                "start_time": "08:30",
                "end_time": "18:30",
                "is_night_shift": False,
                "description":
                    "Management, Accounts and Plant Head",
            },
            {
                "code": "HF-I",
                "name": "Hotforging Shift - I",
                "start_time": "06:00",
                "end_time": "14:00",
                "is_night_shift": False,
                "description":
                    "Hotforging Morning Shift",
            },
            {
                "code": "HF-II",
                "name": "Hotforging Shift - II",
                "start_time": "14:00",
                "end_time": "22:00",
                "is_night_shift": False,
                "description":
                    "Hotforging Evening Shift",
            },
            {
                "code": "CNC-I",
                "name": "CNC Shift - I",
                "start_time": "08:30",
                "end_time": "20:30",
                "is_night_shift": False,
                "description":
                    "CNC / Other Day Shift",
            },
            {
                "code": "CNC-II",
                "name": "CNC Shift - II",
                "start_time": "20:30",
                "end_time": "08:30",
                "is_night_shift": True,
                "description":
                    "CNC / Other Night Shift",
            },
        ]

        for company in companies:
            for data in shifts:
                shift, created = (
                    Shift.objects.update_or_create(
                        company=company,
                        code=data["code"],
                        defaults=data,
                    )
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{company.code} - "
                        f"{shift.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "All shifts created successfully."
            )
        )
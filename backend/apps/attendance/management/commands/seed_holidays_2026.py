from datetime import date

from django.core.management.base import (
    BaseCommand,
)

from apps.companies.models import Company
from apps.attendance.models import Holiday


class Command(BaseCommand):
    help = "Create 2026 HRMS holidays"

    def handle(
        self,
        *args,
        **options,
    ):
        companies = Company.objects.filter(
            code__in=[
                "ST",
                "SBT",
                "SUT",
            ]
        )

        holidays = [
            (
                "New Year's Day",
                date(2026, 1, 1),
                "NATIONAL",
            ),
            (
                "Pongal",
                date(2026, 1, 15),
                "STATE",
            ),
            (
                "Thiruvalluvar Day",
                date(2026, 1, 16),
                "STATE",
            ),
            (
                "Uzhavar Thirunal",
                date(2026, 1, 17),
                "STATE",
            ),
            (
                "Republic Day",
                date(2026, 1, 26),
                "NATIONAL",
            ),
            (
                "Tamil New Year",
                date(2026, 4, 14),
                "STATE",
            ),
            (
                "May Day",
                date(2026, 5, 1),
                "NATIONAL",
            ),
            (
                "Independence Day",
                date(2026, 8, 15),
                "NATIONAL",
            ),
            (
                "Gandhi Jayanti",
                date(2026, 10, 2),
                "NATIONAL",
            ),
            (
                "Christmas",
                date(2026, 12, 25),
                "NATIONAL",
            ),
        ]

        for company in companies:
            for (
                name,
                holiday_date,
                holiday_type,
            ) in holidays:

                Holiday.objects.update_or_create(
                    company=company,
                    date=holiday_date,
                    name=name,
                    defaults={
                        "holiday_type":
                            holiday_type,
                        "is_optional":
                            False,
                        "is_active":
                            True,
                    },
                )

                self.stdout.write(
                    f"{company.code} "
                    f"{holiday_date} "
                    f"{name}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                "2026 holidays created."
            )
        )

        
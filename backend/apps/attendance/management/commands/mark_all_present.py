from datetime import time

from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.db import transaction

from apps.attendance.models import (
    Attendance,
)
from apps.employees.models import Employee


class Command(BaseCommand):
    help = (
        "Mark all active employees PRESENT for the given "
        "date with 08:30-16:30 check in/out times."
    )

    def add_arguments(
        self,
        parser,
    ):
        parser.add_argument(
            "date",
            help="Attendance date in YYYY-MM-DD format.",
        )

        parser.add_argument(
            "--company",
            type=int,
            default=None,
            help="Restrict to a single company id.",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only show what would be created.",
        )

    @transaction.atomic
    def handle(
        self,
        *args,
        **options,
    ):
        from datetime import date as date_cls

        raw_date = options["date"]

        try:
            day = date_cls.fromisoformat(raw_date)
        except ValueError:
            raise CommandError(
                "Invalid date format. Use YYYY-MM-DD."
            )

        employees = Employee.objects.filter(
            status__in=[
                Employee.Status.ACTIVE,
                Employee.Status.PROBATION,
                Employee.Status.NOTICE,
            ]
        )

        if options["company"]:
            employees = employees.filter(
                company_id=options["company"]
            )

        employee_ids = list(
            employees.values_list(
                "id",
                flat=True,
            )
        )

        if not employee_ids:
            self.stdout.write(
                self.style.WARNING(
                    "No active employees found "
                    f"for {raw_date}."
                )
            )
            return

        check_in = time(
            8,
            30,
        )
        check_out = time(
            16,
            30,
        )

        total = len(employee_ids)

        if options["dry_run"]:
            self.stdout.write(
                f"Would mark {total} employees PRESENT "
                f"on {raw_date} (08:30 - 16:30)."
            )
            return

        created = 0
        updated = 0

        existing = set(
            Attendance.objects.filter(
                date=day,
                employee_id__in=employee_ids,
            ).values_list(
                "employee_id",
                flat=True,
            )
        )

        for employee_id in employee_ids:
            defaults = {
                "status":
                    Attendance.Status.PRESENT,
                "check_in_time": check_in,
                "check_out_time": check_out,
                "check_out_next_day": False,
                "remarks": "",
            }

            _, was_created = (
                Attendance.objects.update_or_create(
                    employee_id=employee_id,
                    date=day,
                    defaults=defaults,
                )
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Marked {total} employees PRESENT on "
                f"{raw_date} ({created} created, "
                f"{updated} updated)."
            )
        )

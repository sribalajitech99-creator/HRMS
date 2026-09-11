import re

from django.core.management.base import BaseCommand

from apps.employees.models import Employee


def parse_employee_code(code):
    match = re.match(r"^([A-Za-z]+)[\s_\-]*(\d+)$", code.strip())
    if not match:
        return None
    return match.group(1).upper(), int(match.group(2))


class Command(BaseCommand):

    help = "Normalize employee codes to PREFIXNNN (no spaces, 3-digit) and resolve duplicates."

    @staticmethod
    def next_available_code(prefix, start, taken_codes):
        num = start
        while True:
            candidate = f"{prefix}{num:03d}"
            if candidate not in taken_codes:
                return candidate
            num += 1

    def handle(self, *args, **options):
        affected = [
            e for e in Employee.objects.all()
            if parse_employee_code(e.employee_code) is not None
            and e.employee_code != f"{parse_employee_code(e.employee_code)[0]}{parse_employee_code(e.employee_code)[1]:03d}"
        ]
        affected.sort(key=lambda e: (e.employee_code, e.pk))

        taken_codes = set(
            Employee.objects.values_list("employee_code", flat=True)
        )

        normalized = 0
        for employee in affected:
            parsed = parse_employee_code(employee.employee_code)
            prefix, num = parsed
            candidate = self.next_available_code(prefix, num, taken_codes)
            taken_codes.discard(employee.employee_code)
            taken_codes.add(candidate)
            old_code = employee.employee_code
            employee.employee_code = candidate
            employee.save(update_fields=["employee_code"])
            normalized += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"{old_code} -> {candidate}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Normalized {normalized} employee code(s)."
            )
        )
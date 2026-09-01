from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.companies.models import Company
from apps.employees.models import Employee

from .services import (
    early_exit_minutes,
    effective_working_hours,
    is_overnight_shift,
    late_minutes,
    overtime_hours,
    worked_duration_hours,
)


class Shift(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="shifts",
    )

    name = models.CharField(
        max_length=120
    )

    code = models.CharField(
        max_length=30
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_night_shift = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    break_duration = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Scheduled break in minutes applied to net "
            "working hours. 0 means no break configured."
        ),
    )

    grace_time = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Grace period in minutes before a late check-in "
            "is counted. 0 means no grace."
        ),
    )

    minimum_half_day_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("4.00"),
        help_text=(
            "Minimum worked hours required for a full day. "
            "Used for half-day timing."
        ),
    )

    full_day_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Scheduled net full-day hours. Leave blank to "
            "auto-derive from start_time/end_time minus break."
        ),
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "company",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "company",
                    "code",
                ],
                name="unique_shift_code_per_company",
            )
        ]

    def __str__(self):
        return (
            f"{self.company.code} - "
            f"{self.name}"
        )


class Holiday(models.Model):
    class HolidayType(models.TextChoices):
        NATIONAL = (
            "NATIONAL",
            "National Holiday"
        )

        STATE = (
            "STATE",
            "State Holiday"
        )

        FESTIVAL = (
            "FESTIVAL",
            "Festival Holiday"
        )

        COMPANY = (
            "COMPANY",
            "Company Holiday"
        )

        OPTIONAL = (
            "OPTIONAL",
            "Optional Holiday"
        )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="holidays",
    )

    name = models.CharField(
        max_length=150
    )

    date = models.DateField()

    holiday_type = models.CharField(
        max_length=20,
        choices=HolidayType.choices,
        default=HolidayType.COMPANY,
    )

    is_optional = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "date",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "company",
                    "date",
                    "name",
                ],
                name="unique_company_holiday",
            )
        ]

    def __str__(self):
        return (
            f"{self.name} - "
            f"{self.date}"
        )


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = (
            "PRESENT",
            "Present"
        )

        ABSENT = (
            "ABSENT",
            "Absent"
        )

        ON_LEAVE = (
            "ON_LEAVE",
            "On Leave"
        )

        HALF_DAY = (
            "HALF_DAY",
            "Half Day"
        )

        HOLIDAY = (
            "HOLIDAY",
            "Holiday"
        )

        WEEK_OFF = (
            "WEEK_OFF",
            "Week Off"
        )

    class AttendanceType(models.TextChoices):
        FULL_DAY = (
            "FULL_DAY",
            "Full Day"
        )

        HALF_DAY_FIRST_HALF = (
            "HALF_DAY_FIRST_HALF",
            "Half Day - First Half"
        )

        HALF_DAY_SECOND_HALF = (
            "HALF_DAY_SECOND_HALF",
            "Half Day - Second Half"
        )

        PERMISSION = (
            "PERMISSION",
            "Permission"
        )

        LATE_ENTRY = (
            "LATE_ENTRY",
            "Late Entry"
        )

        EARLY_EXIT = (
            "EARLY_EXIT",
            "Early Exit"
        )

        WORK_FROM_HOME = (
            "WORK_FROM_HOME",
            "Work From Home"
        )

        ON_DUTY = (
            "ON_DUTY",
            "On Duty"
        )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    date = models.DateField()

    shift = models.ForeignKey(
        Shift,
        on_delete=models.PROTECT,
        related_name="attendance_records",
        null=True,
        blank=True,
    )

    holiday = models.ForeignKey(
        Holiday,
        on_delete=models.SET_NULL,
        related_name="attendance_records",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT,
    )

    attendance_type = models.CharField(
        max_length=30,
        choices=AttendanceType.choices,
        default=AttendanceType.FULL_DAY,
    )

    permission_from = models.TimeField(
        null=True,
        blank=True,
    )

    permission_to = models.TimeField(
        null=True,
        blank=True,
    )

    permission_reason = models.CharField(
        max_length=255,
        blank=True,
    )

    late_minutes = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Minutes late compared to shift start "
            "after grace. Auto-calculated."
        ),
    )

    early_exit_minutes = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Minutes left early compared to shift end. "
            "Auto-calculated."
        ),
    )

    check_in_time = models.TimeField(
        null=True,
        blank=True,
    )

    check_out_time = models.TimeField(
        null=True,
        blank=True,
    )

    check_out_next_day = models.BooleanField(
        default=False
    )

    working_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    calculated_ot_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    approved_ot_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    worked_on_holiday = models.BooleanField(
        default=False
    )

    worked_on_week_off = models.BooleanField(
        default=False
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-date",
            "employee__employee_code",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "date",
                ],
                name="unique_employee_attendance_date",
            )
        ]

        indexes = [
            models.Index(
                fields=[
                    "company",
                    "date",
                ],
                name="attendance_company_date_idx",
            ),
            models.Index(
                fields=[
                    "employee",
                    "date",
                ],
                name="attendance_employee_date_idx",
            ),
        ]

    def clean(self):
        if (
            self.employee_id
            and self.company_id
            and self.employee.company_id
            != self.company_id
        ):
            raise ValidationError(
                "Attendance company must match employee company."
            )

        if (
            self.shift_id
            and self.company_id
            and self.shift.company_id
            != self.company_id
        ):
            raise ValidationError(
                "Selected shift belongs to another company."
            )

        if (
            self.holiday_id
            and self.company_id
            and self.holiday.company_id
            != self.company_id
        ):
            raise ValidationError(
                "Selected holiday belongs to another company."
            )

        if (
            self.approved_ot_hours
            < Decimal("0")
        ):
            raise ValidationError(
                "Approved OT hours cannot be negative."
            )

        if (
            self.attendance_type
            == self.AttendanceType.PERMISSION
            and self.permission_from
            and self.permission_to
            and self.permission_to
            <= self.permission_from
        ):
            raise ValidationError(
                {
                    "permission_to":
                        "Permission end must be after "
                        "permission start."
                }
            )

    def calculate_hours(self):
        self.working_hours = Decimal(
            "0.00"
        )

        self.calculated_ot_hours = Decimal(
            "0.00"
        )

        self.late_minutes = 0
        self.early_exit_minutes = 0

        if self.status not in [
            self.Status.PRESENT,
            self.Status.HALF_DAY,
        ]:
            return

        if (
            not self.check_in_time
            or not self.check_out_time
        ):

            if self.shift:
                self.late_minutes = late_minutes(
                    self.check_in_time,
                    self.shift,
                )

                self.early_exit_minutes = early_exit_minutes(
                    self.check_out_time,
                    self.shift,
                )

            return

        overnight = (
            self.check_out_next_day
            or bool(
                self.shift
                and self.shift.is_night_shift
            )
            or (
                self.shift
                and is_overnight_shift(
                    self.shift.start_time,
                    self.shift.end_time,
                )
            )
        )

        self.working_hours = worked_duration_hours(
            self.shift,
            self.check_in_time,
            self.check_out_time,
            overnight,
        )

        self.calculated_ot_hours = overtime_hours(
            self.shift,
            self.working_hours,
        )

        self.late_minutes = late_minutes(
            self.check_in_time,
            self.shift,
        )

        self.early_exit_minutes = early_exit_minutes(
            self.check_out_time,
            self.shift,
        )

        if (
            self.attendance_type
            == self.AttendanceType.PERMISSION
        ):
            self.working_hours = effective_working_hours(
                self.shift,
                self.check_in_time,
                self.check_out_time,
                overnight,
                self.permission_from,
                self.permission_to,
            )

    def save(
        self,
        *args,
        **kwargs,
    ):
        if self.employee_id:
            self.company_id = (
                self.employee.company_id
            )

        if (
            self.shift_id
            and is_overnight_shift(
                self.shift.start_time,
                self.shift.end_time,
            )
        ):
            self.check_out_next_day = True

        self.calculate_hours()

        self.worked_on_holiday = (
            bool(self.holiday_id)
            and self.status
            == self.Status.PRESENT
        )

        self.worked_on_week_off = (
            self.status
            == self.Status.PRESENT
            and self.date.weekday()
            == 6
        )

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):
        return (
            f"{self.employee.employee_code} "
            f"- {self.date}"
        )
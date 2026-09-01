from datetime import timedelta

from django.conf import settings
from django.db import models

from apps.companies.models import Company

from apps.employees.models import Employee


class LeaveType(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="leave_types"
    )

    name = models.CharField(
        max_length=100
    )

    code = models.CharField(
        max_length=20
    )

    annual_allocation = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    is_paid = models.BooleanField(
        default=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = [
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "company",
                    "code",
                ],
                name="unique_leave_type_code_per_company"
            )
        ]

    def __str__(self):

        return self.name


class LeaveRequest(models.Model):

    class Status(models.TextChoices):

        PENDING = "PENDING", "Pending"

        APPROVED = "APPROVED", "Approved"

        REJECTED = "REJECTED", "Rejected"

        CANCELLED = "CANCELLED", "Cancelled"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="leave_requests",
        null=True,
        blank=True,
    )

    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT
    )

    start_date = models.DateField()

    end_date = models.DateField()

    total_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=1
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def save(
        self,
        *args,
        **kwargs
    ):

        if self.employee_id:
            self.company_id = (
                self.employee.company_id
            )

        if (
            self.start_date
            and self.end_date
        ):
            days = (
                (
                    self.end_date
                    - self.start_date
                ).days
                + 1
            )

            self.total_days = max(
                days,
                1,
            )

        super().save(
            *args,
            **kwargs
        )

    def __str__(self):

        return (
            f"{self.employee.employee_code} - "
            f"{self.start_date}"
        )
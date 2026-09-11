from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.companies.models import (
    Company,
    Department,
    Designation,
)


class Employee(models.Model):

    class Status(models.TextChoices):

        ACTIVE = "ACTIVE", "Active"

        PROBATION = "PROBATION", "Probation"

        NOTICE = "NOTICE", "Notice Period"

        INACTIVE = "INACTIVE", "Inactive"

        EXITED = "EXITED", "Exited"


    employee_code = models.CharField(
        max_length=30,
        unique=True
    )


    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employee"
    )


    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="employees"
    )


    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="employees"
    )


    designation = models.ForeignKey(
        Designation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="employees"
    )


    reporting_manager = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="team_members"
    )


    first_name = models.CharField(
        max_length=100
    )


    last_name = models.CharField(
        max_length=100,
        blank=True
    )


    work_email = models.EmailField(
        blank=True
    )


    mobile = models.CharField(
        max_length=30,
        blank=True
    )


    date_of_birth = models.DateField(
        null=True,
        blank=True
    )


    joining_date = models.DateField()


    exit_date = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "Date the employee left. Auto-set when status "
            "changes to Inactive or Exited."
        ),
    )


    employment_type = models.CharField(
        max_length=50,
        default="Permanent"
    )


    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )


    current_address = models.TextField(
        blank=True
    )


    permanent_address = models.TextField(
        blank=True
    )


    bank_name = models.CharField(
        max_length=100,
        blank=True
    )


    bank_account_number = models.CharField(
        max_length=60,
        blank=True
    )


    ifsc_code = models.CharField(
        max_length=30,
        blank=True
    )


    pan_number = models.CharField(
        max_length=30,
        blank=True
    )


    aadhaar_number = models.CharField(
        max_length=30,
        blank=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):

        return (
            f"{self.employee_code} - "
            f"{self.first_name}"
        )


    def save(
        self,
        *args,
        **kwargs,
    ):
        if self.status in [
            self.Status.INACTIVE,
            self.Status.EXITED,
        ] and not self.exit_date:
            self.exit_date = timezone.localdate()

        super().save(
            *args,
            **kwargs,
        )
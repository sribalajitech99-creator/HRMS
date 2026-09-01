from django.db import models

from apps.companies.models import Company

from apps.employees.models import Employee


class Asset(models.Model):

    class Status(models.TextChoices):

        AVAILABLE = "AVAILABLE", "Available"

        ASSIGNED = "ASSIGNED", "Assigned"

        REPAIR = "REPAIR", "In Repair"

        RETIRED = "RETIRED", "Retired"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="assets"
    )

    asset_code = models.CharField(
        max_length=50,
        unique=True
    )

    category = models.CharField(
        max_length=100
    )

    brand = models.CharField(
        max_length=100,
        blank=True
    )

    model = models.CharField(
        max_length=100,
        blank=True
    )

    serial_number = models.CharField(
        max_length=100,
        blank=True
    )

    assigned_employee = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assets"
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.AVAILABLE
    )

    class Meta:
        ordering = [
            "asset_code",
        ]

    def __str__(self):
        return self.asset_code
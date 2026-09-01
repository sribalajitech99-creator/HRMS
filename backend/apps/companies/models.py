from django.conf import settings
from django.db import models


class Company(models.Model):
    name = models.CharField(
        max_length=200
    )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    legal_name = models.CharField(
        max_length=250,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        default="India"
    )

    employee_prefix = models.CharField(
        max_length=20,
        default="EMP"
    )

    currency = models.CharField(
        max_length=10,
        default="INR"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_companies"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class CompanySetting(models.Model):
    """Persistent, company-scoped settings stored as key/value pairs.

    Keys use a ``group.key`` convention, e.g. ``payroll.working_days``.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="settings"
    )

    group = models.CharField(
        max_length=50
    )

    key = models.CharField(
        max_length=100
    )

    value = models.TextField(
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "company",
                    "group",
                    "key",
                ],
                name="unique_company_setting"
            )
        ]

    def __str__(self):
        return (
            f"{self.company.code} - "
            f"{self.group}.{self.key}"
        )


class Department(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="departments"
    )

    name = models.CharField(
        max_length=150
    )

    code = models.CharField(
        max_length=30
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "company",
                    "code"
                ],
                name="unique_department_code_per_company"
            )
        ]

    def __str__(self):
        return self.name


class Designation(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="designations"
    )

    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="designations"
    )

    name = models.CharField(
        max_length=150
    )

    code = models.CharField(
        max_length=30
    )

    level = models.PositiveIntegerField(
        default=1
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "company",
                    "code"
                ],
                name="unique_designation_code_per_company"
            )
        ]

    def __str__(self):
        return self.name
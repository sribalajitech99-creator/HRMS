from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.companies.models import Company


class User(AbstractUser):

    class Role(models.TextChoices):

        SUPER_ADMIN = (
            "SUPER_ADMIN",
            "Super Admin"
        )

        COMPANY_ADMIN = (
            "COMPANY_ADMIN",
            "Company Admin"
        )

        HR_MANAGER = (
            "HR_MANAGER",
            "HR Manager"
        )

        HR_EXECUTIVE = (
            "HR_EXECUTIVE",
            "HR Executive"
        )

        DEPARTMENT_MANAGER = (
            "DEPARTMENT_MANAGER",
            "Department Manager"
        )

        REPORTING_MANAGER = (
            "REPORTING_MANAGER",
            "Reporting Manager"
        )

        PAYROLL_MANAGER = (
            "PAYROLL_MANAGER",
            "Payroll Manager"
        )

        ACCOUNTS_MANAGER = (
            "ACCOUNTS_MANAGER",
            "Accounts Manager"
        )

        RECRUITER = (
            "RECRUITER",
            "Recruiter"
        )

        EMPLOYEE = (
            "EMPLOYEE",
            "Employee"
        )

        AUDITOR = (
            "AUDITOR",
            "Auditor"
        )


    email = models.EmailField(
        unique=True
    )


    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        db_index=True
    )


    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):

        return (
            self.get_full_name()
            or self.email
            or self.username
        )


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField(
        blank=True
    )

    link = models.CharField(
        max_length=255,
        blank=True
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.title
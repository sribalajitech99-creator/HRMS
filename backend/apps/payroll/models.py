from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.companies.models import Company

from apps.employees.models import Employee


class EmployeeSalary(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="salaries"
    )

    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    hra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    effective_from = models.DateField()

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = [
            "-effective_from",
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_code} - "
            f"{self.basic_salary}"
        )


class PayrollRun(models.Model):

    class Status(models.TextChoices):

        DRAFT = "DRAFT", "Draft"

        CALCULATED = "CALCULATED", "Calculated"

        APPROVED = "APPROVED", "Approved"

        PAID = "PAID", "Paid"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="payroll_runs"
    )

    year = models.PositiveIntegerField()

    month = models.PositiveIntegerField()

    working_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("26.00")
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-year",
            "-month",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "company",
                    "year",
                    "month",
                ],
                name="unique_payroll_run_company_period"
            )
        ]

    def __str__(self):
        return (
            f"{self.company.code} - "
            f"{self.month}/{self.year}"
        )


class Payslip(models.Model):

    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="payslips"
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="payslips"
    )

    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    hra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    working_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    present_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    absent_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    leave_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    ot_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )

    gross_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    overtime_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    net_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        ordering = [
            "employee__employee_code",
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_code} - "
            f"{self.payroll_run.month}/"
            f"{self.payroll_run.year}"
        )
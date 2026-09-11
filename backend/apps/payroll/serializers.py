from rest_framework import serializers

from .models import (
    EmployeeSalary,
    PayrollRun,
    Payslip,
)

from .utils import amount_in_words

from .pdf import mask_account_number


def _should_see_full_bank(user):
    """Staff and payroll roles see full bank details; employees do not."""
    staff_roles = {
        "COMPANY_ADMIN",
        "HR_MANAGER",
        "HR_EXECUTIVE",
        "PAYROLL_MANAGER",
        "ACCOUNTS_MANAGER",
        "AUDITOR",
    }

    return bool(
        user
        and user.is_authenticated
        and (
            user.is_superuser
            or user.role in staff_roles
        )
    )


class EmployeeSalarySerializer(serializers.ModelSerializer):

    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True
    )

    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalary
        fields = "__all__"

    def get_employee_name(self, obj):
        return (
            f"{obj.employee.first_name} "
            f"{obj.employee.last_name}"
        ).strip()

    def validate(self, attrs):
        employee = attrs.get(
            "employee",
            getattr(
                self.instance,
                "employee",
                None,
            ),
        )

        return attrs


class PayrollRunSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    company_code = serializers.CharField(
        source="company.code",
        read_only=True
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    period = serializers.SerializerMethodField()

    class Meta:
        model = PayrollRun
        fields = [
            "id",
            "company",
            "company_name",
            "company_code",
            "year",
            "month",
            "pay_date",
            "working_days",
            "status",
            "status_name",
            "period",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "status",
            "status_name",
        ]

    def get_period(self, obj):
        return f"{obj.month:02d}-{obj.year}"


class PayslipSerializer(serializers.ModelSerializer):

    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True
    )

    employee_name = serializers.SerializerMethodField()

    department_name = serializers.CharField(
        source="employee.department.name",
        read_only=True
    )

    designation_name = serializers.CharField(
        source="employee.designation.name",
        read_only=True
    )

    period = serializers.SerializerMethodField()

    month = serializers.IntegerField(
        source="payroll_run.month",
        read_only=True
    )

    year = serializers.IntegerField(
        source="payroll_run.year",
        read_only=True
    )

    pay_date = serializers.DateField(
        source="payroll_run.pay_date",
        read_only=True
    )

    joining_date = serializers.DateField(
        source="employee.joining_date",
        read_only=True
    )

    gross_earnings = serializers.SerializerMethodField()

    total_deductions = serializers.SerializerMethodField()

    amount_in_words = serializers.SerializerMethodField()

    bank_name = serializers.CharField(
        source="employee.bank_name",
        read_only=True
    )

    ifsc_code = serializers.CharField(
        source="employee.ifsc_code",
        read_only=True
    )

    bank_account = serializers.SerializerMethodField()

    account_holder = serializers.SerializerMethodField()

    class Meta:
        model = Payslip
        fields = [
            "id",
            "payroll_run",
            "period",
            "month",
            "year",
            "pay_date",
            "employee",
            "employee_code",
            "employee_name",
            "department_name",
            "designation_name",
            "joining_date",
            "basic_salary",
            "bonus",
            "dearness_allowance",
            "conveyance_allowance",
            "medical_allowance",
            "special_allowance",
            "other_allowance",
            "total_monthly",
            "per_day_rate",
            "no_of_days",
            "working_days",
            "calendar_days",
            "present_days",
            "absent_days",
            "leave_days",
            "paid_leave_days",
            "unpaid_leave_days",
            "half_days",
            "holidays",
            "week_offs",
            "ot_hours",
            "ot_rate",
            "lop_days",
            "lop_deduction",
            "gross_salary",
            "overtime_amount",
            "gross_earnings",
            "pf",
            "esi",
            "professional_tax",
            "tds",
            "other_deduction",
            "deductions",
            "total_deductions",
            "net_salary",
            "amount_in_words",
            "bank_name",
            "ifsc_code",
            "bank_account",
            "account_holder",
            "created_at",
        ]

        read_only_fields = [
            field
            for field in [
                "employee_code",
                "employee_name",
                "department_name",
                "designation_name",
                "period",
                "month",
                "year",
                "pay_date",
                "joining_date",
                "basic_salary",
                "bonus",
                "dearness_allowance",
                "conveyance_allowance",
                "medical_allowance",
                "special_allowance",
                "other_allowance",
                "total_monthly",
                "per_day_rate",
                "no_of_days",
                "working_days",
                "calendar_days",
                "present_days",
                "absent_days",
                "leave_days",
                "paid_leave_days",
                "unpaid_leave_days",
                "half_days",
                "holidays",
                "week_offs",
                "ot_hours",
                "ot_rate",
                "lop_days",
                "lop_deduction",
                "gross_salary",
                "overtime_amount",
                "gross_earnings",
                "pf",
                "esi",
                "professional_tax",
                "tds",
                "other_deduction",
                "deductions",
                "total_deductions",
                "net_salary",
                "amount_in_words",
                "bank_name",
                "ifsc_code",
                "bank_account",
                "account_holder",
            ]
        ]

    def get_employee_name(self, obj):
        return (
            f"{obj.employee.first_name} "
            f"{obj.employee.last_name}"
        ).strip()

    def get_period(self, obj):
        return (
            f"{obj.payroll_run.month:02d}-"
            f"{obj.payroll_run.year}"
        )

    def get_gross_earnings(self, obj):
        return (
            obj.gross_salary + obj.overtime_amount
        )

    def get_total_deductions(self, obj):
        return obj.deductions

    def get_amount_in_words(self, obj):
        return amount_in_words(obj.net_salary)

    def get_bank_account(self, obj):
        if _should_see_full_bank(
            self.context.get("request").user
            if self.context.get("request")
            else None
        ):
            return obj.employee.bank_account_number

        return mask_account_number(
            obj.employee.bank_account_number
        )

    def get_account_holder(self, obj):
        return (
            f"{obj.employee.first_name} "
            f"{obj.employee.last_name}"
        ).strip()
from rest_framework import serializers

from .models import (
    EmployeeSalary,
    PayrollRun,
    Payslip,
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

    company_name = serializers.CharField(
        source="payroll_run.company.name",
        read_only=True
    )

    department_name = serializers.CharField(
        source="employee.department.name",
        read_only=True
    )

    designation_name = serializers.CharField(
        source="employee.designation.name",
        read_only=True
    )

    period = serializers.SerializerMethodField()

    class Meta:
        model = Payslip
        fields = [
            "id",
            "payroll_run",
            "period",
            "employee",
            "employee_code",
            "employee_name",
            "company_name",
            "department_name",
            "designation_name",
            "basic_salary",
            "hra",
            "allowance",
            "working_days",
            "present_days",
            "absent_days",
            "leave_days",
            "ot_hours",
            "gross_salary",
            "overtime_amount",
            "deductions",
            "net_salary",
            "created_at",
        ]

        read_only_fields = [
            field
            for field in [
                "employee_code",
                "employee_name",
                "company_name",
                "department_name",
                "designation_name",
                "period",
                "basic_salary",
                "hra",
                "allowance",
                "working_days",
                "present_days",
                "absent_days",
                "leave_days",
                "ot_hours",
                "gross_salary",
                "overtime_amount",
                "deductions",
                "net_salary",
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
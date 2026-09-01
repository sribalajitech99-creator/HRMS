from rest_framework import serializers

from .models import (
    LeaveType,
    LeaveRequest,
)


class LeaveTypeSerializer(
    serializers.ModelSerializer
):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    class Meta:

        model = LeaveType

        fields = "__all__"


class LeaveRequestSerializer(
    serializers.ModelSerializer
):

    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True
    )

    employee_name = serializers.SerializerMethodField()

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    leave_type_name = serializers.CharField(
        source="leave_type.name",
        read_only=True
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    class Meta:

        model = LeaveRequest

        fields = [
            "id",
            "employee",
            "employee_code",
            "employee_name",
            "company",
            "company_name",
            "leave_type",
            "leave_type_name",
            "start_date",
            "end_date",
            "total_days",
            "reason",
            "status",
            "status_name",
            "approved_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "company",
            "status",
            "status_name",
            "approved_by",
            "total_days",
        ]

    def get_employee_name(
        self,
        obj
    ):
        return (
            f"{obj.employee.first_name} "
            f"{obj.employee.last_name}"
        ).strip()

    def validate(
        self,
        attrs
    ):
        employee = attrs.get(
            "employee",
            getattr(
                self.instance,
                "employee",
                None,
            ),
        )

        leave_type = attrs.get(
            "leave_type",
            getattr(
                self.instance,
                "leave_type",
                None,
            ),
        )

        if (
            employee
            and leave_type
            and leave_type.company_id
            != employee.company_id
        ):
            raise serializers.ValidationError(
                {
                    "leave_type":
                        "This leave type does not "
                        "belong to the employee's "
                        "company."
                }
            )

        start = attrs.get(
            "start_date",
            getattr(
                self.instance,
                "start_date",
                None,
            ),
        )

        end = attrs.get(
            "end_date",
            getattr(
                self.instance,
                "end_date",
                None,
            ),
        )

        if (
            start
            and end
            and end < start
        ):
            raise serializers.ValidationError(
                {
                    "end_date":
                        "End date cannot be "
                        "earlier than start date."
                }
            )

        return attrs


class LeaveBalanceSerializer(
    serializers.Serializer
):

    leave_type = serializers.IntegerField()

    leave_type_name = serializers.CharField()

    allocated = serializers.DecimalField(
        max_digits=7,
        decimal_places=2,
    )

    used = serializers.DecimalField(
        max_digits=7,
        decimal_places=2,
    )

    balance = serializers.DecimalField(
        max_digits=7,
        decimal_places=2,
    )
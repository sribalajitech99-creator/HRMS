from rest_framework import serializers

from .models import (
    Attendance,
    Holiday,
    Shift,
)


class ShiftSerializer(
    serializers.ModelSerializer
):
    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
    )

    class Meta:
        model = Shift

        fields = [
            "id",
            "company",
            "company_name",
            "name",
            "code",
            "start_time",
            "end_time",
            "is_night_shift",
            "is_active",
            "break_duration",
            "grace_time",
            "minimum_half_day_hours",
            "full_day_hours",
            "description",
        ]


class HolidaySerializer(
    serializers.ModelSerializer
):
    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
    )

    class Meta:
        model = Holiday

        fields = [
            "id",
            "company",
            "company_name",
            "name",
            "date",
            "holiday_type",
            "is_optional",
            "is_active",
        ]


class AttendanceSerializer(
    serializers.ModelSerializer
):
    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True,
    )

    employee_name = serializers.SerializerMethodField()

    company = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
    )

    shift_name = serializers.CharField(
        source="shift.name",
        read_only=True,
    )

    holiday_name = serializers.CharField(
        source="holiday.name",
        read_only=True,
    )

    class Meta:
        model = Attendance

        fields = [
            "id",

            "employee",
            "employee_code",
            "employee_name",

            "company",
            "company_name",

            "date",

            "shift",
            "shift_name",

            "holiday",
            "holiday_name",

            "status",
            "attendance_type",

            "permission_from",
            "permission_to",
            "permission_reason",

            "late_minutes",
            "early_exit_minutes",

            "check_in_time",
            "check_out_time",
            "check_out_next_day",

            "working_hours",

            "calculated_ot_hours",
            "approved_ot_hours",

            "worked_on_holiday",
            "worked_on_week_off",

            "remarks",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "company",
            "working_hours",
            "calculated_ot_hours",
            "late_minutes",
            "early_exit_minutes",
            "worked_on_holiday",
            "worked_on_week_off",
        ]

    def get_employee_name(
        self,
        obj,
    ):
        return (
            f"{obj.employee.first_name} "
            f"{obj.employee.last_name}"
        ).strip()

    def validate(
        self,
        attrs,
    ):
        employee = attrs.get(
            "employee",
            getattr(
                self.instance,
                "employee",
                None,
            ),
        )

        shift = attrs.get(
            "shift",
            getattr(
                self.instance,
                "shift",
                None,
            ),
        )

        holiday = attrs.get(
            "holiday",
            getattr(
                self.instance,
                "holiday",
                None,
            ),
        )

        if (
            employee
            and shift
            and shift.company_id
            != employee.company_id
        ):
            raise serializers.ValidationError(
                {
                    "shift":
                        "This shift belongs to another company."
                }
            )

        if (
            employee
            and holiday
            and holiday.company_id
            != employee.company_id
        ):
            raise serializers.ValidationError(
                {
                    "holiday":
                        "This holiday belongs to another company."
                }
            )

        return attrs

    def create(
        self,
        validated_data,
    ):
        employee = validated_data[
            "employee"
        ]

        validated_data[
            "company"
        ] = employee.company

        return super().create(
            validated_data
        )

    def update(
        self,
        instance,
        validated_data,
    ):
        employee = validated_data.get(
            "employee",
            instance.employee,
        )

        validated_data[
            "company"
        ] = employee.company

        return super().update(
            instance,
            validated_data,
        )
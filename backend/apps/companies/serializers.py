from rest_framework import serializers

from .models import (
    Company,
    CompanySetting,
    Department,
    Designation,
)


class CompanySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Company
        fields = "__all__"

        read_only_fields = (
            "created_by",
            "created_at",
            "updated_at",
        )


class DepartmentSerializer(
    serializers.ModelSerializer
):
    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    class Meta:
        model = Department
        fields = "__all__"


class DesignationSerializer(
    serializers.ModelSerializer
):
    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True
    )

    class Meta:
        model = Designation
        fields = "__all__"


class CompanySettingSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = CompanySetting
        fields = [
            "id",
            "company",
            "group",
            "key",
            "value",
            "updated_at",
        ]

        read_only_fields = [
            "company",
            "updated_at",
        ]
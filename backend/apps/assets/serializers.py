from rest_framework import serializers

from .models import Asset


class AssetSerializer(
    serializers.ModelSerializer
):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    employee_name = serializers.SerializerMethodField()

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    class Meta:

        model = Asset

        fields = [
            "id",
            "company",
            "company_name",
            "asset_code",
            "category",
            "brand",
            "model",
            "serial_number",
            "assigned_employee",
            "employee_name",
            "status",
            "status_name",
        ]

    def get_employee_name(self, obj):
        if not obj.assigned_employee_id:
            return None

        return (
            f"{obj.assigned_employee.first_name} "
            f"{obj.assigned_employee.last_name}"
        ).strip()
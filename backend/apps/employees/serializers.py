from rest_framework import serializers

from .models import Employee


class EmployeeSerializer(
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


    designation_name = serializers.CharField(
        source="designation.name",
        read_only=True
    )


    class Meta:

        model = Employee

        fields = "__all__"
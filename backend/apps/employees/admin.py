from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "employee_code",
        "first_name",
        "last_name",
        "company",
        "department",
        "designation",
        "status",
    )


    list_filter = (
        "company",
        "department",
        "status",
    )


    search_fields = (
        "employee_code",
        "first_name",
        "last_name",
        "work_email",
    )
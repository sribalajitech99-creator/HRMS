from django.contrib import admin

from .models import (
    Company,
    Department,
    Designation,
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "city",
        "state",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "legal_name",
    )

    list_filter = (
        "is_active",
        "state",
        "country",
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "company",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "company__name",
    )

    list_filter = (
        "company",
        "is_active",
    )


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "company",
        "department",
        "level",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "company__name",
        "department__name",
    )

    list_filter = (
        "company",
        "department",
        "is_active",
    )
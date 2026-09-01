from django.contrib import admin

from .models import (
    Attendance,
    Holiday,
    Shift,
)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "company",
        "start_time",
        "end_time",
        "is_night_shift",
        "is_active",
    ]

    list_filter = [
        "company",
        "is_night_shift",
        "is_active",
    ]

    search_fields = [
        "code",
        "name",
    ]


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = [
        "date",
        "name",
        "company",
        "holiday_type",
        "is_optional",
        "is_active",
    ]

    list_filter = [
        "company",
        "holiday_type",
        "is_active",
    ]

    search_fields = [
        "name",
    ]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        "date",
        "employee",
        "company",
        "status",
        "shift",
        "working_hours",
        "approved_ot_hours",
    ]

    list_filter = [
        "company",
        "status",
        "shift",
        "date",
    ]

    search_fields = [
        "employee__employee_code",
        "employee__first_name",
        "employee__last_name",
    ]
from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from .models import Notification, User


@admin.register(User)
class HRMSUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "company",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "company",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    fieldsets = (
        UserAdmin.fieldsets
        + (
            (
                "HRMS Access",
                {
                    "fields": (
                        "role",
                        "company",
                    )
                }
            ),
        )
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "title",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
    )

    search_fields = (
        "user__username",
        "title",
        "message",
    )
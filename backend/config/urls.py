from django.conf import settings

from django.conf.urls.static import static

from django.contrib import admin

from django.urls import (
    include,
    path,
)


urlpatterns = [
    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "api/v1/auth/",
        include(
            "apps.accounts.urls"
        )
    ),

    path(
        "api/v1/",
        include(
            "apps.companies.urls"
        )
    ),

    path(
        "api/v1/",
        include(
            "apps.employees.urls"
        )
    ),

    path(
        "api/v1/",
        include(
            "apps.attendance.urls"
        )
    ),

    path(
        "api/v1/",
        include(
            "apps.leave_management.urls"
        )
    ),

    path(
        "api/v1/",
        include(
            "apps.payroll.urls"
        )
    ),

    path(
        "api/v1/",
        include(
            "apps.recruitment.urls"
        )
    ),

    path(
        "api/v1/",
        include(
            "apps.assets.urls"
        )
    ),

    path(
        "api/v1/reports/",
        include(
            "apps.reports.urls"
        )
    ),
]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,

        document_root=
            settings.MEDIA_ROOT
    )
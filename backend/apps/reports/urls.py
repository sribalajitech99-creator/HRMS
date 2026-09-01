from django.urls import path

from .views import (
    DashboardView,
    ReportDataView,
)


urlpatterns = [
    path(
        "dashboard/",
        DashboardView.as_view()
    ),

    path(
        "data/",
        ReportDataView.as_view()
    ),
]
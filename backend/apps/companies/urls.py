from rest_framework.routers import DefaultRouter

from .views import (
    CompanySettingViewSet,
    CompanyViewSet,
    DepartmentViewSet,
    DesignationViewSet,
)


router = DefaultRouter()

router.register(
    "companies",
    CompanyViewSet,
    basename="companies"
)

router.register(
    "departments",
    DepartmentViewSet,
    basename="departments"
)

router.register(
    "designations",
    DesignationViewSet,
    basename="designations"
)

router.register(
    "settings",
    CompanySettingViewSet,
    basename="settings"
)


urlpatterns = router.urls
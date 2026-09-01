from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    AttendanceViewSet,
    HolidayViewSet,
    ShiftViewSet,
)


router = DefaultRouter()

router.register(
    "attendance",
    AttendanceViewSet,
    basename="attendance",
)

router.register(
    "shifts",
    ShiftViewSet,
    basename="shifts",
)

router.register(
    "holidays",
    HolidayViewSet,
    basename="holidays",
)


urlpatterns = router.urls
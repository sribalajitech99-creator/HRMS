from rest_framework.routers import DefaultRouter

from .views import (
    JobOpeningViewSet,
    CandidateViewSet,
)


router = DefaultRouter()

router.register(
    "job-openings",
    JobOpeningViewSet,
    basename="job-openings"
)

router.register(
    "candidates",
    CandidateViewSet,
    basename="candidates"
)


urlpatterns = router.urls
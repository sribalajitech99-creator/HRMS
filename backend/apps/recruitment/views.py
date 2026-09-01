from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.models import User
from apps.accounts.permissions import (
    CompanyScopedMixin,
    IsRecruiter,
    visible_company_ids,
)

from .models import (
    Candidate,
    JobOpening,
)

from .serializers import (
    CandidateSerializer,
    JobOpeningSerializer,
)


class JobOpeningViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = (
        JobOpening.objects
        .select_related(
            "company",
            "department"
        )
        .all()
    )

    serializer_class = JobOpeningSerializer

    permission_classes = [
        IsRecruiter
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "company",
        "department",
        "status",
    ]

    search_fields = [
        "job_code",
        "title",
        "description",
    ]

    ordering_fields = [
        "job_code",
        "title",
        "positions",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        ids = self.get_visible_company_ids()

        if ids is not None:
            queryset = queryset.filter(
                company_id__in=ids
            )

        return queryset

    def perform_create(
        self,
        serializer
    ):
        user = self.request.user

        if not (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        ):
            serializer.validated_data["company_id"] = (
                user.company_id
            )

        serializer.save()


class CandidateViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = (
        Candidate.objects
        .select_related(
            "job",
            "job__company",
        )
        .all()
    )

    serializer_class = CandidateSerializer

    permission_classes = [
        IsRecruiter
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "job",
        "stage",
    ]

    search_fields = [
        "name",
        "email",
        "phone",
        "job__title",
        "job__job_code",
    ]

    ordering_fields = [
        "name",
        "experience",
        "stage",
        "applied_on",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        ids = self.get_visible_company_ids()

        if ids is not None:
            queryset = queryset.filter(
                job__company_id__in=ids
            )

        return queryset

    def perform_create(
        self,
        serializer
    ):
        user = self.request.user

        job = serializer.validated_data.get("job")

        if (
            not (
                user.is_superuser
                or user.role == User.Role.SUPER_ADMIN
            )
            and job
            and user.company_id
            and job.company_id != user.company_id
        ):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Cannot add a candidate to a job in "
                "another company."
            )

        serializer.save()
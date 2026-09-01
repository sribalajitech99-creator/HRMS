from django.db.models import Q

from rest_framework import filters
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import (
    CompanyScopedMixin,
    IsHRAdmin,
)

from .models import (
    Company,
    CompanySetting,
    Department,
    Designation,
)

from .serializers import (
    CompanySerializer,
    CompanySettingSerializer,
    DepartmentSerializer,
    DesignationSerializer,
)


class CompanyViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = Company.objects.all()

    serializer_class = CompanySerializer

    permission_classes = [
        IsHRAdmin
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "is_active",
        "country",
        "state",
    ]

    search_fields = [
        "name",
        "code",
        "legal_name",
    ]

    ordering_fields = [
        "name",
        "code",
        "id",
    ]

    ordering = [
        "code",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        ids = self.get_visible_company_ids()

        if ids is not None:
            queryset = queryset.filter(
                id__in=ids
            )

        return queryset

    def perform_create(
        self,
        serializer
    ):
        serializer.save(
            created_by=self.request.user
        )


class DepartmentViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = (
        Department.objects
        .select_related(
            "company"
        )
        .all()
    )

    serializer_class = DepartmentSerializer

    permission_classes = [
        IsHRAdmin
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]

    filterset_fields = [
        "company",
        "is_active",
    ]

    search_fields = [
        "name",
        "code",
        "company__name",
    ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                **self.company_filter_kwargs()
            )
        )


class DesignationViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = (
        Designation.objects
        .select_related(
            "company",
            "department"
        )
        .all()
    )

    serializer_class = DesignationSerializer

    permission_classes = [
        IsHRAdmin
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]

    filterset_fields = [
        "company",
        "department",
        "is_active",
    ]

    search_fields = [
        "name",
        "code",
        "company__name",
    ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                **self.company_filter_kwargs()
            )
        )


class CompanySettingViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = (
        CompanySetting.objects
        .select_related("company")
        .all()
    )

    serializer_class = CompanySettingSerializer

    permission_classes = [
        IsHRAdmin
    ]

    filter_backends = [
        DjangoFilterBackend,
    ]

    filterset_fields = [
        "company",
        "group",
        "key",
    ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                **self.company_filter_kwargs()
            )
        )

    def create(
        self,
        request,
        *args,
        **kwargs
    ):
        data = request.data.copy()

        ids = self.get_visible_company_ids()

        company_id = data.get("company")

        if (
            company_id
            and ids is not None
            and int(company_id) not in ids
        ):
            return Response(
                {
                    "detail":
                        "You cannot save settings "
                        "for this company."
                },
                status=403
            )

        if not company_id:
            data["company"] = request.user.company_id

        serializer = self.get_serializer(
            data=data
        )

        serializer.is_valid(
            raise_exception=True
        )

        CompanySetting.objects.update_or_create(
            company_id=(
                serializer.validated_data["company"].id
            ),
            group=serializer.validated_data["group"],
            key=serializer.validated_data["key"],
            defaults={
                "value":
                    serializer.validated_data.get(
                        "value",
                        ""
                    )
            },
        )

        instance = CompanySetting.objects.filter(
            company=serializer.validated_data["company"],
            group=serializer.validated_data["group"],
            key=serializer.validated_data["key"],
        ).first()

        return Response(
            self.get_serializer(
                instance
            ).data,
            status=201,
        )
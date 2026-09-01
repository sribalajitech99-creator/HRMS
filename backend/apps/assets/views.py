from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.models import User
from apps.accounts.permissions import (
    CompanyScopedMixin,
    IsHRAdmin,
)

from .models import Asset

from .serializers import AssetSerializer


class AssetViewSet(
    CompanyScopedMixin,
    ModelViewSet
):

    queryset = (
        Asset.objects
        .select_related(
            "company",
            "assigned_employee",
        )
        .all()
    )

    serializer_class = AssetSerializer

    permission_classes = [
        IsHRAdmin
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]

    filterset_fields = [
        "company",
        "category",
        "status",
        "assigned_employee",
    ]

    search_fields = [
        "asset_code",
        "category",
        "brand",
        "model",
        "serial_number",
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
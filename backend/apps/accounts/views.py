from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Notification, User

from .permissions import IsCompanyAdmin

from .serializers import (
    ChangePasswordSerializer,
    NotificationSerializer,
    UserCreateSerializer,
    UserSerializer,
)


class CurrentUserView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request
    ):

        return Response({
            "success": True,

            "data":
                UserSerializer(
                    request.user
                ).data,
        })


class ChangePasswordView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request
    ):

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={
                "request": request
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        request.user.set_password(
            serializer.validated_data[
                "new_password"
            ]
        )

        request.user.save(
            update_fields=["password"]
        )

        return Response({
            "success": True,
            "message":
                "Password changed successfully.",
        })


class UserViewSet(ModelViewSet):

    queryset = (
        User.objects
        .select_related("company")
        .all()
    )

    permission_classes = [
        IsCompanyAdmin
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "role",
        "is_active",
        "company",
    ]

    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "company__name",
    ]

    ordering_fields = [
        "username",
        "email",
        "role",
        "date_joined",
    ]

    ordering = [
        "username",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        if not (
            user.is_superuser
            or user.role == "SUPER_ADMIN"
        ):
            queryset = queryset.filter(
                company=user.company
            )

        return queryset

    def get_serializer_class(self):

        if self.action == "create":

            return UserCreateSerializer

        return UserSerializer

    def perform_create(
        self,
        serializer
    ):

        user = self.request.user

        data = {}

        if not (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        ):
            data["company"] = user.company

            serializer.validated_data["role"] = (
                serializer.validated_data.get(
                    "role",
                    User.Role.EMPLOYEE,
                )
                if serializer.validated_data.get(
                    "role"
                ) != User.Role.SUPER_ADMIN
                else User.Role.EMPLOYEE
            )

        serializer.save(
            **data
        )

    def perform_update(
        self,
        serializer
    ):

        user = self.request.user

        if not (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        ):

            serializer.validated_data.pop(
                "role",
                None
            )

            serializer.validated_data["company"] = (
                user.company
            )

        serializer.save()


class NotificationViewSet(ModelViewSet):

    serializer_class = NotificationSerializer

    permission_classes = [
        IsAuthenticated
    ]

    queryset = Notification.objects.all()

    filter_backends = [
        filters.OrderingFilter,
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):

        queryset = (
            Notification.objects
            .filter(
                user=self.request.user
            )
        )

        read = (
            self.request.query_params
            .get("is_read")
        )

        if read in [
            "true",
            "false",
        ]:
            queryset = queryset.filter(
                is_read=(read == "true")
            )

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="unread-count",
    )
    def unread_count(
        self,
        request
    ):
        return Response({
            "count":
                self.get_queryset()
                .filter(
                    is_read=False
                )
                .count(),
        })

    @action(
        detail=True,
        methods=["post"],
        url_path="read",
    )
    def mark_read(
        self,
        request,
        pk=None
    ):

        notification = self.get_object()

        notification.is_read = True

        notification.save(
            update_fields=["is_read"]
        )

        return Response({
            "success": True,
        })

    @action(
        detail=False,
        methods=["post"],
        url_path="read-all",
    )
    def read_all(
        self,
        request
    ):

        self.get_queryset().filter(
            is_read=False
        ).update(
            is_read=True
        )

        return Response({
            "success": True,
        })
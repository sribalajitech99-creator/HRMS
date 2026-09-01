from decimal import Decimal

from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.models import User
from apps.accounts.permissions import (
    CompanyScopedMixin,
    IsHRAdmin,
    IsHRManagerOrReadOnly,
    visible_company_ids,
)
from apps.accounts.services import (
    notify_hr_staff,
    notify_user,
)

from .models import (
    LeaveRequest,
    LeaveType,
)

from .serializers import (
    LeaveRequestSerializer,
    LeaveTypeSerializer,
)


class LeaveTypeViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = (
        LeaveType.objects
        .select_related("company")
        .all()
    )

    serializer_class = LeaveTypeSerializer

    permission_classes = [
        IsHRAdmin
    ]

    filter_backends = [
        DjangoFilterBackend,
    ]

    filterset_fields = [
        "company",
        "is_active",
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

    def perform_update(
        self,
        serializer
    ):
        user = self.request.user

        if not (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        ):
            serializer.validated_data["company_id"] = (
                self.get_object().company_id
            )

        serializer.save()


class LeaveRequestViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = (
        LeaveRequest.objects
        .select_related(
            "employee",
            "employee__company",
            "company",
            "leave_type",
        )
        .all()
    )

    serializer_class = LeaveRequestSerializer

    permission_classes = [
        IsHRManagerOrReadOnly
    ]

    filter_backends = [
        DjangoFilterBackend,
    ]

    filterset_fields = [
        "employee",
        "company",
        "leave_type",
        "status",
    ]

    search_fields = [
        "employee__employee_code",
        "employee__first_name",
        "employee__last_name",
        "reason",
    ]

    ordering_fields = [
        "start_date",
        "created_at",
        "status",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        if (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        ):
            return queryset

        if user.role == User.Role.EMPLOYEE:
            employee = getattr(
                user,
                "employee",
                None,
            )

            if employee:
                return queryset.filter(
                    employee=employee
                )

            return queryset.none()

        ids = visible_company_ids(user)

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
            or user.role in {
                User.Role.COMPANY_ADMIN,
                User.Role.HR_MANAGER,
                User.Role.HR_EXECUTIVE,
            }
        ):
            employee = getattr(
                user,
                "employee",
                None,
            )

            if not employee:
                raise PermissionDenied(
                    "Your account is not linked "
                    "to an employee record."
                )

            serializer.validated_data["employee"] = (
                employee
            )

            serializer.validated_data["status"] = (
                LeaveRequest.Status.PENDING
            )

        instance = serializer.save()

        notify_hr_staff(
            instance.company,
            "New leave request",
            (
                f"{instance.employee.employee_code} "
                f"{instance.employee.first_name} "
                "applied for leave "
                f"{instance.start_date} to "
                f"{instance.end_date} "
                f"({instance.total_days} day(s))."
            ),
            link="/leave",
        )

    def perform_update(
        self,
        serializer
    ):
        user = self.request.user

        instance = self.get_object()

        if user.role == User.Role.EMPLOYEE:
            if instance.status != LeaveRequest.Status.PENDING:
                raise PermissionDenied(
                    "You cannot edit an already "
                    "answered leave request."
                )

            serializer.validated_data["employee"] = (
                instance.employee
            )

        serializer.save()

    def perform_destroy(
        self,
        instance
    ):
        user = self.request.user

        if user.role == User.Role.EMPLOYEE:
            if instance.status != LeaveRequest.Status.PENDING:
                raise PermissionDenied(
                    "You cannot delete an already "
                    "answered leave request."
                )

        instance.delete()

    def _require_hr(
        self,
        request
    ):
        user = request.user

        if not (
            user.is_superuser
            or user.role in {
                User.Role.SUPER_ADMIN,
                User.Role.COMPANY_ADMIN,
                User.Role.HR_MANAGER,
                User.Role.HR_EXECUTIVE,
            }
        ):
            raise PermissionDenied(
                "Only HR can perform this "
                "action."
            )

    @action(
        detail=True,
        methods=["post"]
    )
    def approve(
        self,
        request,
        pk=None
    ):

        self._require_hr(request)

        leave = self.get_object()

        leave.status = LeaveRequest.Status.APPROVED

        leave.approved_by = request.user

        leave.save(
            update_fields=[
                "status",
                "approved_by",
            ]
        )

        employee_user = leave.employee.user

        notify_user(
            employee_user,
            "Leave approved",
            (
                f"{leave.leave_type.name} approved "
                f"for {leave.start_date} to "
                f"{leave.end_date}."
            ),
            link="/leave",
        )

        return Response(
            self.get_serializer(
                leave
            ).data
        )

    @action(
        detail=True,
        methods=["post"]
    )
    def reject(
        self,
        request,
        pk=None
    ):

        self._require_hr(request)

        leave = self.get_object()

        leave.status = LeaveRequest.Status.REJECTED

        leave.approved_by = request.user

        leave.save(
            update_fields=[
                "status",
                "approved_by",
            ]
        )

        notify_user(
            leave.employee.user,
            "Leave rejected",
            (
                f"{leave.leave_type.name} request "
                f"for {leave.start_date} to "
                f"{leave.end_date} was rejected."
            ),
            link="/leave",
        )

        return Response(
            self.get_serializer(
                leave
            ).data
        )

    @action(
        detail=True,
        methods=["post"]
    )
    def cancel(
        self,
        request,
        pk=None
    ):

        leave = self.get_object()

        if leave.status != LeaveRequest.Status.PENDING:
            raise PermissionDenied(
                "Only pending requests can "
                "be cancelled."
            )

        if request.user.role == User.Role.EMPLOYEE:
            employee = getattr(
                request.user,
                "employee",
                None,
            )

            if (
                not employee
                or leave.employee_id != employee.id
            ):
                raise PermissionDenied(
                    "You cannot cancel someone "
                    "else's leave request."
                )

        leave.status = LeaveRequest.Status.CANCELLED

        leave.save(
            update_fields=["status"]
        )

        return Response(
            self.get_serializer(
                leave
            ).data
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="balance",
    )
    def balance(
        self,
        request
    ):

        employee_id = (
            request.query_params.get("employee")
        )

        if (
            not employee_id
            and request.user.role
            == User.Role.EMPLOYEE
        ):
            employee = getattr(
                request.user,
                "employee",
                None,
            )

            if employee:
                employee_id = employee.id

        if not employee_id:
            return Response(
                {
                    "detail":
                        "The 'employee' query "
                        "parameter is required."
                },
                status=400,
            )

        try:
            employee_id = int(employee_id)
        except (TypeError, ValueError):
            return Response(
                {
                    "detail":
                        "Invalid employee id."
                },
                status=400,
            )

        qs = self.get_queryset()

        result = []

        for leave_type in LeaveType.objects.filter(
            company__employees__id=employee_id,
            is_active=True,
        ).distinct():

            allocated = (
                leave_type.annual_allocation
                or Decimal("0.00")
            )

            used = Decimal("0.00")

            approved_sum = (
                LeaveRequest.objects
                .filter(
                    employee_id=employee_id,
                    leave_type=leave_type,
                    status=LeaveRequest.Status.APPROVED,
                )
                .values("total_days")
            )

            used = sum(
                item["total_days"]
                or Decimal("0.00")
                for item in approved_sum
            )

            result.append({
                "leave_type": leave_type.id,
                "leave_type_name": leave_type.name,
                "allocated": allocated,
                "used": round(used, 2),
                "balance": round(
                    allocated - used,
                    2,
                ),
            })

        return Response({
            "success": True,
            "balances": result,
        })
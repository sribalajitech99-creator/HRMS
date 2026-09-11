from django.db import IntegrityError, transaction

from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.models import User
from apps.accounts.permissions import (
    CompanyScopedMixin,
    visible_company_ids,
)

from .models import (
    EmployeeSalary,
    PayrollRun,
    Payslip,
)

from .serializers import (
    EmployeeSalarySerializer,
    PayrollRunSerializer,
    PayslipSerializer,
)

from .services import calculate_payroll_run

from .pdf import payslip_pdf_response, bulk_payslip_zip_response


class PayrollAccess(BasePermission):
    """Employees may read their own payslips; payroll people manage."""

    staff_roles = {
        User.Role.COMPANY_ADMIN,
        User.Role.HR_MANAGER,
        User.Role.HR_EXECUTIVE,
        User.Role.PAYROLL_MANAGER,
        User.Role.ACCOUNTS_MANAGER,
        User.Role.AUDITOR,
    }

    admin_roles = {
        User.Role.SUPER_ADMIN,
        User.Role.COMPANY_ADMIN,
        User.Role.HR_MANAGER,
        User.Role.HR_EXECUTIVE,
        User.Role.PAYROLL_MANAGER,
        User.Role.ACCOUNTS_MANAGER,
    }

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or user.role == User.Role.SUPER_ADMIN:
            return True

        if request.method in ("GET", "HEAD", "OPTIONS"):
            if user.role in self.staff_roles:
                return True

            return hasattr(user, "employee")

        return user.role in self.admin_roles


class EmployeeSalaryViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = (
        EmployeeSalary.objects
        .select_related(
            "employee",
            "employee__company",
        )
        .all()
    )

    serializer_class = EmployeeSalarySerializer

    permission_classes = [
        PayrollAccess
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "employee",
        "is_active",
    ]

    search_fields = [
        "employee__employee_code",
        "employee__first_name",
        "employee__last_name",
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
                employee__company_id__in=ids
            )

        return queryset

    def _deactivate_other_active_records(self, employee_id, exclude_id=None):
        qs = EmployeeSalary.objects.filter(
            employee_id=employee_id,
            is_active=True,
        )

        if exclude_id:
            qs = qs.exclude(pk=exclude_id)

        qs.update(is_active=False)

    @transaction.atomic
    def perform_create(self, serializer):
        data = serializer.validated_data

        employee = data["employee"]

        if data.get("is_active", True):
            self._deactivate_other_active_records(employee.id)

        serializer.save()

    @transaction.atomic
    def perform_update(self, serializer):
        instance = self.get_object()

        data = serializer.validated_data

        if data.get("is_active", instance.is_active):
            self._deactivate_other_active_records(
                instance.employee_id,
                exclude_id=instance.pk,
            )

        serializer.save()


class PayrollRunViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = (
        PayrollRun.objects
        .select_related("company")
        .all()
    )

    serializer_class = PayrollRunSerializer

    permission_classes = [
        PayrollAccess
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "company",
        "year",
        "month",
        "status",
    ]

    ordering_fields = [
        "year",
        "month",
        "created_at",
    ]

    ordering = [
        "-year",
        "-month",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        if not (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        ):
            if user.role == User.Role.EMPLOYEE:
                return PayrollRun.objects.none()

            ids = visible_company_ids(user)

            if ids is not None:
                queryset = queryset.filter(
                    company_id__in=ids
                )

        return queryset

    def perform_create(self, serializer):
        user = self.request.user

        if not (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        ):
            company = serializer.validated_data.get(
                "company",
            )

            if (
                company
                and user.company_id
                and company.id != user.company_id
            ):
                raise PermissionDenied(
                    "You cannot create a payroll "
                    "run for another company."
                )

        try:
            serializer.save()
        except IntegrityError:
            raise PermissionDenied(
                "A payroll run for this company "
                "and period already exists."
            )

    def _finalized(self, payroll):
        return payroll.status in [
            PayrollRun.Status.APPROVED,
            PayrollRun.Status.PAID,
        ]

    def perform_update(self, serializer):
        payroll = self.get_object()

        if self._finalized(payroll):
            raise PermissionDenied(
                "An approved or paid payroll "
                "cannot be modified."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if instance.status == PayrollRun.Status.PAID:
            raise PermissionDenied(
                "A paid payroll cannot be deleted."
            )

        instance.delete()

    @action(
        detail=True,
        methods=["post"]
    )
    @transaction.atomic
    def calculate(self, request, pk=None):
        payroll = self.get_object()

        if payroll.status in [
            PayrollRun.Status.APPROVED,
            PayrollRun.Status.PAID,
        ]:
            return Response(
                {
                    "success": False,
                    "message": (
                        f"Payroll for "
                        f"{payroll.period} is already "
                        f"{payroll.get_status_display().lower()} "
                        "and cannot be recalculated."
                    ),
                },
                status=400,
            )

        count = calculate_payroll_run(payroll)

        return Response({
            "success": True,
            "message": "Payroll calculated successfully",
            "payslip_count": count,
        })

    @action(
        detail=True,
        methods=["post"]
    )
    def approve(self, request, pk=None):
        payroll = self.get_object()

        if payroll.status != PayrollRun.Status.CALCULATED:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Only a calculated payroll "
                        "can be approved."
                    ),
                },
                status=400,
            )

        payroll.status = PayrollRun.Status.APPROVED

        payroll.save(update_fields=["status"])

        return Response({
            "success": True,
            "message": "Payroll approved.",
        })

    @action(
        detail=True,
        methods=["post"],
        url_path="mark-paid",
    )
    def mark_paid(self, request, pk=None):
        payroll = self.get_object()

        if payroll.status not in [
            PayrollRun.Status.CALCULATED,
            PayrollRun.Status.APPROVED,
        ]:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Payroll must be calculated "
                        "before marking paid."
                    ),
                },
                status=400,
            )

        payroll.status = PayrollRun.Status.PAID

        payroll.save(update_fields=["status"])

        return Response({
            "success": True,
            "message": "Payroll marked as paid.",
        })


class PayslipViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    queryset = (
        Payslip.objects
        .select_related(
            "payroll_run",
            "payroll_run__company",
            "employee",
            "employee__department",
            "employee__designation",
        )
        .all()
    )

    serializer_class = PayslipSerializer

    permission_classes = [
        PayrollAccess
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "payroll_run",
        "employee",
    ]

    search_fields = [
        "employee__employee_code",
        "employee__first_name",
        "employee__last_name",
    ]

    ordering_fields = [
        "employee__employee_code",
        "gross_salary",
        "net_salary",
    ]

    http_method_names = [
        "get",
        "post",
        "head",
        "options",
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
                employee__company_id__in=ids
            )

        return queryset

    @action(
        detail=True,
        methods=["get"],
    )
    def pdf(self, request, pk=None):
        payslip = self.get_object()

        user = request.user

        mask_bank = not (
            user.is_superuser
            or user.role in PayrollAccess.staff_roles
        )

        return payslip_pdf_response(
            payslip,
            mask_bank=mask_bank,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-pdf",
    )
    def bulk_pdf(self, request):
        user = request.user

        mask_bank = not (
            user.is_superuser
            or user.role in PayrollAccess.staff_roles
        )

        payroll_run_id = request.data.get("payroll_run")
        payslip_ids = request.data.get("payslip_ids")

        queryset = self.get_queryset()

        if payslip_ids:
            if not isinstance(payslip_ids, list):
                return Response(
                    {
                        "success": False,
                        "message": "payslip_ids must be a list.",
                    },
                    status=400,
                )

            queryset = queryset.filter(
                pk__in=payslip_ids,
            )
        elif payroll_run_id:
            queryset = queryset.filter(
                payroll_run_id=payroll_run_id,
            )

        payslips = list(queryset)

        if not payslips:
            return Response(
                {
                    "success": False,
                    "message": "No payslips found.",
                },
                status=404,
            )

        response = bulk_payslip_zip_response(
            payslips,
            mask_bank=mask_bank,
        )

        if response is None:
            return Response(
                {
                    "success": False,
                    "message": "Failed to generate PDF.",
                },
                status=500,
            )

        return response
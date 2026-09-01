from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.models import User
from apps.accounts.permissions import visible_company_ids

from .models import Employee

from .serializers import EmployeeSerializer


class IsHRAdminOrReadStaff:
    """Allow HR roles to write; all staff (and the employee themself) may read.

    Read access is further restricted in get_queryset so that plain employees
    only ever see their own employee record.
    """

    staff_roles = {
        User.Role.COMPANY_ADMIN,
        User.Role.HR_MANAGER,
        User.Role.HR_EXECUTIVE,
        User.Role.DEPARTMENT_MANAGER,
        User.Role.REPORTING_MANAGER,
        User.Role.PAYROLL_MANAGER,
        User.Role.ACCOUNTS_MANAGER,
        User.Role.RECRUITER,
        User.Role.AUDITOR,
    }

    hr_roles = {
        User.Role.SUPER_ADMIN,
        User.Role.COMPANY_ADMIN,
        User.Role.HR_MANAGER,
        User.Role.HR_EXECUTIVE,
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

        return user.role in self.hr_roles


class EmployeeViewSet(ModelViewSet):
    queryset = (
        Employee.objects
        .select_related(
            "company",
            "department",
            "designation",
            "reporting_manager",
            "user"
        )
        .all()
    )

    serializer_class = EmployeeSerializer

    permission_classes = [
        IsHRAdminOrReadStaff
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "company",
        "department",
        "designation",
        "status",
        "employment_type",
    ]

    search_fields = [
        "employee_code",
        "first_name",
        "last_name",
        "work_email",
        "mobile",
    ]

    ordering_fields = [
        "employee_code",
        "first_name",
        "joining_date",
    ]

    ordering = [
        "employee_code",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        if (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        ):
            return queryset

        if user.role == User.Role.DEPARTMENT_MANAGER:
            department = getattr(
                getattr(user, "employee", None),
                "department_id",
                None,
            )

            ids = visible_company_ids(user)

            scoped = queryset

            if ids is not None:
                scoped = scoped.filter(
                    company_id__in=ids
                )

            if department:
                scoped = scoped.filter(
                    department_id=department
                )

            return scoped

        if user.role == User.Role.EMPLOYEE:
            employee = getattr(
                user,
                "employee",
                None,
            )

            if employee:
                return queryset.filter(
                    pk=employee.pk
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
                user.company_id
            )

        serializer.save()
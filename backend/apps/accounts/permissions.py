from rest_framework.permissions import BasePermission

from .models import User


def user_has_global_access(user):
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        )
    )


def visible_company_ids(user):
    """Return None for global access, a list of company ids otherwise.

    Non-superusers are restricted to their assigned company. A user with no
    company assigned has no company access (empty list) to prevent cross-company
    data leakage.
    """
    if not user or not user.is_authenticated:
        return []

    if user_has_global_access(user):
        return None

    if user.company_id:
        return [user.company_id]

    return []


class CompanyScopedMixin:
    """Mixin that scopes querysets to the requesting user's company."""

    def get_visible_company_ids(self):
        return visible_company_ids(self.request.user)

    def company_filter_kwargs(self):
        ids = self.get_visible_company_ids()
        if ids is None:
            return {}
        return {"company_id__in": ids}

    def employee_company_filter_kwargs(self):
        ids = self.get_visible_company_ids()
        if ids is None:
            return {}
        return {"employee__company_id__in": ids}

    def user_company_filter_kwargs(self):
        ids = self.get_visible_company_ids()
        if ids is None:
            return {}
        return {"company_id__in": ids}


class IsSuperAdmin(BasePermission):

    def has_permission(
        self,
        request,
        view
    ):

        return user_has_global_access(request.user)


class IsCompanyAdmin(BasePermission):

    allowed_roles = {
        "SUPER_ADMIN",
        "COMPANY_ADMIN",
    }


    def has_permission(
        self,
        request,
        view
    ):

        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or
                user.role in self.allowed_roles
            )
        )


class IsHRAdmin(BasePermission):

    allowed_roles = {
        "SUPER_ADMIN",
        "COMPANY_ADMIN",
        "HR_MANAGER",
        "HR_EXECUTIVE",
    }


    def has_permission(
        self,
        request,
        view
    ):

        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or
                user.role in self.allowed_roles
            )
        )


class IsPayrollAdmin(BasePermission):

    allowed_roles = {
        "SUPER_ADMIN",
        "COMPANY_ADMIN",
        "HR_MANAGER",
        "HR_EXECUTIVE",
        "PAYROLL_MANAGER",
        "ACCOUNTS_MANAGER",
    }


    def has_permission(
        self,
        request,
        view
    ):

        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or
                user.role in self.allowed_roles
            )
        )


class IsRecruiter(BasePermission):

    allowed_roles = {
        "SUPER_ADMIN",
        "COMPANY_ADMIN",
        "HR_MANAGER",
        "HR_EXECUTIVE",
        "RECRUITER",
    }


    def has_permission(
        self,
        request,
        view
    ):

        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or
                user.role in self.allowed_roles
            )
        )


class IsHRManagerOrReadOnly(BasePermission):
    """Write access for HR roles; read access for any authenticated user.

    Read scoping to a user's own records is implemented in each view queryset.
    """

    hr_roles = {
        "SUPER_ADMIN",
        "COMPANY_ADMIN",
        "HR_MANAGER",
        "HR_EXECUTIVE",
    }


    def has_permission(
        self,
        request,
        view
    ):

        user = request.user

        if (
            not user
            or not user.is_authenticated
        ):
            return False

        if (
            user.is_superuser
            or user.role == "SUPER_ADMIN"
        ):
            return True

        if request.method in (
            "GET",
            "HEAD",
            "OPTIONS",
        ):
            return True

        return user.role in self.hr_roles


class IsOperationsAccess(BasePermission):
    """Attendance / shift / holiday / employee read access.

    Non-HR staff with a company get full access; plain employees only get
    access to their own records which is enforced in the view queryset.
    """

    allowed_roles = {
        "SUPER_ADMIN",
        "COMPANY_ADMIN",
        "HR_MANAGER",
        "HR_EXECUTIVE",
        "DEPARTMENT_MANAGER",
        "REPORTING_MANAGER",
        "PAYROLL_MANAGER",
        "ACCOUNTS_MANAGER",
        "RECRUITER",
        "AUDITOR",
    }


    def has_permission(
        self,
        request,
        view
    ):

        user = request.user

        if (
            not user
            or not user.is_authenticated
        ):
            return False

        if (
            user.is_superuser
            or user.role == "SUPER_ADMIN"
        ):
            return True

        return user.role in self.allowed_roles
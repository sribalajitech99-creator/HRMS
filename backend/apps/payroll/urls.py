from rest_framework.routers import DefaultRouter

from .views import (
    EmployeeSalaryViewSet,
    PayrollRunViewSet,
    PayslipViewSet,
)


router = DefaultRouter()

router.register(
    "employee-salaries",
    EmployeeSalaryViewSet,
    basename="employee-salaries"
)

router.register(
    "payroll-runs",
    PayrollRunViewSet,
    basename="payroll-runs"
)

router.register(
    "payslips",
    PayslipViewSet,
    basename="payslips"
)


urlpatterns = router.urls
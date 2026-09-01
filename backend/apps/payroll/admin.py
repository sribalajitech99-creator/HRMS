from django.contrib import admin

from .models import (
    EmployeeSalary,
    PayrollRun,
    Payslip,
)


admin.site.register(
    EmployeeSalary
)

admin.site.register(
    PayrollRun
)

admin.site.register(
    Payslip
)


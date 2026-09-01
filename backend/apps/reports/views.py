from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOperationsAccess
from apps.companies.models import Company
from apps.employees.models import Employee
from apps.attendance.models import Attendance
from apps.leave_management.models import (
    LeaveRequest,
)
from apps.payroll.models import (
    PayrollRun,
    Payslip,
)
from apps.recruitment.models import (
    JobOpening,
    Candidate,
)
from apps.assets.models import Asset

from .data import REPORTS
from .utils import (
    build_pdf_response,
    build_xlsx_response,
    excel_filename,
    pdf_filename,
)


class DashboardView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        today = timezone.localdate()

        company_id = request.query_params.get(
            "company"
        )

        employees = Employee.objects.all()

        attendance = Attendance.objects.all()

        leaves = LeaveRequest.objects.all()

        payroll = Payslip.objects.all()

        jobs = JobOpening.objects.all()

        candidates = Candidate.objects.all()

        assets = Asset.objects.all()

        if company_id:

            employees = employees.filter(
                company_id=company_id
            )

            attendance = attendance.filter(
                employee__company_id=company_id
            )

            leaves = leaves.filter(
                employee__company_id=company_id
            )

            payroll = payroll.filter(
                employee__company_id=company_id
            )

            jobs = jobs.filter(
                company_id=company_id
            )

            candidates = candidates.filter(
                job__company_id=company_id
            )

            assets = assets.filter(
                company_id=company_id
            )

        active_employees = employees.filter(
            status="ACTIVE"
        )

        today_attendance = attendance.filter(
            date=today
        )

        present_today = (
            today_attendance
            .filter(
                status="PRESENT"
            )
            .count()
        )

        absent_today = (
            today_attendance
            .filter(
                status="ABSENT"
            )
            .count()
        )

        on_leave_today = (
            leaves
            .filter(
                status="APPROVED",
                start_date__lte=today,
                end_date__gte=today,
            )
            .count()
        )

        total_active = (
            active_employees.count()
        )

        attendance_rate = 0

        if total_active:

            attendance_rate = round(
                (
                    present_today
                    / total_active
                )
                * 100,
                2
            )

        current_payroll = (
            payroll
            .filter(
                payroll_run__year=today.year,
                payroll_run__month=today.month,
            )
        )

        payroll_values = (
            current_payroll.aggregate(
                gross=Sum(
                    "gross_salary"
                ),
                overtime=Sum(
                    "overtime_amount"
                ),
                deductions=Sum(
                    "deductions"
                ),
                net=Sum(
                    "net_salary"
                ),
            )
        )

        department_distribution = list(
            employees
            .values(
                "department__name"
            )
            .annotate(
                total=Count("id")
            )
            .order_by("-total")[:10]
        )

        company_distribution = list(
            employees
            .values(
                "company__id",
                "company__name",
                "company__code",
            )
            .annotate(
                total=Count("id")
            )
            .order_by("-total")
        )

        attendance_trend = []

        for offset in range(
            6,
            -1,
            -1
        ):

            day = today - timedelta(
                days=offset
            )

            records = attendance.filter(
                date=day
            )

            attendance_trend.append({
                "date":
                    day.strftime(
                        "%d %b"
                    ),

                "present":
                    records.filter(
                        status="PRESENT"
                    ).count(),

                "absent":
                    records.filter(
                        status="ABSENT"
                    ).count(),

                "on_leave":
                    records.filter(
                        status="ON_LEAVE"
                    ).count(),
            })

        latest_attendance = (
            attendance
            .select_related(
                "employee"
            )
            .order_by(
                "-date",
                "-id"
            )[:8]
        )

        recent_activity = []

        for item in latest_attendance:

            recent_activity.append({
                "employee_code":
                    item.employee.employee_code,

                "employee_name":
                    (
                        f"{item.employee.first_name} "
                        f"{item.employee.last_name}"
                    ).strip(),

                "activity":
                    item.status,

                "date":
                    item.date,
            })

        company_count = (
            Company.objects
            .filter(
                is_active=True
            )
            .count()
        )

        department_count = (
            Employee.objects
            .filter(
                company__is_active=True
            )
            .exclude(
                department_id=None
            )
            .values("department_id")
            .distinct()
            .count()
        )

        data = {

            "workforce": {
                "total":
                    employees.count(),

                "active":
                    total_active,

                "probation":
                    employees.filter(
                        status="PROBATION"
                    ).count(),

                "notice":
                    employees.filter(
                        status="NOTICE"
                    ).count(),
            },

            "attendance": {
                "present":
                    present_today,

                "absent":
                    absent_today,

                "late": 0,

                "on_leave":
                    on_leave_today,

                "rate":
                    attendance_rate,
            },

            "leave": {
                "pending":
                    leaves.filter(
                        status="PENDING"
                    ).count(),

                "approved_today":
                    leaves.filter(
                        status="APPROVED",
                        start_date=today,
                    ).count(),
            },

            "payroll": {
                "gross":
                    payroll_values[
                        "gross"
                    ] or 0,

                "overtime":
                    payroll_values[
                        "overtime"
                    ] or 0,

                "deductions":
                    payroll_values[
                        "deductions"
                    ] or 0,

                "net":
                    payroll_values[
                        "net"
                    ] or 0,
            },

            "recruitment": {
                "open_jobs":
                    jobs.filter(
                        status="OPEN"
                    ).count(),

                "candidates":
                    candidates.count(),

                "interviews":
                    candidates.filter(
                        stage="INTERVIEW"
                    ).count(),

                "selected":
                    candidates.filter(
                        stage="SELECTED"
                    ).count(),
            },

            "assets": {
                "total":
                    assets.count(),

                "available":
                    assets.filter(
                        status="AVAILABLE"
                    ).count(),

                "assigned":
                    assets.filter(
                        status="ASSIGNED"
                    ).count(),
            },

            "summary": {
                "employees":
                    employees.count(),

                "companies":
                    company_count,

                "departments":
                    department_count,

                "present_today":
                    present_today,

                "absent_today":
                    absent_today,

                "on_leave_today":
                    on_leave_today,
            },

            "companies":
                Company.objects
                .filter(
                    is_active=True
                )
                .values(
                    "id",
                    "name",
                    "code"
                ),

            "department_distribution":
                department_distribution,

            "company_distribution":
                company_distribution,

            "attendance_trend":
                attendance_trend,

            "recent_activity":
                recent_activity,
        }

        return Response(data)


class ReportDataView(APIView):

    permission_classes = [
        IsOperationsAccess
    ]

    def _company_label(self, request):
        user = request.user

        if user.company_id:
            return user.company.name

        company = (
            Company.objects
            .filter(
                is_active=True
            )
            .first()
        )

        return (
            company.name
            if company
            else "HRMS"
        )

    def get(self, request):

        report_key = request.query_params.get(
            "report"
        )

        if not report_key:
            return Response(
                {
                    "detail":
                        "The 'report' query parameter "
                        "is required."
                },
                status=400,
            )

        function = REPORTS.get(
            report_key
        )

        if not function:
            return Response(
                {
                    "detail":
                        f"Unknown report: {report_key}"
                },
                status=400,
            )

        result = function(
            request.query_params,
            request.user,
        )

        if result is None:
            return Response(
                {
                    "detail":
                        "Required filters are missing "
                        "for this report."
                },
                status=400,
            )

        export = request.query_params.get(
            "export"
        )

        filename_slug = report_key

        if export == "xlsx":
            return build_xlsx_response(
                result["columns"],
                result["rows"],
                result["title"],
                filename=excel_filename(
                    filename_slug
                ),
            )

        if export == "pdf":
            return build_pdf_response(
                self._company_label(request),
                result["title"],
                result["period"],
                result["columns"],
                result["rows"],
                filename=pdf_filename(
                    filename_slug
                ),
            )

        return Response({
            "success": True,
            "report": report_key,
            "title": result["title"],
            "period": result["period"],
            "columns": result["columns"],
            "rows": result["rows"],
            "totals": result.get("totals", {}),
        })
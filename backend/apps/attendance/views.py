from datetime import date as date_cls
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.models import User
from apps.accounts.permissions import (
    CompanyScopedMixin,
    IsHRManagerOrReadOnly,
    visible_company_ids,
)
from apps.employees.models import Employee

from .models import (
    Attendance,
    Holiday,
    Shift,
)

from .serializers import (
    AttendanceSerializer,
    HolidaySerializer,
    ShiftSerializer,
)


class ScopedHolidayShiftMixin(
    CompanyScopedMixin
):

    permission_classes = [
        IsHRManagerOrReadOnly
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


class ShiftViewSet(
    ScopedHolidayShiftMixin,
    ModelViewSet
):
    serializer_class = ShiftSerializer

    queryset = (
        Shift.objects
        .select_related("company")
        .all()
    )

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "company",
        "is_active",
        "is_night_shift",
    ]

    search_fields = [
        "name",
        "code",
        "company__name",
        "company__code",
    ]

    ordering_fields = [
        "name",
        "code",
        "start_time",
    ]

    ordering = [
        "company",
        "start_time",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        active = (
            self.request
            .query_params
            .get("is_active")
        )

        if active in [
            "true",
            "false",
        ]:
            queryset = queryset.filter(
                is_active=(
                    active == "true"
                )
            )

        return queryset


class HolidayViewSet(
    ScopedHolidayShiftMixin,
    ModelViewSet
):
    serializer_class = HolidaySerializer

    queryset = (
        Holiday.objects
        .select_related("company")
        .all()
    )

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "company",
        "is_active",
        "holiday_type",
    ]

    search_fields = [
        "name",
        "company__name",
        "company__code",
    ]

    ordering_fields = [
        "date",
        "name",
    ]

    ordering = ["date"]

    def get_queryset(self):
        queryset = super().get_queryset()

        params = self.request.query_params

        year = params.get("year")
        month = params.get("month")

        if year:
            queryset = queryset.filter(
                date__year=year
            )

        if month:
            queryset = queryset.filter(
                date__month=month
            )

        return queryset


class AttendanceViewSet(
    CompanyScopedMixin,
    ModelViewSet
):
    serializer_class = AttendanceSerializer

    queryset = (
        Attendance.objects
        .select_related(
            "employee",
            "employee__department",
            "employee__designation",
            "company",
            "shift",
            "holiday",
        )
        .all()
    )

    permission_classes = [
        IsHRManagerOrReadOnly
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "employee",
        "company",
        "date",
        "status",
        "shift",
    ]

    search_fields = [
        "employee__employee_code",
        "employee__first_name",
        "employee__last_name",
        "remarks",
    ]

    ordering_fields = [
        "date",
        "employee__employee_code",
        "working_hours",
        "approved_ot_hours",
    ]

    ordering = [
        "-date",
        "employee__employee_code",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        params = self.request.query_params

        if (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        ):
            pass
        elif user.role == User.Role.EMPLOYEE:
            employee = getattr(
                user,
                "employee",
                None,
            )

            if employee:
                queryset = queryset.filter(
                    employee=employee
                )
            else:
                return queryset.none()
        else:
            ids = visible_company_ids(user)

            if ids is not None:
                queryset = queryset.filter(
                    company_id__in=ids
                )

        year = params.get("year")
        month = params.get("month")

        if year:
            queryset = queryset.filter(
                date__year=year
            )

        if month:
            queryset = queryset.filter(
                date__month=month
            )

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="summary",
    )
    def summary(self, request):
        params = request.query_params

        employee_id = params.get("employee")
        year = int(params.get("year", date_cls.today().year))
        month = int(params.get("month", date_cls.today().month))

        qs = self.get_queryset()

        if employee_id:
            qs = qs.filter(
                employee_id=employee_id
            )

        qs = qs.filter(
            date__year=year,
            date__month=month,
        )

        rows = list(qs)

        present = sum(
            1 for r in rows
            if r.status == Attendance.Status.PRESENT
        )

        absent = sum(
            1 for r in rows
            if r.status == Attendance.Status.ABSENT
        )

        leave = sum(
            1 for r in rows
            if r.status == Attendance.Status.ON_LEAVE
        )

        half_day = sum(
            1 for r in rows
            if r.status == Attendance.Status.HALF_DAY
        )

        holiday = sum(
            1 for r in rows
            if r.status == Attendance.Status.HOLIDAY
        )

        week_off = sum(
            1 for r in rows
            if r.status == Attendance.Status.WEEK_OFF
        )

        working_hours = sum(
            (r.working_hours or Decimal("0.00"))
            for r in rows
        )

        calculated_ot = sum(
            (r.calculated_ot_hours or Decimal("0.00"))
            for r in rows
        )

        approved_ot = sum(
            (r.approved_ot_hours or Decimal("0.00"))
            for r in rows
        )

        return Response({
            "success": True,
            "year": year,
            "month": month,
            "summary": {
                "present_days": present,
                "absent_days": absent,
                "leave_days": leave,
                "half_days": half_day,
                "holiday_days": holiday,
                "week_off_days": week_off,
                "working_hours": round(working_hours, 2),
                "calculated_ot_hours": round(calculated_ot, 2),
                "approved_ot_hours": round(approved_ot, 2),
            },
        })

    @action(
        detail=False,
        methods=["get"],
        url_path="daily",
    )
    def daily(self, request):
        params = request.query_params

        raw_date = params.get("date")
        company_id = params.get("company")
        department_id = params.get("department")

        if not raw_date:
            return Response(
                {
                    "detail":
                        "The 'date' query parameter "
                        "is required."
                },
                status=400,
            )

        try:
            day = date_cls.fromisoformat(raw_date)
        except ValueError:
            return Response(
                {
                    "detail":
                        "Invalid date format. "
                        "Use YYYY-MM-DD."
                },
                status=400,
            )

        employees = Employee.objects.select_related(
            "department",
            "designation",
            "company",
        ).filter(
            status__in=[
                Employee.Status.ACTIVE,
                Employee.Status.PROBATION,
                Employee.Status.NOTICE,
            ]
        )

        ids = self.get_visible_company_ids()

        if ids is not None:
            employees = employees.filter(
                company_id__in=ids
            )

        if company_id:
            employees = employees.filter(
                company_id=company_id
            )

        if department_id:
            employees = employees.filter(
                department_id=department_id
            )

        attendance_map = {
            rec.employee_id: rec
            for rec in Attendance.objects.filter(
                date=day,
                employee_id__in=employees.values_list(
                    "id",
                    flat=True
                ),
            )
        }

        rows = []

        for employee in employees:
            rec = attendance_map.get(
                employee.id
            )

            rows.append({
                "employee_id": employee.id,
                "employee_code": employee.employee_code,
                "employee_name":
                    (
                        f"{employee.first_name} "
                        f"{employee.last_name}"
                    ).strip(),
                "department_name":
                    (
                        employee.department.name
                        if employee.department
                        else None
                    ),
                "designation_name":
                    (
                        employee.designation.name
                        if employee.designation
                        else None
                    ),
                "company_id": employee.company_id,
                "status":
                    rec.status
                    if rec
                    else None,
                "shift":
                    rec.shift_id
                    if rec
                    else None,
                "shift_name":
                    rec.shift.name
                    if rec and rec.shift
                    else None,
                "check_in_time":
                    rec.check_in_time
                    if rec
                    else None,
                "check_out_time":
                    rec.check_out_time
                    if rec
                    else None,
                "check_out_next_day":
                    rec.check_out_next_day
                    if rec
                    else False,
                "working_hours":
                    rec.working_hours
                    if rec
                    else "0.00",
                "approved_ot_hours":
                    rec.approved_ot_hours
                    if rec
                    else "0.00",
                "remarks":
                    rec.remarks
                    if rec
                    else "",
                "attendance_id":
                    rec.id
                    if rec
                    else None,
            })

        return Response({
            "success": True,
            "date": day,
            "rows": rows,
            "total": len(rows),
        })

    @action(
        detail=False,
        methods=["post"],
        url_path="bulk",
    )
    @transaction.atomic
    def bulk(self, request):
        data = request.data

        raw_date = data.get("date")
        records = data.get("records") or []

        if not raw_date:
            return Response(
                {
                    "detail":
                        "The 'date' field is required."
                },
                status=400,
            )

        try:
            day = date_cls.fromisoformat(raw_date)
        except (ValueError, TypeError):
            return Response(
                {
                    "detail":
                        "Invalid date format. "
                        "Use YYYY-MM-DD."
                },
                status=400,
            )

        user = self.request.user

        if not isinstance(records, list) or not records:
            return Response(
                {
                    "detail":
                        "Provide a non-empty 'records' list."
                },
                status=400,
            )

        holidays = {
            h.id: h
            for h in Holiday.objects.filter(
                date=day,
            )
        }

        created = 0
        updated = 0
        errors = []

        ids = self.get_visible_company_ids()

        for index, item in enumerate(records):
            employee_id = item.get("employee")
            status_value = item.get("status")

            if not employee_id:
                errors.append({
                    "row": index,
                    "employee": None,
                    "message":
                        "Employee is required.",
                })
                continue

            employee = (
                Employee.objects
                .filter(pk=employee_id)
                .first()
            )

            if not employee:
                errors.append({
                    "row": index,
                    "employee": employee_id,
                    "message":
                        "Employee not found.",
                })
                continue

            if (
                ids is not None
                and employee.company_id not in ids
            ):
                errors.append({
                    "row": index,
                    "employee": employee_id,
                    "message":
                        "Employee not in your company.",
                })
                continue

            try:
                shift = None

                shift_id = item.get("shift")

                if shift_id:
                    shift = Shift.objects.filter(
                        pk=shift_id,
                        company=employee.company,
                    ).first()

                defaults = {
                    "status":
                        status_value
                        or Attendance.Status.PRESENT,
                    "shift": shift,
                    "check_in_time":
                        item.get("check_in_time") or None,
                    "check_out_time":
                        item.get("check_out_time") or None,
                    "check_out_next_day":
                        bool(
                            item.get(
                                "check_out_next_day",
                                False,
                            )
                        ),
                    "approved_ot_hours":
                        Decimal(
                            str(
                                item.get(
                                    "approved_ot_hours",
                                    "0",
                                )
                            )
                            or "0"
                        ),
                    "holiday":
                        holidays.get(
                            employee.company_id
                        ),
                    "remarks":
                        item.get("remarks", ""),
                }

                _, was_created = (
                    Attendance.objects
                    .update_or_create(
                        employee=employee,
                        date=day,
                        defaults=defaults,
                    )
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

            except Exception as exc:
                errors.append({
                    "row": index,
                    "employee": employee_id,
                    "message": str(exc),
                })

        return Response({
            "success": True,
            "message": (
                "Bulk attendance saved: "
                f"{created} created, {updated} updated."
            ),
            "created": created,
            "updated": updated,
            "errors": errors,
        })

    def perform_create(
        self,
        serializer
    ):
        user = self.request.user

        if not (
            user.is_superuser
            or user.role == User.Role.SUPER_ADMIN
        ):
            employee = serializer.validated_data.get(
                "employee"
            )

            if (
                employee
                and user.company_id
                and employee.company_id != user.company_id
            ):
                from rest_framework.exceptions import ValidationError
                raise ValidationError(
                    {
                        "employee":
                            "Employee does not belong "
                            "to your company."
                    }
                )

        serializer.save()
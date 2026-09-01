from decimal import Decimal

import django.db.models.deletion
import django.utils.timezone

from django.db import migrations, models


def migrate_old_attendance_data(
    apps,
    schema_editor,
):
    Attendance = apps.get_model(
        "attendance",
        "Attendance",
    )

    Shift = apps.get_model(
        "attendance",
        "Shift",
    )

    # -----------------------------------------
    # GENERATE CODES FOR EXISTING SHIFTS
    # -----------------------------------------

    for shift in Shift.objects.all():
        base_code = (
            shift.name
            .upper()
            .replace(" ", "-")
            .replace("_", "-")
        )[:20]

        code = base_code

        number = 1

        while Shift.objects.filter(
            company_id=shift.company_id,
            code=code,
        ).exclude(
            pk=shift.pk
        ).exists():
            number += 1

            code = (
                f"{base_code[:15]}"
                f"-{number}"
            )

        shift.code = code

        shift.save(
            update_fields=[
                "code"
            ]
        )

    # -----------------------------------------
    # PRESERVE OLD ATTENDANCE
    # -----------------------------------------

    status_map = {
        "PRESENT": "PRESENT",
        "ABSENT": "ABSENT",
        "HALF_DAY": "HALF_DAY",

        "PAID_LEAVE": "ON_LEAVE",
        "UNPAID_LEAVE": "ON_LEAVE",

        "WEEKLY_OFF": "WEEK_OFF",

        "HOLIDAY": "HOLIDAY",

        "WFH": "PRESENT",
        "ON_DUTY": "PRESENT",
        "LATE": "PRESENT",
    }

    for record in Attendance.objects.select_related(
        "employee"
    ).all():

        if record.employee_id:
            record.company_id = (
                record.employee.company_id
            )

        if record.clock_in:
            record.check_in_time = (
                record.clock_in.time()
            )

        if record.clock_out:
            record.check_out_time = (
                record.clock_out.time()
            )

            if (
                record.clock_in
                and record.clock_out.date()
                > record.clock_in.date()
            ):
                record.check_out_next_day = True

        record.working_hours = (
            Decimal(
                str(
                    record.total_minutes
                    or 0
                )
            )
            / Decimal("60")
        )

        old_ot_hours = (
            Decimal(
                str(
                    record.overtime_minutes
                    or 0
                )
            )
            / Decimal("60")
        )

        record.calculated_ot_hours = (
            old_ot_hours
        )

        record.approved_ot_hours = (
            old_ot_hours
        )

        record.status = (
            status_map.get(
                record.status,
                "PRESENT",
            )
        )

        record.save(
            update_fields=[
                "company",
                "check_in_time",
                "check_out_time",
                "check_out_next_day",
                "working_hours",
                "calculated_ot_hours",
                "approved_ot_hours",
                "status",
            ]
        )


def reverse_data_migration(
    apps,
    schema_editor,
):
    pass


class Migration(
    migrations.Migration
):

    dependencies = [
        (
            "attendance",
            "0001_initial",
        ),
        (
            "companies",
            "0002_remove_branch_unique_branch_code_per_company_and_more",
        ),
        (
            "employees",
            "0002_remove_employee_branch",
        ),
    ]

    operations = [

        # ==========================================
        # HOLIDAY
        # ==========================================

        migrations.CreateModel(
            name="Holiday",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=150
                    ),
                ),
                (
                    "date",
                    models.DateField(),
                ),
                (
                    "holiday_type",
                    models.CharField(
                        choices=[
                            (
                                "NATIONAL",
                                "National Holiday",
                            ),
                            (
                                "STATE",
                                "State Holiday",
                            ),
                            (
                                "FESTIVAL",
                                "Festival Holiday",
                            ),
                            (
                                "COMPANY",
                                "Company Holiday",
                            ),
                            (
                                "OPTIONAL",
                                "Optional Holiday",
                            ),
                        ],
                        default="COMPANY",
                        max_length=20,
                    ),
                ),
                (
                    "is_optional",
                    models.BooleanField(
                        default=False
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="holidays",
                        to="companies.company",
                    ),
                ),
            ],
            options={
                "ordering": [
                    "date",
                    "name",
                ],
            },
        ),

        migrations.AddConstraint(
            model_name="holiday",
            constraint=models.UniqueConstraint(
                fields=(
                    "company",
                    "date",
                    "name",
                ),
                name="unique_company_holiday",
            ),
        ),

        # ==========================================
        # SHIFT
        # ==========================================

        migrations.AddField(
            model_name="shift",
            name="code",
            field=models.CharField(
                max_length=30,
                null=True,
            ),
        ),

        migrations.AddField(
            model_name="shift",
            name="description",
            field=models.CharField(
                blank=True,
                default="",
                max_length=255,
            ),
        ),

        migrations.AddField(
            model_name="shift",
            name="is_night_shift",
            field=models.BooleanField(
                default=False
            ),
        ),

        migrations.AddField(
            model_name="shift",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name="shift",
            name="updated_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),

        migrations.AlterField(
            model_name="shift",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="shifts",
                to="companies.company",
            ),
        ),

        migrations.AlterField(
            model_name="shift",
            name="name",
            field=models.CharField(
                max_length=120
            ),
        ),

        # ==========================================
        # ATTENDANCE NEW FIELDS
        # ==========================================

        migrations.AddField(
            model_name="attendance",
            name="company",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="attendance_records",
                to="companies.company",
            ),
        ),

        migrations.AddField(
            model_name="attendance",
            name="holiday",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="attendance_records",
                to="attendance.holiday",
            ),
        ),

        migrations.AddField(
            model_name="attendance",
            name="check_in_time",
            field=models.TimeField(
                null=True,
                blank=True,
            ),
        ),

        migrations.AddField(
            model_name="attendance",
            name="check_out_time",
            field=models.TimeField(
                null=True,
                blank=True,
            ),
        ),

        migrations.AddField(
            model_name="attendance",
            name="check_out_next_day",
            field=models.BooleanField(
                default=False
            ),
        ),

        migrations.AddField(
            model_name="attendance",
            name="working_hours",
            field=models.DecimalField(
                max_digits=7,
                decimal_places=2,
                default=Decimal("0.00"),
            ),
        ),

        migrations.AddField(
            model_name="attendance",
            name="calculated_ot_hours",
            field=models.DecimalField(
                max_digits=7,
                decimal_places=2,
                default=Decimal("0.00"),
            ),
        ),

        migrations.AddField(
            model_name="attendance",
            name="approved_ot_hours",
            field=models.DecimalField(
                max_digits=7,
                decimal_places=2,
                default=Decimal("0.00"),
            ),
        ),

        migrations.AddField(
            model_name="attendance",
            name="worked_on_holiday",
            field=models.BooleanField(
                default=False
            ),
        ),

        migrations.AddField(
            model_name="attendance",
            name="worked_on_week_off",
            field=models.BooleanField(
                default=False
            ),
        ),

        migrations.AddField(
            model_name="attendance",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name="attendance",
            name="updated_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),

        # ==========================================
        # COPY OLD DATA INTO NEW FIELDS
        # ==========================================

        migrations.RunPython(
            migrate_old_attendance_data,
            reverse_data_migration,
        ),

        # ==========================================
        # NOW COMPANY CAN SAFELY BE REQUIRED
        # ==========================================

        migrations.AlterField(
            model_name="attendance",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="attendance_records",
                to="companies.company",
            ),
        ),

        migrations.AlterField(
            model_name="attendance",
            name="employee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="attendance_records",
                to="employees.employee",
            ),
        ),

        migrations.AlterField(
            model_name="attendance",
            name="shift",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="attendance_records",
                to="attendance.shift",
            ),
        ),

        migrations.AlterField(
            model_name="attendance",
            name="status",
            field=models.CharField(
                choices=[
                    (
                        "PRESENT",
                        "Present",
                    ),
                    (
                        "ABSENT",
                        "Absent",
                    ),
                    (
                        "ON_LEAVE",
                        "On Leave",
                    ),
                    (
                        "HALF_DAY",
                        "Half Day",
                    ),
                    (
                        "HOLIDAY",
                        "Holiday",
                    ),
                    (
                        "WEEK_OFF",
                        "Week Off",
                    ),
                ],
                default="PRESENT",
                max_length=20,
            ),
        ),

        # ==========================================
        # REMOVE OLD FIELDS
        # ==========================================

        migrations.RemoveField(
            model_name="attendance",
            name="clock_in",
        ),

        migrations.RemoveField(
            model_name="attendance",
            name="clock_out",
        ),

        migrations.RemoveField(
            model_name="attendance",
            name="total_minutes",
        ),

        migrations.RemoveField(
            model_name="attendance",
            name="overtime_minutes",
        ),

        migrations.RemoveField(
            model_name="attendance",
            name="late_minutes",
        ),

        migrations.RemoveField(
            model_name="shift",
            name="grace_minutes",
        ),

        migrations.RemoveField(
            model_name="shift",
            name="minimum_work_minutes",
        ),

        # ==========================================
        # FINAL SHIFT CODE
        # ==========================================

        migrations.AlterField(
            model_name="shift",
            name="code",
            field=models.CharField(
                max_length=30
            ),
        ),

        migrations.AddConstraint(
            model_name="shift",
            constraint=models.UniqueConstraint(
                fields=(
                    "company",
                    "code",
                ),
                name="unique_shift_code_per_company",
            ),
        ),

        # ==========================================
        # INDEXES
        # ==========================================

        migrations.AddIndex(
            model_name="attendance",
            index=models.Index(
                fields=[
                    "company",
                    "date",
                ],
                name="attendance_company_date_idx",
            ),
        ),

        migrations.AddIndex(
            model_name="attendance",
            index=models.Index(
                fields=[
                    "employee",
                    "date",
                ],
                name="attendance_employee_date_idx",
            ),
        ),
    ]
    
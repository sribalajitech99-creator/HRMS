import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payroll", "0002_alter_employeesalary_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeesalary",
            name="bonus",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=12,
            ),
        ),
        migrations.AddField(
            model_name="payslip",
            name="bonus",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=12,
            ),
        ),
        migrations.RemoveField(
            model_name="employeesalary",
            name="hra",
        ),
        migrations.RemoveField(
            model_name="employeesalary",
            name="allowance",
        ),
        migrations.RemoveField(
            model_name="payslip",
            name="hra",
        ),
        migrations.RemoveField(
            model_name="payslip",
            name="allowance",
        ),
    ]

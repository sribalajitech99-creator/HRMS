from django.db import models
from django.utils import timezone

from apps.companies.models import (
    Company,
    Department,
)


class JobOpening(models.Model):

    class Status(models.TextChoices):

        OPEN = "OPEN", "Open"

        ON_HOLD = "ON_HOLD", "On Hold"

        CLOSED = "CLOSED", "Closed"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="job_openings"
    )

    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="job_openings"
    )

    job_code = models.CharField(
        max_length=30,
        unique=True
    )

    title = models.CharField(
        max_length=150
    )

    positions = models.PositiveIntegerField(
        default=1
    )

    description = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.OPEN
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return f"{self.job_code} - {self.title}"


class Candidate(models.Model):

    class Stage(models.TextChoices):

        APPLIED = "APPLIED", "Applied"

        SCREENING = "SCREENING", "Screening"

        INTERVIEW = "INTERVIEW", "Interview"

        SELECTED = "SELECTED", "Selected"

        OFFERED = "OFFERED", "Offered"

        JOINED = "JOINED", "Joined"

        REJECTED = "REJECTED", "Rejected"

    job = models.ForeignKey(
        JobOpening,
        on_delete=models.CASCADE,
        related_name="candidates"
    )

    name = models.CharField(
        max_length=150
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=30
    )

    experience = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    stage = models.CharField(
        max_length=30,
        choices=Stage.choices,
        default=Stage.APPLIED
    )

    interview_date = models.DateTimeField(
        null=True,
        blank=True
    )

    interview_notes = models.TextField(
        blank=True
    )

    applied_on = models.DateField(
        default=timezone.localdate
    )

    class Meta:
        ordering = [
            "-applied_on",
        ]

    def __str__(self):
        return self.name
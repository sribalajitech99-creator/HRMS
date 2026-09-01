from rest_framework import serializers

from .models import (
    JobOpening,
    Candidate,
)


class JobOpeningSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True
    )

    class Meta:
        model = JobOpening
        fields = "__all__"


class CandidateSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(
        source="job.title",
        read_only=True
    )

    job_code = serializers.CharField(
        source="job.job_code",
        read_only=True
    )

    class Meta:
        model = Candidate
        fields = "__all__"
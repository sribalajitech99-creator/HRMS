from django.contrib import admin

from .models import (
    JobOpening,
    Candidate,
)


admin.site.register(
    JobOpening
)

admin.site.register(
    Candidate
)
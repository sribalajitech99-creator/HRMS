from pathlib import Path
from datetime import timedelta
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-development-key"
)

DEBUG = os.getenv(
    "DEBUG",
    "False"
).lower() == "true"

ALLOWED_HOSTS = [
    value.strip()
    for value in os.getenv(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1"
    ).split(",")
    if value.strip()
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "corsheaders",

    "apps.accounts.apps.AccountsConfig",
    "apps.companies.apps.CompaniesConfig",
    "apps.employees.apps.EmployeesConfig",
    "apps.attendance.apps.AttendanceConfig",
    "apps.leave_management.apps.LeaveManagementConfig",
    "apps.payroll.apps.PayrollConfig",
    "apps.recruitment.apps.RecruitmentConfig",
    "apps.assets.apps.AssetsConfig",
    "apps.reports.apps.ReportsConfig",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND":
            "django.template.backends.django.DjangoTemplates",

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",

        "NAME": os.getenv(
            "DB_NAME",
            "hrms_db"
        ),

        "USER": os.getenv(
            "DB_USER",
            "hrms_user"
        ),

        "PASSWORD": os.getenv(
            "DB_PASSWORD",
            ""
        ),

        "HOST": os.getenv(
            "DB_HOST",
            "localhost"
        ),

        "PORT": os.getenv(
            "DB_PORT",
            "3306"
        ),

        "OPTIONS": {
            "charset": "utf8mb4",

            "init_command":
                "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


AUTH_USER_MODEL = "accounts.User"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
        "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator"
    },

    {
        "NAME":
        "django.contrib.auth.password_validation."
        "MinimumLengthValidator"
    },

    {
        "NAME":
        "django.contrib.auth.password_validation."
        "CommonPasswordValidator"
    },

    {
        "NAME":
        "django.contrib.auth.password_validation."
        "NumericPasswordValidator"
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

STATIC_ROOT = (
    BASE_DIR / "staticfiles"
)


CSRF_TRUSTED_ORIGINS = [
    value.strip()
    for value in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "http://localhost:5173",
    ).split(",")
    if value.strip()
]

if os.getenv(
    "SECURE_SSL_REDIRECT",
    "false"
).lower() == "true":
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000

    SECURE_CONTENT_TYPE_NOSNIFF = True

    SECURE_BROWSER_XSS_FILTER = True

    X_FRAME_OPTIONS = "DENY"


MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CORS_ALLOWED_ORIGINS = [
    value.strip()
    for value in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173"
    ).split(",")
    if value.strip()
]


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication."
        "JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions."
        "IsAuthenticated",
    ),

    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework."
        "DjangoFilterBackend",

        "rest_framework.filters."
        "SearchFilter",

        "rest_framework.filters."
        "OrderingFilter",
    ),

    "DEFAULT_PAGINATION_CLASS":
        "apps.attendance.pagination."
        "StandardPagination",

    "PAGE_SIZE": 20,
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":
        timedelta(minutes=30),

    "REFRESH_TOKEN_LIFETIME":
        timedelta(days=1),

    "AUTH_HEADER_TYPES":
        ("Bearer",),
}
from django.urls import path

from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    ChangePasswordView,
    CurrentUserView,
    NotificationViewSet,
    UserViewSet,
)


router = DefaultRouter()


router.register(
    "users",
    UserViewSet,
    basename="users"
)


router.register(
    "notifications",
    NotificationViewSet,
    basename="notifications"
)


urlpatterns = [
    path(
        "login/",
        TokenObtainPairView.as_view()
    ),

    path(
        "refresh/",
        TokenRefreshView.as_view()
    ),

    path(
        "me/",
        CurrentUserView.as_view()
    ),

    path(
        "change-password/",
        ChangePasswordView.as_view()
    ),
]


urlpatterns += router.urls
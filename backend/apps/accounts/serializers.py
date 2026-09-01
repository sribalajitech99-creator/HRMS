from rest_framework import serializers

from .models import Notification, User


class UserSerializer(
    serializers.ModelSerializer
):

    full_name = serializers.SerializerMethodField()

    role_name = serializers.CharField(
        source="get_role_display",
        read_only=True
    )

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    class Meta:

        model = User

        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "role_name",
            "company",
            "company_name",
            "is_active",
            "is_staff",
            "is_superuser",
        ]


    def get_full_name(
        self,
        obj
    ):

        return obj.get_full_name()


class UserCreateSerializer(
    serializers.ModelSerializer
):

    password = serializers.CharField(
        write_only=True
    )

    class Meta:

        model = User

        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "company",
            "is_active",
        ]


    def validate_username(
        self,
        value
    ):
        return value.strip().lower()

    def create(
        self,
        validated_data
    ):

        password = validated_data.pop(
            "password"
        )

        user = User(
            **validated_data
        )

        user.set_password(
            password
        )

        user.save()

        return user


class NotificationSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Notification

        fields = [
            "id",
            "title",
            "message",
            "link",
            "is_read",
            "created_at",
        ]

        read_only_fields = [
            "title",
            "message",
            "link",
            "created_at",
        ]


class ChangePasswordSerializer(
    serializers.Serializer
):

    current_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=6,
    )

    def validate(
        self,
        attrs
    ):

        user = self.context["request"].user

        if not user.check_password(
            attrs["current_password"]
        ):
            raise serializers.ValidationError(
                {
                    "current_password":
                        "Current password is incorrect."
                }
            )

        return attrs
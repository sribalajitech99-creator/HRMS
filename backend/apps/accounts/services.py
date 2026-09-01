from django.db.models import Q

from .models import Notification, User


def notify_user(
    user,
    title,
    message="",
    link="",
):
    if not user:
        return None

    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link,
    )


def notify_hr_staff(
    company,
    title,
    message="",
    link="",
    exclude=None,
):
    """Notify active HR/admin staff for a company.

    Superusers and users whose company matches receive the notification. If no
    company is provided only superusers are notified.
    """
    roles = [
        User.Role.SUPER_ADMIN,
        User.Role.COMPANY_ADMIN,
        User.Role.HR_MANAGER,
        User.Role.HR_EXECUTIVE,
    ]

    staff = User.objects.filter(
        role__in=roles,
        is_active=True,
    )

    if company:
        staff = staff.filter(
            Q(company=company)
            | Q(is_superuser=True)
        )
    else:
        staff = staff.filter(
            is_superuser=True,
        )

    if exclude:
        staff = staff.exclude(
            pk=exclude.pk
        )

    count = 0

    for user in staff:
        notify_user(
            user,
            title,
            message,
            link,
        )
        count += 1

    return count
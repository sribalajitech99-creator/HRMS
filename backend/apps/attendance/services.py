"""Reusable, authoritative attendance time-calculation helpers.

These pure functions are the single source of truth for shift/check-in/
check-out calculations. The Attendance model's ``calculate_hours`` and the
AttendanceSerializer both delegate here so business logic is not duplicated.
"""
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from decimal import Decimal


@dataclass(frozen=True)
class DurationResult:
    hours: Decimal
    minutes: int


def is_overnight_shift(start: time, end: time) -> bool:
    """A shift is overnight when its scheduled end occurs the next calendar day.

    This is the case when the end time is earlier than or equal to the start
    time (e.g. 22:00 -> 06:00).
    """
    return end <= start


def time_to_minutes(value) -> int:
    """Convert a time (or 'HH:MM' string) to minutes since midnight."""
    if value is None:
        return 0
    if isinstance(value, time):
        return value.hour * 60 + value.minute
    if isinstance(value, str):
        hour, minute = value.split(":")[:2]
        return int(hour) * 60 + int(minute)
    return 0


def minutes_to_decimal(minutes) -> Decimal:
    return Decimal(str(minutes / 60)).quantize(Decimal("0.01"))


def minutes_between(start: time, end: time, overnight: bool = False) -> int:
    """Whole minutes from start to end, adding 24h when overnight."""
    delta = time_to_minutes(end) - time_to_minutes(start)
    if overnight:
        delta += 1440
    if delta <= 0:
        delta += 1440
    return delta


def shift_duration_hours(start: time, end: time, break_minutes: int = 0) -> Decimal:
    """Scheduled shift duration in decimal hours (gross, minus break)."""
    gross = minutes_between(start, end, is_overnight_shift(start, end))
    net = max(gross - int(break_minutes or 0), 0)
    return minutes_to_decimal(net)


def full_day_hours(shift) -> Decimal:
    """Net scheduled full-day hours, honouring an explicit override if set."""
    if not shift:
        return Decimal("0.00")
    if shift.full_day_hours is not None:
        return Decimal(str(shift.full_day_hours))
    return shift_duration_hours(
        shift.start_time,
        shift.end_time,
        shift.break_duration,
    )


def worked_duration_hours(
    shift,
    check_in: time,
    check_out: time,
    overnight: bool,
) -> Decimal:
    """Net worked hours on a day, honouring the scheduled break.

    The full scheduled break is counted only when the employee worked a
    full / normal day so payroll does not overstate payable time. If there is
    no shift or no break configured the gross duration is returned.
    """
    if not check_in or not check_out:
        return Decimal("0.00")

    gross = minutes_between(check_in, check_out, overnight)

    break_minutes = 0
    if shift and shift.break_duration:
        break_minutes = int(shift.break_duration)

    return minutes_to_decimal(max(gross - break_minutes, 0))


def overtime_hours(
    shift,
    worked: Decimal,
) -> Decimal:
    """Potential OT = net worked hours beyond the scheduled shift window.

    Break cancels out (it is in both worked and scheduled), so OT reflects
    time actually worked past the raw shift window.
    """
    scheduled = full_day_hours(shift)
    return max(worked - scheduled, Decimal("0.00"))


def late_minutes(
    check_in: time,
    shift,
) -> int:
    """Whole minutes late vs shift start after grace. Never negative."""
    if (
        not check_in
        or not shift
    ):
        return 0

    grace = int(shift.grace_time or 0)
    late = time_to_minutes(check_in) - time_to_minutes(shift.start_time) - grace
    return max(late, 0)


def early_exit_minutes(
    check_out: time,
    shift,
) -> int:
    """Whole minutes left before the shift end. Never negative."""
    if (
        not check_out
        or not shift
    ):
        return 0

    early = time_to_minutes(shift.end_time) - time_to_minutes(check_out)
    return max(early, 0)


def half_day_timing(
    shift,
    first_half: bool,
):
    """Suggested check-in/out for a half day based on the shift's midpoint.

    Returns a ``(check_in, check_out)`` tuple of ``datetime.time``.
    """
    if not shift:
        return None, None

    start = shift.start_time
    end = shift.end_time
    overnight = is_overnight_shift(start, end)

    total = minutes_between(start, end, overnight)
    midpoint = time_to_minutes(start) + total // 2
    if midpoint >= 1440:
        midpoint -= 1440

    mid_time = time_from_minutes(midpoint)

    if first_half:
        return start, mid_time
    return mid_time, end


def time_from_minutes(minutes: int) -> time:
    minutes = minutes % 1440
    return time(minutes // 60, minutes % 60)


def permission_duration_hours(frm: time, to: time) -> Decimal:
    """Duration in decimal hours of a permission window."""
    if not frm or not to:
        return Decimal("0.00")
    minutes = time_to_minutes(to) - time_to_minutes(frm)
    if minutes < 0:
        minutes += 1440
    return minutes_to_decimal(max(minutes, 0))


def effective_working_hours(
    shift,
    check_in: time,
    check_out: time,
    overnight: bool,
    permission_from: time,
    permission_to: time,
) -> Decimal:
    """Net worked hours after deducting scheduled break and permission."""
    worked = worked_duration_hours(
        shift,
        check_in,
        check_out,
        overnight,
    )

    permission = permission_duration_hours(
        permission_from,
        permission_to,
    )

    return max(worked - permission, Decimal("0.00"))

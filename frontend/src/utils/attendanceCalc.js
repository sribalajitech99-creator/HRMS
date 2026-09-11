export function timeToMinutes(value) {
  if (!value) return 0;
  const parts = String(value).split(":");
  const hour = Number(parts[0]) || 0;
  const minute = Number(parts[1]) || 0;
  return hour * 60 + minute;
}

export function isOvernightShift(startTime, endTime) {
  if (!startTime || !endTime) return false;
  return timeToMinutes(endTime) <= timeToMinutes(startTime);
}

export function minutesBetween(startTime, endTime, overnight = false) {
  let delta =
    timeToMinutes(endTime) - timeToMinutes(startTime);
  if (overnight) delta += 1440;
  if (delta <= 0) delta += 1440;
  return delta;
}

export function minutesToDecimal(minutes) {
  return Math.round((minutes / 60) * 100) / 100;
}

export function calculateShiftDuration(shift) {
  if (!shift || !shift.start_time || !shift.end_time) return 0;
  const gross = minutesBetween(
    shift.start_time,
    shift.end_time,
    isOvernightShift(shift.start_time, shift.end_time)
  );
  const breakMin = Number(shift.break_duration) || 0;
  return minutesToDecimal(Math.max(gross - breakMin, 0));
}

export function calculateWorkingDuration(checkIn, checkOut, overnight) {
  if (!checkIn || !checkOut) return 0;
  const gross = minutesBetween(checkIn, checkOut, Boolean(overnight));
  return minutesToDecimal(gross);
}

export function calculateWorkingDurationNet(
  checkIn,
  checkOut,
  overnight,
  breakMinutes = 0
) {
  if (!checkIn || !checkOut) return 0;
  const gross = minutesBetween(checkIn, checkOut, Boolean(overnight));
  return minutesToDecimal(Math.max(gross - (Number(breakMinutes) || 0), 0));
}

export function calculateLateMinutes(checkIn, shift) {
  if (!checkIn || !shift || !shift.start_time) return 0;
  const grace = Number(shift.grace_time) || 0;
  const late =
    timeToMinutes(checkIn) - timeToMinutes(shift.start_time) - grace;
  return Math.max(late, 0);
}

export function calculateEarlyExitMinutes(checkOut, shift) {
  if (!checkOut || !shift || !shift.end_time) return 0;
  const early =
    timeToMinutes(shift.end_time) - timeToMinutes(checkOut);
  return Math.max(early, 0);
}

export function calculateOvertime(shift, workedHours) {
  if (!shift) return 0;
  const scheduled = calculateShiftDuration(shift);
  return Math.max(Number(workedHours) - scheduled, 0);
}

export function calculateHalfDayTiming(shift, firstHalf) {
  if (!shift || !shift.start_time || !shift.end_time) {
    return { checkIn: "", checkOut: "" };
  }
  const overnight = isOvernightShift(shift.start_time, shift.end_time);
  const total = minutesBetween(shift.start_time, shift.end_time, overnight);
  let midpoint = timeToMinutes(shift.start_time) + Math.floor(total / 2);
  if (midpoint >= 1440) midpoint -= 1440;
  const mid = minutesToTime(midpoint);

  if (firstHalf) {
    return {
      checkIn: shift.start_time,
      checkOut: mid,
    };
  }
  return {
    checkIn: mid,
    checkOut: shift.end_time,
  };
}

export function calculatePermissionDuration(from, to) {
  if (!from || !to) return 0;
  let minutes = timeToMinutes(to) - timeToMinutes(from);
  if (minutes < 0) minutes += 1440;
  return minutesToDecimal(Math.max(minutes, 0));
}

export function calculateEffectiveWorkingHours(
  workedHours,
  permissionDuration
) {
  return Math.max(
    (Number(workedHours) || 0) - (Number(permissionDuration) || 0),
    0
  );
}

export function minutesToTime(minutes) {
  const m = ((minutes % 1440) + 1440) % 1440;
  const h = Math.floor(m / 60);
  const min = m % 60;
  return `${String(h).padStart(2, "0")}:${String(min).padStart(2, "0")}`;
}

export function decimalToHhMm(decimalHours) {
  const value = Number(decimalHours) || 0;
  const totalMinutes = Math.round(value * 60);
  const h = Math.floor(totalMinutes / 60);
  const min = totalMinutes % 60;
  return `${String(h).padStart(2, "0")}:${String(min).padStart(2, "0")}`;
}

export function formatMinutes(minutes) {
  const value = Number(minutes) || 0;
  const h = Math.floor(value / 60);
  const min = value % 60;
  if (h === 0) return `${min} min`;
  if (min === 0) return `${h} hr`;
  return `${h} hr ${min} min`;
}

export const ATTENDANCE_TYPES = [
  { value: "FULL_DAY", label: "Full Day" },
  { value: "HALF_DAY_FIRST_HALF", label: "Half Day - First Half" },
  { value: "HALF_DAY_SECOND_HALF", label: "Half Day - Second Half" },
  { value: "PERMISSION", label: "Permission" },
  { value: "LATE_ENTRY", label: "Late Entry" },
  { value: "EARLY_EXIT", label: "Early Exit" },
  { value: "WORK_FROM_HOME", label: "Work From Home" },
  { value: "ON_DUTY", label: "On Duty" },
];

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Search,
  Trash2,
  X,
} from "lucide-react";

import api from "../../api/client";

import {
  ATTENDANCE_TYPES,
  calculateEarlyExitMinutes,
  calculateEffectiveWorkingHours,
  calculateHalfDayTiming,
  calculateLateMinutes,
  calculateOvertime,
  calculatePermissionDuration,
  calculateWorkingDuration,
  calculateWorkingDurationNet,
  decimalToHhMm,
  formatMinutes,
  isOvernightShift,
} from "../../utils/attendanceCalc";

import "../../styles/attendance-calendar.css";


const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];


const EMPTY_FORM = {
  status: "PRESENT",
  attendance_type: "FULL_DAY",
  shift: "",
  check_in_time: "",
  check_out_time: "",
  check_out_next_day: false,
  approved_ot_hours: "0",
  permission_from: "",
  permission_to: "",
  permission_reason: "",
  remarks: "",
};


function formatDate(
  year,
  month,
  day
) {
  return [
    year,
    String(month + 1).padStart(2, "0"),
    String(day).padStart(2, "0"),
  ].join("-");
}


export default function AttendancePage() {
  const today = new Date();

  const [
    currentYear,
    setCurrentYear,
  ] = useState(
    today.getFullYear()
  );

  const [
    currentMonth,
    setCurrentMonth,
  ] = useState(
    today.getMonth()
  );

  const [
    employees,
    setEmployees,
  ] = useState([]);

  const [
    employeeSearch,
    setEmployeeSearch,
  ] = useState("");

  const [
    employeeResultsOpen,
    setEmployeeResultsOpen,
  ] = useState(false);

  const [
    selectedEmployee,
    setSelectedEmployee,
  ] = useState(null);

  const [
    attendance,
    setAttendance,
  ] = useState([]);

  const [
    holidays,
    setHolidays,
  ] = useState([]);

  const [
    shifts,
    setShifts,
  ] = useState([]);

  const [
    selectedDate,
    setSelectedDate,
  ] = useState(null);

  const [
    selectedRecord,
    setSelectedRecord,
  ] = useState(null);

  const [
    drawerOpen,
    setDrawerOpen,
  ] = useState(false);

  const [
    form,
    setForm,
  ] = useState(
    EMPTY_FORM
  );

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");


  const manualOverrideRef =
    useRef({
      checkIn: false,
      checkOut: false,
    });


  const findShift = useCallback((
    shiftId
  ) =>
    shifts.find(
      (shift) =>
        String(shift.id) ===
        String(shiftId)
    ),
  [shifts]);


  /* =========================================================
     EMPLOYEE SEARCH
  ========================================================= */

  useEffect(() => {
    const query =
      employeeSearch.trim();

    if (!query) {
      setEmployees([]);
      setEmployeeResultsOpen(false);
      return;
    }

    const timer = setTimeout(
      async () => {
        try {
          const response =
            await api.get(
              "/employees/",
              {
                params: {
                  search: query,
                  page_size: 20,
                },
              }
            );

          const data =
            response.data?.results ??
            response.data ??
            [];

          setEmployees(
            Array.isArray(data)
              ? data
              : []
          );

          setEmployeeResultsOpen(
            true
          );
        } catch (err) {
          console.error(
            "Employee search error:",
            err
          );
        }
      },
      300
    );

    return () =>
      clearTimeout(timer);
  }, [employeeSearch]);


  /* =========================================================
     LOAD ATTENDANCE / HOLIDAYS / SHIFTS
  ========================================================= */

  const loadCalendarData =
    async () => {
      if (!selectedEmployee) {
        return;
      }

      setLoading(true);

      try {
        const [
          attendanceResponse,
          holidayResponse,
          shiftsResponse,
        ] = await Promise.all([
          api.get(
            "/attendance/",
            {
              params: {
                employee:
                  selectedEmployee.id,
                year:
                  currentYear,
                month:
                  currentMonth + 1,
                page_size:
                  100,
              },
            }
          ),

          api.get(
            "/holidays/",
            {
              params: {
                company:
                  selectedEmployee.company,
                year:
                  currentYear,
                month:
                  currentMonth + 1,
                page_size:
                  100,
              },
            }
          ),

          api.get(
            "/shifts/",
            {
              params: {
                company:
                  selectedEmployee.company,
                is_active:
                  true,
                page_size:
                  100,
              },
            }
          ),
        ]);

        const attendanceData =
          attendanceResponse.data
            ?.results ??
          attendanceResponse.data ??
          [];

        const holidayData =
          holidayResponse.data
            ?.results ??
          holidayResponse.data ??
          [];

        const shiftData =
          shiftsResponse.data
            ?.results ??
          shiftsResponse.data ??
          [];

        setAttendance(
          Array.isArray(
            attendanceData
          )
            ? attendanceData
            : []
        );

        setHolidays(
          Array.isArray(
            holidayData
          )
            ? holidayData
            : []
        );

        setShifts(
          Array.isArray(
            shiftData
          )
            ? shiftData
            : []
        );
      } catch (err) {
        console.error(
          "Attendance data error:",
          err
        );

        setError(
          "Unable to load attendance data."
        );
      } finally {
        setLoading(false);
      }
    };


  useEffect(() => {
    loadCalendarData();
  }, [
    selectedEmployee,
    currentYear,
    currentMonth,
  ]);


  /* =========================================================
     MAP ATTENDANCE / HOLIDAYS
  ========================================================= */

  const attendanceMap =
    useMemo(() => {
      const map = {};

      attendance.forEach(
        (record) => {
          map[
            record.date
          ] = record;
        }
      );

      return map;
    }, [attendance]);


  const holidayMap =
    useMemo(() => {
      const map = {};

      holidays.forEach(
        (holiday) => {
          map[
            holiday.date
          ] = holiday;
        }
      );

      return map;
    }, [holidays]);


  /* =========================================================
     CALENDAR DAYS
  ========================================================= */

  const calendarCells =
    useMemo(() => {
      const firstDay =
        new Date(
          currentYear,
          currentMonth,
          1
        ).getDay();

      const totalDays =
        new Date(
          currentYear,
          currentMonth + 1,
          0
        ).getDate();

      const cells = [];

      for (
        let index = 0;
        index < firstDay;
        index++
      ) {
        cells.push(null);
      }

      for (
        let day = 1;
        day <= totalDays;
        day++
      ) {
        cells.push(day);
      }

      return cells;
    }, [
      currentYear,
      currentMonth,
    ]);


  /* =========================================================
     SELECT EMPLOYEE
  ========================================================= */

  const selectEmployee = (
    employee
  ) => {
    setSelectedEmployee(
      employee
    );

    setEmployeeSearch("");

    setEmployeeResultsOpen(
      false
    );

    setAttendance([]);
    setHolidays([]);
    setShifts([]);

    setSelectedDate(null);
    setSelectedRecord(null);
    setDrawerOpen(false);
  };


  /* =========================================================
     OPEN DATE DRAWER
  ========================================================= */

  const populateFormFromRecord = (
    record,
    holiday
  ) => {
    if (record) {
      const shift =
        findShift(
          record.shift
        );

      const savedCheckIn =
        record.check_in_time
          ? record.check_in_time.slice(
              0,
              5
            )
          : "";

      const savedCheckOut =
        record.check_out_time
          ? record.check_out_time.slice(
              0,
              5
            )
          : "";

      const shiftStart =
        shift
          ? shift.start_time.slice(
              0,
              5
            )
          : "";

      const shiftEnd =
        shift
          ? shift.end_time.slice(
              0,
              5
            )
          : "";

      const overnight =
        Boolean(
          record.check_out_next_day
        ) ||
        (shift &&
          isOvernightShift(
            shift.start_time,
            shift.end_time
          ));

      setForm({
        status:
          record.status ||
          "PRESENT",

        attendance_type:
          record.attendance_type ||
          "FULL_DAY",

        shift:
          record.shift ||
          "",

        check_in_time:
          savedCheckIn ||
          shiftStart,

        check_out_time:
          savedCheckOut ||
          shiftEnd,

        check_out_next_day:
          overnight,

        approved_ot_hours:
          record.approved_ot_hours ??
          "0",

        permission_from:
          record.permission_from
            ? record.permission_from.slice(
                0,
                5
              )
            : "",

        permission_to:
          record.permission_to
            ? record.permission_to.slice(
                0,
                5
              )
            : "",

        permission_reason:
          record.permission_reason ||
          "",

        remarks:
          record.remarks ||
          "",
      });
    } else {
      setForm({
        ...EMPTY_FORM,

        status:
          holiday
            ? "HOLIDAY"
            : "PRESENT",
      });
    }
  };


  const openDate = async (
    day
  ) => {
    if (!selectedEmployee) {
      return;
    }

    const date =
      formatDate(
        currentYear,
        currentMonth,
        day
      );

    const holiday =
      holidayMap[
        date
      ];

    setSelectedDate(date);

    setError("");

    manualOverrideRef.current = {
      checkIn: false,
      checkOut: false,
    };

    setDrawerOpen(true);

    let record =
      attendanceMap[date] ||
      null;

    try {
      const response =
        await api.get(
          "/attendance/",
          {
            params: {
              employee:
                selectedEmployee.id,
              date,
              page_size: 1,
            },
          }
        );

      const found =
        response.data?.results?.[0] ??
        response.data?.[0] ??
        null;

      if (found) {
        record = found;
      }
    } catch (err) {
      console.error(
        "Load attendance record error:",
        err
      );
    }

    setSelectedRecord(record);

    populateFormFromRecord(
      record,
      holiday
    );
  };


  /* =========================================================
     SHIFT / ATTENDANCE TYPE / TIME CHANGE
  ========================================================= */

  const handleShiftChange = (
    value
  ) => {
    const shift =
      findShift(value);

    const overnight =
      Boolean(
        shift &&
        isOvernightShift(
          shift.start_time,
          shift.end_time
        )
      );

    setForm((
      current
    ) => ({

      ...current,

      shift: value,

      check_in_time:
        shift
          ? shift.start_time.slice(
              0,
              5
            )
          : current.check_in_time,

      check_out_time:
        shift
          ? shift.end_time.slice(
              0,
              5
            )
          : current.check_out_time,

      check_out_next_day:
        overnight,

    }));

    manualOverrideRef.current = {
      checkIn: false,
      checkOut: false,
    };
  };


  const handleAttendanceTypeChange = (
    value
  ) => {
    setForm((
      current
    ) => {

      const next = {
        ...current,
        attendance_type:
          value,
      };

      const isFirstHalf =
        value ===
        "HALF_DAY_FIRST_HALF";

      const isSecondHalf =
        value ===
        "HALF_DAY_SECOND_HALF";

      if (
        isFirstHalf ||
        isSecondHalf
      ) {
        const shift =
          findShift(
            current.shift
          );

        if (shift) {
          const timing =
            calculateHalfDayTiming(
              shift,
              isFirstHalf
            );

          next.check_in_time =
            timing.checkIn
              ? timing.checkIn.slice(
                  0,
                  5
                )
              : "";

          next.check_out_time =
            timing.checkOut
              ? timing.checkOut.slice(
                  0,
                  5
                )
              : "";
        }
      }

      return next;
    });
  };


  const handleTimeChange = (
    field,
    value
  ) => {
    setForm((
      current
    ) => ({

      ...current,
      [field]: value,

    }));

    if (
      field ===
      "check_in_time"
    ) {
      manualOverrideRef.current.checkIn =
        true;
    } else if (
      field ===
      "check_out_time"
    ) {
      manualOverrideRef.current.checkOut =
        true;
    }
  };


  /* =========================================================
     SAVE ATTENDANCE
  ========================================================= */

  const saveAttendance =
    async () => {
      if (
        !selectedEmployee ||
        !selectedDate
      ) {
        return;
      }

      setSaving(true);
      setError("");

      const holiday =
        holidayMap[
          selectedDate
        ];

      const payload = {
        employee:
          selectedEmployee.id,

        date:
          selectedDate,

        status:
          form.status,

        attendance_type:
          form.attendance_type ||
          "FULL_DAY",

        shift:
          form.shift
            ? Number(
                form.shift
              )
            : null,

        check_in_time:
          form.check_in_time ||
          null,

        check_out_time:
          form.check_out_time ||
          null,

        check_out_next_day:
          Boolean(
            form.check_out_next_day
          ),

        approved_ot_hours:
          Number(
            form.approved_ot_hours ||
            0
          ),

        permission_from:
          form.permission_from ||
          null,

        permission_to:
          form.permission_to ||
          null,

        permission_reason:
          form.permission_reason ||
          "",

        holiday:
          holiday?.id ||
          null,

        remarks:
          form.remarks ||
          "",
      };

      try {
        if (selectedRecord) {
          await api.patch(
            `/attendance/${selectedRecord.id}/`,
            payload
          );
        } else {
          await api.post(
            "/attendance/",
            payload
          );
        }

        setDrawerOpen(false);

        await loadCalendarData();
      } catch (err) {
        console.error(
          "Save attendance error:",
          err
        );

        const data =
          err.response?.data;

        const isDuplicate =
          data &&
          typeof data ===
            "object" &&
          /unique|already exist/i.test(
            [
              ...[].concat(
                data.non_field_errors ||
                  []
              ),
              ...[].concat(
                Array.isArray(
                  data.employee
                )
                  ? data.employee
                  : []
              ),
              ...[].concat(
                Array.isArray(
                  data.date
                )
                  ? data.date
                  : []
              ),
            ].join(" ")
          );

        if (isDuplicate) {
          try {
            const response =
              await api.get(
                "/attendance/",
                {
                  params: {
                    employee:
                      selectedEmployee.id,
                    date:
                      selectedDate,
                    page_size: 1,
                  },
                }
              );

            const existing =
              response.data?.results?.[0] ??
              response.data?.[0] ??
              null;

            if (existing) {
              setSelectedRecord(
                existing
              );

              populateFormFromRecord(
                existing,
                holidayMap[
                  selectedDate
                ]
              );
            }
          } catch (reloadErr) {
            console.error(
              "Reload existing attendance error:",
              reloadErr
            );
          }

          setError(
            "Attendance already exists for this employee on this date. It has been loaded for editing."
          );
        } else if (data) {
          if (
            typeof data ===
            "string"
          ) {
            setError(data);
          } else {
            setError(
              Object.entries(data)
                .map(
                  ([
                    key,
                    value,
                  ]) =>
                    `${key}: ${
                      Array.isArray(
                        value
                      )
                        ? value.join(
                            ", "
                          )
                        : value
                    }`
                )
                .join(" | ")
            );
          }
        } else {
          setError(
            "Unable to save attendance."
          );
        }
      } finally {
        setSaving(false);
      }
    };


  /* =========================================================
     DELETE ATTENDANCE
  ========================================================= */

  const deleteAttendance =
    async () => {
      if (!selectedRecord) {
        return;
      }

      const confirmed =
        window.confirm(
          "Are you sure you want to delete this attendance record?"
        );

      if (!confirmed) {
        return;
      }

      try {
        await api.delete(
          `/attendance/${selectedRecord.id}/`
        );

        setDrawerOpen(false);

        await loadCalendarData();
      } catch (err) {
        console.error(
          "Delete attendance error:",
          err
        );

        setError(
          "Unable to delete attendance."
        );
      }
    };


  /* =========================================================
     MONTH NAVIGATION
  ========================================================= */

  const previousMonth = () => {
    if (
      currentMonth === 0
    ) {
      setCurrentMonth(11);

      setCurrentYear(
        (year) =>
          year - 1
      );
    } else {
      setCurrentMonth(
        (month) =>
          month - 1
      );
    }
  };


  const nextMonth = () => {
    if (
      currentMonth === 11
    ) {
      setCurrentMonth(0);

      setCurrentYear(
        (year) =>
          year + 1
      );
    } else {
      setCurrentMonth(
        (month) =>
          month + 1
      );
    }
  };


  const goToCurrentMonth = () => {
    const now =
      new Date();

    setCurrentYear(
      now.getFullYear()
    );

    setCurrentMonth(
      now.getMonth()
    );
  };


  /* =========================================================
     MONTH SUMMARY
  ========================================================= */

  const summary =
    useMemo(() => {
      const result = {
        present: 0,
        absent: 0,
        leave: 0,
        halfDay: 0,
        holiday: 0,
        weekOff: 0,
        workingHours: 0,
        ot: 0,
      };

      attendance.forEach(
        (record) => {
          switch (
            record.status
          ) {
            case "PRESENT":
              result.present += 1;
              break;

            case "ABSENT":
              result.absent += 1;
              break;

            case "ON_LEAVE":
              result.leave += 1;
              break;

            case "HALF_DAY":
              result.halfDay += 1;
              break;

            case "HOLIDAY":
              result.holiday += 1;
              break;

            case "WEEK_OFF":
              result.weekOff += 1;
              break;

            default:
              break;
          }

          result.workingHours +=
            Number(
              record.working_hours ||
              0
            );

          result.ot +=
            Number(
              record.approved_ot_hours ||
              0
            );
        }
      );

      return result;
    }, [attendance]);


  /* =========================================================
     STATUS HELPERS
  ========================================================= */

  const getStatusShort = (
    status
  ) => {
    switch (status) {
      case "PRESENT":
        return "P";

      case "ABSENT":
        return "A";

      case "ON_LEAVE":
        return "L";

      case "HALF_DAY":
        return "HD";

      case "HOLIDAY":
        return "H";

      case "WEEK_OFF":
        return "WO";

      default:
        return "-";
    }
  };


  const getStatusLabel = (
    status
  ) => {
    switch (status) {
      case "PRESENT":
        return "Present";

      case "ABSENT":
        return "Absent";

      case "ON_LEAVE":
        return "On Leave";

      case "HALF_DAY":
        return "Half Day";

      case "HOLIDAY":
        return "Holiday";

      case "WEEK_OFF":
        return "Week Off";

      default:
        return status;
    }
  };


  /* =========================================================
     LIVE CALCULATIONS
  ========================================================= */

  const computed = useMemo(() => {
    const shift = findShift(form.shift);

    const overnight =
      Boolean(form.check_out_next_day) ||
      (shift &&
        isOvernightShift(
          shift.start_time,
          shift.end_time
        ));

    const breakMinutes = Number(
      shift?.break_duration || 0
    );

    const workingHours = calculateWorkingDurationNet(
      form.check_in_time,
      form.check_out_time,
      overnight,
      breakMinutes
    );

    const grossWorkingHours = calculateWorkingDuration(
      form.check_in_time,
      form.check_out_time,
      overnight
    );

    const permissionDuration = calculatePermissionDuration(
      form.permission_from,
      form.permission_to
    );

    const effectiveWorkingHours = calculateEffectiveWorkingHours(
      workingHours,
      permissionDuration
    );

    const calculatedOT = calculateOvertime(
      shift,
      workingHours
    );

    const lateMinutes = calculateLateMinutes(
      form.check_in_time,
      shift
    );

    const earlyExitMinutes = calculateEarlyExitMinutes(
      form.check_out_time,
      shift
    );

    return {
      overnight,
      workingHours,
      grossWorkingHours,
      permissionDuration,
      effectiveWorkingHours,
      calculatedOT,
      lateMinutes,
      earlyExitMinutes,
    };
  }, [
    form.shift,
    form.check_in_time,
    form.check_out_time,
    form.check_out_next_day,
    form.attendance_type,
    form.permission_from,
    form.permission_to,
    shifts,
    findShift,
  ]);


  /* =========================================================
     PAGE UI
  ========================================================= */

  return (
    <div className="attendance-page">

      {/* PAGE HEADER */}

      <div className="attendance-page-header">
        <div>
          <h1>
            Attendance
          </h1>

          <p>
            Search an employee,
            select a date and
            manage attendance
            from the monthly
            calendar.
          </p>
        </div>
      </div>


      {/* EMPLOYEE SEARCH */}

      <div className="attendance-search-section">

        <div className="attendance-search-title">
          Employee Attendance
        </div>

        <div className="attendance-search-container">

          <Search
            size={19}
            className="attendance-search-icon"
          />

          <input
            type="text"
            placeholder="Search employee by name or employee ID..."
            value={
              employeeSearch
            }
            onChange={(
              event
            ) =>
              setEmployeeSearch(
                event.target.value
              )
            }
            onFocus={() => {
              if (
                employees.length
              ) {
                setEmployeeResultsOpen(
                  true
                );
              }
            }}
          />

        </div>


        {employeeResultsOpen &&
          employees.length >
            0 && (

          <div className="attendance-search-results">

            {employees.map(
              (
                employee
              ) => {

                const fullName =
                  `${employee.first_name || ""} ${
                    employee.last_name || ""
                  }`.trim();

                return (
                  <button
                    type="button"
                    key={
                      employee.id
                    }
                    className="attendance-search-result"
                    onClick={() =>
                      selectEmployee(
                        employee
                      )
                    }
                  >

                    <div className="attendance-search-result-code">
                      {
                        employee.employee_code
                      }
                    </div>

                    <div className="attendance-search-result-main">

                      <strong>
                        {fullName ||
                          "Unnamed Employee"}
                      </strong>

                      <span>
                        {
                          employee.company_name ||
                          "-"
                        }
                        {" • "}
                        {
                          employee.department_name ||
                          "No Department"
                        }
                      </span>

                    </div>

                    <div className="attendance-search-result-designation">
                      {
                        employee.designation_name ||
                        "-"
                      }
                    </div>

                  </button>
                );
              }
            )}

          </div>
        )}

      </div>


      {/* NO EMPLOYEE */}

      {!selectedEmployee ? (

        <div className="attendance-empty-state">

          <div className="attendance-empty-icon">
            <CalendarDays
              size={34}
            />
          </div>

          <h3>
            Select an employee
          </h3>

          <p>
            Search an employee above
            to open their monthly
            attendance calendar.
          </p>

        </div>

      ) : (
        <>

          {/* SELECTED EMPLOYEE */}

          <div className="attendance-employee-card">

            <div className="attendance-employee-main">

              <div className="attendance-avatar">
                {(
                  selectedEmployee.first_name?.[0] ||
                  "E"
                ).toUpperCase()}
              </div>

              <div>

                <span className="attendance-employee-id">
                  {
                    selectedEmployee.employee_code
                  }
                </span>

                <h3>
                  {
                    selectedEmployee.first_name
                  }{" "}
                  {
                    selectedEmployee.last_name
                  }
                </h3>

              </div>

            </div>


            <div className="attendance-employee-info">

              <div>
                <span>
                  Company
                </span>

                <strong>
                  {
                    selectedEmployee.company_name ||
                    "-"
                  }
                </strong>
              </div>

              <div>
                <span>
                  Department
                </span>

                <strong>
                  {
                    selectedEmployee.department_name ||
                    "-"
                  }
                </strong>
              </div>

              <div>
                <span>
                  Designation
                </span>

                <strong>
                  {
                    selectedEmployee.designation_name ||
                    "-"
                  }
                </strong>
              </div>

            </div>

          </div>


          {/* SUMMARY */}

          <div className="attendance-summary-grid">

            <SummaryCard
              label="Present"
              value={
                summary.present
              }
            />

            <SummaryCard
              label="Absent"
              value={
                summary.absent
              }
            />

            <SummaryCard
              label="On Leave"
              value={
                summary.leave
              }
            />

            <SummaryCard
              label="Half Day"
              value={
                summary.halfDay
              }
            />

            <SummaryCard
              label="Working Hours"
              value={
                summary.workingHours.toFixed(
                  2
                )
              }
            />

            <SummaryCard
              label="OT Hours"
              value={
                summary.ot.toFixed(
                  2
                )
              }
            />

          </div>


          {/* CALENDAR */}

          <div className="attendance-calendar-card">

            <div className="attendance-calendar-top">

              <div className="attendance-calendar-month-navigation">

                <button
                  type="button"
                  className="attendance-navigation-button"
                  onClick={
                    previousMonth
                  }
                >
                  <ChevronLeft
                    size={19}
                  />
                </button>

                <div>
                  <h2>
                    {
                      MONTHS[
                        currentMonth
                      ]
                    }{" "}
                    {
                      currentYear
                    }
                  </h2>

                  <span>
                    Click any date to
                    add or edit
                    attendance
                  </span>
                </div>

                <button
                  type="button"
                  className="attendance-navigation-button"
                  onClick={
                    nextMonth
                  }
                >
                  <ChevronRight
                    size={19}
                  />
                </button>

              </div>


              <button
                type="button"
                className="attendance-today-button"
                onClick={
                  goToCurrentMonth
                }
              >
                Today
              </button>

            </div>


            {loading && (
              <div className="attendance-loading">
                Loading attendance...
              </div>
            )}


            <div className="attendance-week-header">

              {[
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
              ].map(
                (
                  day
                ) => (
                  <div
                    key={
                      day
                    }
                  >
                    {day}
                  </div>
                )
              )}

            </div>


            <div className="attendance-calendar-grid">

              {calendarCells.map(
                (
                  day,
                  index
                ) => {

                  if (!day) {
                    return (
                      <div
                        key={
                          `empty-${index}`
                        }
                        className="attendance-calendar-cell attendance-calendar-empty"
                      />
                    );
                  }

                  const date =
                    formatDate(
                      currentYear,
                      currentMonth,
                      day
                    );

                  const record =
                    attendanceMap[
                      date
                    ];

                  const holiday =
                    holidayMap[
                      date
                    ];

                  const dayDate =
                    new Date(
                      currentYear,
                      currentMonth,
                      day
                    );

                  const isSunday =
                    dayDate.getDay() ===
                    0;

                  const isToday =
                    date ===
                    formatDate(
                      today.getFullYear(),
                      today.getMonth(),
                      today.getDate()
                    );

                  return (
                    <button
                      type="button"
                      key={
                        date
                      }
                      className={[
                        "attendance-calendar-cell",

                        isSunday
                          ? "attendance-sunday"
                          : "",

                        holiday
                          ? "attendance-holiday-cell"
                          : "",

                        isToday
                          ? "attendance-today-cell"
                          : "",

                        record
                          ? `attendance-status-${record.status.toLowerCase()}`
                          : "",
                      ]
                        .filter(Boolean)
                        .join(" ")}
                      onClick={() =>
                        openDate(
                          day
                        )
                      }
                    >

                      <div className="attendance-calendar-cell-top">

                        <span className="attendance-day-number">
                          {day}
                        </span>

                        {record && (
                          <span
                            className={`attendance-mini-status attendance-mini-${record.status.toLowerCase()}`}
                          >
                            {
                              getStatusShort(
                                record.status
                              )
                            }
                          </span>
                        )}

                      </div>


                      {holiday && (
                        <div className="attendance-holiday-label">
                          {
                            holiday.name
                          }
                        </div>
                      )}


                      {record && (
                        <div className="attendance-calendar-record">

                          <strong>
                            {
                              getStatusLabel(
                                record.status
                              )
                            }
                          </strong>

                          {record.shift_name && (
                            <span>
                              {
                                record.shift_name
                              }
                            </span>
                          )}

                          {record.check_in_time &&
                            record.check_out_time && (

                            <small>
                              {
                                record.check_in_time.slice(
                                  0,
                                  5
                                )
                              }
                              {" - "}
                              {
                                record.check_out_time.slice(
                                  0,
                                  5
                                )
                              }
                            </small>
                          )}


                          {Number(
                            record.approved_ot_hours ||
                              0
                          ) >
                            0 && (

                            <small className="attendance-calendar-ot">
                              OT:{" "}
                              {
                                record.approved_ot_hours
                              }{" "}
                              hrs
                            </small>
                          )}

                        </div>
                      )}

                    </button>
                  );
                }
              )}

            </div>

          </div>

        </>
      )}


      {/* DRAWER BACKDROP */}

      {drawerOpen && (
        <div
          className="attendance-drawer-backdrop"
          onClick={() =>
            setDrawerOpen(
              false
            )
          }
        />
      )}


      {/* ATTENDANCE DRAWER */}

      <aside
        className={`attendance-drawer ${
          drawerOpen
            ? "attendance-drawer-open"
            : ""
        }`}
      >

        <div className="attendance-drawer-header">

          <div>
            <span>
              Employee Attendance
            </span>

            <h3>
              {
                selectedDate ||
                "-"
              }
            </h3>
          </div>

          <button
            type="button"
            onClick={() =>
              setDrawerOpen(
                false
              )
            }
          >
            <X
              size={20}
            />
          </button>

        </div>


        <div className="attendance-drawer-content">

          {selectedEmployee && (
            <div className="attendance-drawer-employee-card">

              <div className="attendance-drawer-avatar">
                {(
                  selectedEmployee.first_name?.[0] ||
                  "E"
                ).toUpperCase()}
              </div>

              <div>
                <strong>
                  {
                    selectedEmployee.employee_code
                  }
                  {" - "}
                  {
                    selectedEmployee.first_name
                  }
                  {" "}
                  {
                    selectedEmployee.last_name
                  }
                </strong>

                <span>
                  {
                    selectedEmployee.department_name ||
                    "-"
                  }
                  {" • "}
                  {
                    selectedEmployee.designation_name ||
                    "-"
                  }
                </span>
              </div>

            </div>
          )}


          {holidayMap[
            selectedDate
          ] && (

            <div className="attendance-holiday-notice">

              <CalendarDays
                size={19}
              />

              <div>
                <strong>
                  Holiday
                </strong>

                <span>
                  {
                    holidayMap[
                      selectedDate
                    ].name
                  }
                </span>
              </div>

            </div>
          )}


          {error && (
            <div className="attendance-error">
              {error}
            </div>
          )}


          <AttendanceField
            label="Attendance Status"
          >

            <select
              value={
                form.status
              }
              onChange={(
                event
              ) =>
                setForm({
                  ...form,
                  status:
                    event.target
                      .value,
                })
              }
            >

              <option value="PRESENT">
                Present
              </option>

              <option value="ABSENT">
                Absent
              </option>

              <option value="ON_LEAVE">
                On Leave
              </option>

              <option value="HALF_DAY">
                Half Day
              </option>

              <option value="HOLIDAY">
                Holiday
              </option>

              <option value="WEEK_OFF">
                Week Off
              </option>

            </select>

          </AttendanceField>


          <AttendanceField
            label="Attendance Type"
          >

            <select
              value={
                form.attendance_type
              }
              onChange={(
                event
              ) =>
                handleAttendanceTypeChange(
                  event.target
                    .value
                )
              }
            >

              {ATTENDANCE_TYPES.map(
                (
                  type
                ) => (
                  <option
                    key={
                      type.value
                    }
                    value={
                      type.value
                    }
                  >
                    {
                      type.label
                    }
                  </option>
                )
              )}

            </select>

          </AttendanceField>


          <AttendanceField
            label="Shift"
          >

            <select
              value={
                form.shift
              }
              onChange={(
                event
              ) =>
                handleShiftChange(
                  event.target.value
                )
              }
            >

              <option value="">
                Select Shift
              </option>

              {shifts.map(
                (
                  shift
                ) => (
                  <option
                    key={
                      shift.id
                    }
                    value={
                      shift.id
                    }
                  >
                    {
                      shift.name
                    }
                    {" - "}
                    {
                      shift.start_time?.slice(
                        0,
                        5
                      )
                    }
                    {" to "}
                    {
                      shift.end_time?.slice(
                        0,
                        5
                      )
                    }
                  </option>
                )
              )}

            </select>

          </AttendanceField>


          <div className="attendance-two-column">

            <AttendanceField
              label="Check In"
            >

              <input
                type="time"
                value={
                  form.check_in_time
                }
                onChange={(
                  event
                ) =>
                  handleTimeChange(
                    "check_in_time",
                    event.target
                      .value
                  )
                }
              />

            </AttendanceField>


            <AttendanceField
              label="Check Out"
            >

              <input
                type="time"
                value={
                  form.check_out_time
                }
                onChange={(
                  event
                ) =>
                  handleTimeChange(
                    "check_out_time",
                    event.target
                      .value
                  )
                }
              />

            </AttendanceField>

          </div>


          <label className="attendance-next-day">

            <input
              type="checkbox"
              checked={
                form.check_out_next_day
              }
              onChange={(
                event
              ) =>
                setForm({
                  ...form,
                  check_out_next_day:
                    event.target
                      .checked,
                })
              }
            />

            <span>
              Check-out is on the next day
            </span>

          </label>


          {form.attendance_type ===
            "PERMISSION" && (
            <>
              <div className="attendance-two-column">

                <AttendanceField
                  label="Permission From"
                >

                  <input
                    type="time"
                    value={
                      form.permission_from
                    }
                    onChange={(
                      event
                    ) =>
                      setForm({
                        ...form,
                        permission_from:
                          event.target
                            .value,
                      })
                    }
                  />

                </AttendanceField>


                <AttendanceField
                  label="Permission To"
                >

                  <input
                    type="time"
                    value={
                      form.permission_to
                    }
                    onChange={(
                      event
                    ) =>
                      setForm({
                        ...form,
                        permission_to:
                          event.target
                            .value,
                      })
                    }
                  />

                </AttendanceField>

              </div>


              <AttendanceField
                label="Permission Reason"
              >

                <input
                  type="text"
                  placeholder="Reason for permission..."
                  value={
                    form.permission_reason
                  }
                  onChange={(
                    event
                  ) =>
                    setForm({
                      ...form,
                      permission_reason:
                        event.target
                          .value,
                    })
                  }
                />

              </AttendanceField>
            </>
          )}


          <div className="attendance-hours-box attendance-hours-live">

            <div>
              <span>
                Working Hours
              </span>

              <strong>
                {
                  decimalToHhMm(
                    form.attendance_type ===
                      "PERMISSION"
                      ? computed.effectiveWorkingHours
                      : computed.workingHours
                  )
                }
              </strong>
            </div>

            <div>
              <span>
                Late
              </span>

              <strong>
                {
                  computed.lateMinutes > 0
                    ? formatMinutes(
                        computed.lateMinutes
                      )
                    : "00:00"
                }
              </strong>
            </div>

            <div>
              <span>
                Early Exit
              </span>

              <strong>
                {
                  computed.earlyExitMinutes > 0
                    ? formatMinutes(
                        computed.earlyExitMinutes
                      )
                    : "00:00"
                }
              </strong>
            </div>

            <div>
              <span>
                Calculated OT
              </span>

              <strong>
                {
                  computed.calculatedOT.toFixed(2)
                }
              </strong>
            </div>

          </div>


          {form.attendance_type ===
            "PERMISSION" && (
            <div className="attendance-permission-box">

              <div>
                <span>
                  Permission Duration
                </span>

                <strong>
                  {
                    formatMinutes(
                      computed.permissionDuration *
                        60
                    )
                  }
                </strong>
              </div>

              <div>
                <span>
                  Effective Working Hours
                </span>

                <strong>
                  {
                    decimalToHhMm(
                      computed.effectiveWorkingHours
                    )
                  }
                </strong>
              </div>

            </div>
          )}


          <AttendanceField
            label="Approved OT Hours"
          >

            <input
              type="number"
              min="0"
              step="0.25"
              value={
                form.approved_ot_hours
              }
              onChange={(
                event
              ) =>
                setForm({
                  ...form,
                  approved_ot_hours:
                    event.target
                      .value,
                })
              }
            />

          </AttendanceField>


          <AttendanceField
            label="Remarks"
          >

            <textarea
              rows="4"
              placeholder="Enter remarks..."
              value={
                form.remarks
              }
              onChange={(
                event
              ) =>
                setForm({
                  ...form,
                  remarks:
                    event.target
                      .value,
                })
              }
            />

          </AttendanceField>

        </div>


        <div className="attendance-drawer-footer">

          {selectedRecord && (
            <button
              type="button"
              className="attendance-delete-button"
              onClick={
                deleteAttendance
              }
            >
              <Trash2
                size={17}
              />

              Delete
            </button>
          )}


          <button
            type="button"
            className="attendance-save-button"
            disabled={
              saving
            }
            onClick={
              saveAttendance
            }
          >
            {saving
              ? "Saving..."
              : selectedRecord
                ? "Update Attendance"
                : "Save Attendance"}
          </button>

        </div>

      </aside>

    </div>
  );
}


function AttendanceField({
  label,
  children,
}) {
  return (
    <div className="attendance-field">

      <label>
        {label}
      </label>

      {children}

    </div>
  );
}


function SummaryCard({
  label,
  value,
}) {
  return (
    <div className="attendance-summary-card">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}
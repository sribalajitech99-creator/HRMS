import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  BarChart3,
  CalendarDays,
  Clock3,
  Download,
  FileText,
  FileSpreadsheet,
  RefreshCw,
  Wallet,
  Users,
  Umbrella,
} from "lucide-react";

import api from "../../api/client";
import "./reports.css";

const CATEGORIES = {
  employees: {
    label: "Employee Reports",
    icon: Users,
    reports: [
      {
        key: "employee_master",
        label: "Employee Master Report",
        description:
          "Full employee directory with personal and job details.",
        filters: [
          "company",
          "department",
          "designation",
          "status",
          "search",
        ],
      },
      {
        key: "employee_company_wise",
        label: "Company-wise Employees",
        description:
          "Headcount summary grouped by company.",
        filters: ["company"],
      },
      {
        key: "employee_department_wise",
        label: "Department-wise Employees",
        description:
          "Employee distribution grouped by department.",
        filters: ["company"],
      },
      {
        key: "employee_designation_wise",
        label: "Designation-wise Employees",
        description:
          "Employee distribution grouped by designation.",
        filters: ["company"],
      },
      {
        key: "employee_active",
        label: "Active Employees",
        description: "List of currently active employees.",
        filters: ["company"],
      },
      {
        key: "employee_inactive",
        label: "Inactive Employees",
        description: "List of inactive employees.",
        filters: ["company"],
      },
      {
        key: "employee_exited",
        label: "Exited Employees",
        description: "List of employees who have exited.",
        filters: ["company"],
      },
    ],
  },

  attendance: {
    label: "Attendance Reports",
    icon: CalendarDays,
    reports: [
      {
        key: "attendance_daily",
        label: "Daily Attendance",
        description:
          "Daily punches and status for a selected date.",
        filters: ["date", "company", "department"],
      },
      {
        key: "attendance_monthly_register",
        label: "Monthly Attendance Register",
        description:
          "Day-wise attendance register for a month (P/A/L/HD/H/W).",
        filters: ["year", "month", "company", "department", "employee"],
      },
      {
        key: "attendance_employee_history",
        label: "Employee Attendance History",
        description:
          "Attendance history for a specific employee over a date range.",
        filters: ["employee", "from_date", "to_date"],
        required: ["employee"],
      },
      {
        key: "attendance_present",
        label: "Present Report",
        description:
          "Employees marked present in a month.",
        filters: ["year", "month", "company"],
      },
      {
        key: "attendance_absent",
        label: "Absent Report",
        description:
          "Employees marked absent in a month.",
        filters: ["year", "month", "company"],
      },
      {
        key: "attendance_leave",
        label: "Leave Report",
        description:
          "Employees marked on leave in a month.",
        filters: ["year", "month", "company"],
      },
      {
        key: "attendance_half_day",
        label: "Half-Day Report",
        description:
          "Employees marked half-day in a month.",
        filters: ["year", "month", "company"],
      },
      {
        key: "attendance_holiday_working",
        label: "Holiday Working Report",
        description:
          "Employees who worked on a company holiday.",
        filters: ["year", "month", "company"],
      },
      {
        key: "attendance_weekoff_working",
        label: "Week-Off Working Report",
        description:
          "Employees who worked on a scheduled week-off.",
        filters: ["year", "month", "company"],
      },
      {
        key: "attendance_shift_wise",
        label: "Shift-wise Attendance",
        description:
          "Attendance summary grouped by shift.",
        filters: ["year", "month", "company"],
      },
      {
        key: "attendance_working_hours",
        label: "Working Hours Report",
        description:
          "Total working hours and OT per employee for a month.",
        filters: ["year", "month", "company", "department"],
      },
    ],
  },

  ot: {
    label: "Overtime Reports",
    icon: Clock3,
    reports: [
      {
        key: "ot_daily",
        label: "Daily OT Report",
        description:
          "OT hours for a single day.",
        filters: ["date", "company", "department"],
      },
      {
        key: "ot_monthly",
        label: "Monthly OT Report",
        description:
          "Calculated and approved OT hours per employee for a month.",
        filters: [
          "year",
          "month",
          "company",
          "department",
          "employee",
        ],
      },
      {
        key: "ot_salary",
        label: "OT Salary Report",
        description:
          "OT payment computed from basic salary and approved OT hours.",
        filters: ["year", "month", "company"],
      },
    ],
  },

  payroll: {
    label: "Payroll Reports",
    icon: Wallet,
    reports: [
      {
        key: "payroll_monthly_salary_register",
        label: "Monthly Salary Register",
        description:
          "Full payslip breakdown for a payroll month.",
        filters: [
          "year",
          "month",
          "company",
          "department",
          "employee",
        ],
      },
      {
        key: "payroll_company_register",
        label: "Company Salary Register",
        description:
          "Monthly payroll totals grouped by company.",
        filters: ["year", "month", "company"],
      },
      {
        key: "payroll_department_register",
        label: "Department Salary Register",
        description:
          "Monthly payroll totals grouped by department.",
        filters: ["year", "month", "company"],
      },
      {
        key: "payroll_earnings",
        label: "Earnings Report",
        description:
          "Earnings breakdown per employee for a month.",
        filters: ["year", "month", "company"],
      },
      {
        key: "payroll_deductions",
        label: "Deduction Report",
        description:
          "Deductions per employee for a month.",
        filters: ["year", "month", "company"],
      },
      {
        key: "payroll_net_salary",
        label: "Net Salary Report",
        description:
          "Gross, OT, deductions and net for a month.",
        filters: ["year", "month", "company"],
      },
      {
        key: "payroll_payslip_register",
        label: "Payslip Register",
        description:
          "Register of generated payslips for a month.",
        filters: ["year", "month", "company"],
      },
    ],
  },

  leave: {
    label: "Leave Reports",
    icon: Umbrella,
    reports: [
      {
        key: "leave_employee_history",
        label: "Employee Leave History",
        description:
          "Complete leave history for a specific employee.",
        filters: ["employee"],
        required: ["employee"],
      },
      {
        key: "leave_monthly",
        label: "Monthly Leave Report",
        description:
          "Leave requests overlapping a selected month.",
        filters: ["year", "month", "company"],
      },
      {
        key: "leave_balance",
        label: "Leave Balance Report",
        description:
          "Allocated, used and remaining leave balance per employee.",
        filters: ["company", "employee"],
      },
      {
        key: "leave_type_usage",
        label: "Leave Type Report",
        description:
          "Number of requests grouped by leave type.",
        filters: ["company"],
      },
    ],
  },

  holiday: {
    label: "Holiday Reports",
    icon: CalendarDays,
    reports: [
      {
        key: "holiday_calendar",
        label: "Holiday Calendar",
        description:
          "Company holidays for a selected year.",
        filters: ["year", "company"],
      },
    ],
  },
};

const STATUS_OPTIONS = [
  { value: "ACTIVE", label: "Active" },
  { value: "INACTIVE", label: "Inactive" },
  { value: "EXITED", label: "Exited" },
  { value: "PROBATION", label: "Probation" },
  { value: "NOTICE", label: "Notice" },
];

const EMPLOYMENT_OPTIONS = [
  { value: "PERMANENT", label: "Permanent" },
  { value: "PROBATION", label: "Probation" },
  { value: "CONTRACT", label: "Contract" },
  { value: "INTERN", label: "Intern" },
  { value: "PART_TIME", label: "Part Time" },
  { value: "CONSULTANT", label: "Consultant" },
];

function today() {
  return new Date().toISOString().slice(0, 10);
}

function currentMonth() {
  return new Date().getMonth() + 1;
}

function currentYear() {
  return new Date().getFullYear();
}

export default function ReportsPage() {
  const [activeCategory, setActiveCategory] =
    useState("employees");

  const [report, setReport] = useState(null);

  const [companies, setCompanies] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [employees, setEmployees] = useState([]);

  const [filters, setFilters] = useState({});

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [exiting, setExiting] = useState(false);

  const loadOptions = useCallback(async () => {
    try {
      const [companyRes, departmentRes, employeeRes] =
        await Promise.all([
          api.get("/companies/", {
            params: { page_size: 500 },
          }),
          api.get("/departments/", {
            params: { page_size: 500 },
          }),
          api.get("/employees/", {
            params: { page_size: 500 },
          }),
        ]);

      setCompanies(
        companyRes.data?.results ?? companyRes.data ?? []
      );
      setDepartments(
        departmentRes.data?.results ?? departmentRes.data ?? []
      );
      setEmployees(
        employeeRes.data?.results ?? employeeRes.data ?? []
      );
    } catch {
      // Option loading is best-effort.
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadOptions();
  }, [loadOptions]);

  const selectReport = (item) => {
    setReport(item);

    const defaults = {};

    if (item.filters.includes("year")) {
      defaults.year = currentYear();
    }

    if (item.filters.includes("month")) {
      defaults.month = currentMonth();
    }

    if (item.filters.includes("date")) {
      defaults.date = today();
    }

    setFilters(defaults);
    setResult(null);
    setError("");
  };

  const changeFilter = (name, value) => {
    setFilters((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const buildParams = (format) => {
    const params = new URLSearchParams({
      report: report.key,
    });

    if (format) {
      params.set("export", format);
    }

    Object.entries(filters).forEach(
      ([key, value]) => {
        if (value !== "" && value != null) {
          params.set(key, value);
        }
      }
    );

    return params;
  };

  const runReport = async () => {
    if (!report) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await api.get("/reports/data/", {
        params: buildParams(),
      });

      setResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to generate the report."
      );
    } finally {
      setLoading(false);
    }
  };

  const downloadExport = async (format) => {
    if (!report || exiting) {
      return;
    }

    setExiting(true);

    try {
      const token = localStorage.getItem("access_token");

      const url = `${api.defaults.baseURL}/reports/data/?${buildParams(
        format
      ).toString()}`;

      const response = await fetch(url, {
        headers: token
          ? { Authorization: `Bearer ${token}` }
          : {},
      });

      if (!response.ok) {
        setError(
          "Unable to export the report. Please try again."
        );
        return;
      }

      const blob = await response.blob();

      const objectUrl = URL.createObjectURL(blob);

      const link = document.createElement("a");

      link.href = objectUrl;
      link.download = `report.${format === "pdf" ? "pdf" : "xlsx"}`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      URL.revokeObjectURL(objectUrl);
    } catch {
      setError("Unable to export the report. Please try again.");
    } finally {
      setExiting(false);
    }
  };

  const usedFilters = useMemo(() => {
    if (!report) {
      return [];
    }

    return report.filters ?? [];
  }, [report]);

  return (
    <div className="reports-page">
      <div className="reports-header">
        <div>
          <h1>Reports</h1>
          <p>
            Generate operational and analytical report for your
            organization.
          </p>
        </div>

        {result && (
          <div className="reports-export-actions">
            <button
              type="button"
              className="reports-export-btn"
              onClick={() => downloadExport("xlsx")}
              disabled={exiting}
            >
              <FileSpreadsheet size={16} />
              Export Excel
            </button>

            <button
              type="button"
              className="reports-export-btn reports-export-pdf"
              onClick={() => downloadExport("pdf")}
              disabled={exiting}
            >
              <FileText size={16} />
              Export PDF
            </button>

            <button
              type="button"
              className="reports-refresh-btn"
              onClick={runReport}
              disabled={loading}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>
        )}
      </div>

      <div className="reports-layout">
        {/* CATEGORY + REPORT LIST */}
        <div className="reports-side">
          {Object.entries(CATEGORIES).map(
            ([key, category]) => {
              const Icon = category.icon;

              return (
                <div
                  className="reports-category"
                  key={key}
                >
                  <button
                    type="button"
                    className={`reports-category-toggle ${
                      activeCategory === key
                        ? "active"
                        : ""
                    }`}
                    onClick={() => {
                      setActiveCategory(key);
                      setReport(null);
                      setResult(null);
                      setError("");
                    }}
                  >
                    <Icon size={17} />
                    <span>{category.label}</span>
                    <small>{category.reports.length}</small>
                  </button>

                  {activeCategory === key && (
                    <div className="reports-list">
                      {category.reports.map((item) => (
                        <button
                          type="button"
                          key={item.key}
                          className={`reports-item ${
                            report?.key === item.key
                              ? "active"
                              : ""
                          }`}
                          onClick={() => selectReport(item)}
                        >
                          <BarChart3 size={15} />
                          <span>{item.label}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            }
          )}
        </div>

        {/* REPORT VIEW */}
        <div className="reports-main">
          {!report ? (
            <div className="reports-empty">
              <FileText size={40} />
              <h5>Select a report</h5>
              <p>
                Choose a report from the left to configure
                filters and generate output.
              </p>
            </div>
          ) : (
            <>
              <div className="reports-config">
                <div className="reports-config-heading">
                  <div>
                    <h3>{report.label}</h3>
                    <p>{report.description}</p>
                  </div>
                </div>

                <div className="reports-filters">
                  {usedFilters.includes("company") && (
                    <label>
                      <span>Company</span>
                      <select
                        value={filters.company || ""}
                        onChange={(e) =>
                          changeFilter("company", e.target.value)
                        }
                      >
                        <option value="">All Companies</option>
                        {companies.map((item) => (
                          <option value={item.id} key={item.id}>
                            {item.code} - {item.name}
                          </option>
                        ))}
                      </select>
                    </label>
                  )}

                  {usedFilters.includes("department") && (
                    <label>
                      <span>Department</span>
                      <select
                        value={filters.department || ""}
                        onChange={(e) =>
                          changeFilter("department", e.target.value)
                        }
                      >
                        <option value="">All Departments</option>
                        {departments.map((item) => (
                          <option value={item.id} key={item.id}>
                            {item.name}
                          </option>
                        ))}
                      </select>
                    </label>
                  )}

                  {usedFilters.includes("designation") && (
                    <label>
                      <span>Designation</span>
                      <select
                        value={filters.designation || ""}
                        onChange={(e) =>
                          changeFilter("designation", e.target.value)
                        }
                      >
                        <option value="">All Designations</option>
                        {companies.map((item) => (
                          <option value={item.id} key={`d-${item.id}`}>
                            {item.name}
                          </option>
                        ))}
                      </select>
                    </label>
                  )}

                  {usedFilters.includes("employee") && (
                    <label>
                      <span>Employee</span>
                      <select
                        value={filters.employee || ""}
                        onChange={(e) =>
                          changeFilter("employee", e.target.value)
                        }
                      >
                        <option value="">Select Employee</option>
                        {employees.map((item) => (
                          <option value={item.id} key={item.id}>
                            {item.employee_code} - {item.first_name}{" "}
                            {item.last_name || ""}
                          </option>
                        ))}
                      </select>
                    </label>
                  )}

                  {usedFilters.includes("status") && (
                    <label>
                      <span>Status</span>
                      <select
                        value={filters.status || ""}
                        onChange={(e) =>
                          changeFilter("status", e.target.value)
                        }
                      >
                        <option value="">All Statuses</option>
                        {STATUS_OPTIONS.map((item) => (
                          <option value={item.value} key={item.value}>
                            {item.label}
                          </option>
                        ))}
                      </select>
                    </label>
                  )}

                  {usedFilters.includes("employment_type") && (
                    <label>
                      <span>Employment Type</span>
                      <select
                        value={filters.employment_type || ""}
                        onChange={(e) =>
                          changeFilter("employment_type", e.target.value)
                        }
                      >
                        <option value="">All Types</option>
                        {EMPLOYMENT_OPTIONS.map((item) => (
                          <option value={item.value} key={item.value}>
                            {item.label}
                          </option>
                        ))}
                      </select>
                    </label>
                  )}

                  {usedFilters.includes("search") && (
                    <label>
                      <span>Search</span>
                      <input
                        type="text"
                        value={filters.search || ""}
                        placeholder="Employee code..."
                        onChange={(e) =>
                          changeFilter("search", e.target.value)
                        }
                      />
                    </label>
                  )}

                  {usedFilters.includes("year") && (
                    <label>
                      <span>Year</span>
                      <input
                        type="number"
                        min="2000"
                        max="2100"
                        value={filters.year || currentYear()}
                        onChange={(e) =>
                          changeFilter("year", e.target.value)
                        }
                      />
                    </label>
                  )}

                  {usedFilters.includes("month") && (
                    <label>
                      <span>Month</span>
                      <select
                        value={filters.month || currentMonth()}
                        onChange={(e) =>
                          changeFilter("month", e.target.value)
                        }
                      >
                        {[
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
                        ].map((name, index) => (
                          <option value={index + 1} key={index + 1}>
                            {name}
                          </option>
                        ))}
                      </select>
                    </label>
                  )}

                  {usedFilters.includes("date") && (
                    <label>
                      <span>Date</span>
                      <input
                        type="date"
                        value={filters.date || today()}
                        onChange={(e) =>
                          changeFilter("date", e.target.value)
                        }
                      />
                    </label>
                  )}

                  {usedFilters.includes("from_date") && (
                    <label>
                      <span>From Date</span>
                      <input
                        type="date"
                        value={filters.from_date || ""}
                        onChange={(e) =>
                          changeFilter("from_date", e.target.value)
                        }
                      />
                    </label>
                  )}

                  {usedFilters.includes("to_date") && (
                    <label>
                      <span>To Date</span>
                      <input
                        type="date"
                        value={filters.to_date || ""}
                        onChange={(e) =>
                          changeFilter("to_date", e.target.value)
                        }
                      />
                    </label>
                  )}

                  <div className="reports-run">
                    <button
                      type="button"
                      className="reports-run-btn"
                      onClick={runReport}
                      disabled={loading}
                    >
                      <Download size={16} />
                      {loading ? "Running..." : "Generate Report"}
                    </button>
                  </div>
                </div>
              </div>

              {error && (
                <div className="reports-error">{error}</div>
              )}

              {result && (
                <div className="reports-result">
                  <div className="reports-result-heading">
                    <div>
                      <h3>{result.title}</h3>
                      <span className="reports-period">
                        {result.period}
                      </span>
                    </div>

                    <span className="reports-count">
                      {result.rows.length} row
                      {result.rows.length === 1 ? "" : "s"}
                    </span>
                  </div>

                  <div className="reports-table-wrapper">
                    <table className="reports-table">
                      <thead>
                        <tr>
                          {result.columns.map(
                            (column, index) => (
                              <th key={index}>{column}</th>
                            )
                          )}
                        </tr>
                      </thead>
                      <tbody>
                        {result.rows.length ? (
                          result.rows.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                              {row.map((cell, cellIndex) => (
                                <td key={cellIndex}>
                                  {cell === null ||
                                  cell === undefined ||
                                  cell === ""
                                    ? "—"
                                    : cell}
                                </td>
                              ))}
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td
                              colSpan={result.columns.length}
                              className="reports-table-empty"
                            >
                              No records found for the selected
                              filters.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  {Object.keys(result.totals || {}).length >
                    0 && (
                    <div className="reports-totals">
                      {Object.entries(result.totals).map(
                        ([key, value]) => (
                          <div className="reports-total" key={key}>
                            <span>
                              {key
                                .replace(/_/g, " ")
                                .replace(/\b\w/g, (c) =>
                                  c.toUpperCase()
                                )}
                            </span>
                            <strong>{value}</strong>
                          </div>
                        )
                      )}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

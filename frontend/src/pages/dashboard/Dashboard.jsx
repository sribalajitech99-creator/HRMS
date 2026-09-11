import {
  BriefcaseBusiness,
  Building2,
  CalendarCheck,
  Clock3,
  IndianRupee,
  UserCheck,
  UserMinus,
  Users,
  WalletCards,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import api from "../../api/client";

import "./dashboard.css";

function money(value) {
  return new Intl.NumberFormat(
    "en-IN",
    {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }
  ).format(
    Number(value || 0)
  );
}

function MetricCard({
  label,
  value,
  helper,
  icon: Icon,
}) {
  return (
    <div className="dashboard-card metric-card">
      <div>
        <p className="metric-label">
          {label}
        </p>

        <h2 className="metric-value">
          {value}
        </h2>

        <span className="metric-helper">
          {helper}
        </span>
      </div>

      <div className="metric-icon">
        <Icon size={22} />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const load = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get(
        "/reports/dashboard/"
      );

      setData(response.data);
    } catch {
      setError(
        "Unable to load dashboard."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-loading">
        Loading dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger">
        {error}
      </div>
    );
  }

  const workforce =
    data?.workforce || {};

  const attendance =
    data?.attendance || {};

  const leave =
    data?.leave || {};

  const payroll =
    data?.payroll || {};

  const recruitment =
    data?.recruitment || {};

  return (
    <div className="professional-dashboard">
      <div className="dashboard-heading">
        <div>
          <h1>
            Dashboard
          </h1>

          <p>
            Workforce performance and HR
            operations overview.
          </p>
        </div>
      </div>

      <div className="dashboard-metrics">
        <MetricCard
          label="Active Employees"
          value={
            workforce.active || 0
          }
          helper={`${workforce.total || 0} total employees`}
          icon={Users}
        />

        <MetricCard
          label="Present Today"
          value={
            attendance.present || 0
          }
          helper={`${attendance.rate || 0}% attendance`}
          icon={UserCheck}
        />

        <MetricCard
          label="Absent Today"
          value={
            attendance.absent || 0
          }
          helper="Employees absent today"
          icon={UserMinus}
        />

        <MetricCard
          label="Late Today"
          value={
            attendance.late || 0
          }
          helper="Late arrivals"
          icon={Clock3}
        />

        <MetricCard
          label="Pending Leaves"
          value={
            leave.pending || 0
          }
          helper="Requires HR action"
          icon={CalendarCheck}
        />

        <MetricCard
          label="Monthly Payroll"
          value={money(
            payroll.net
          )}
          helper="Current payroll net cost"
          icon={IndianRupee}
        />
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card large">
          <div className="card-heading">
            <div>
              <h3>
                Attendance Overview
              </h3>

              <p>
                Last 7 days
              </p>
            </div>
          </div>

          <div className="attendance-bars">
            {data.attendance_trend?.map(
              (item) => {
                const total =
                  item.present +
                  item.absent +
                  item.late;

                const presentWidth =
                  total
                    ? (
                        item.present /
                        total
                      ) *
                      100
                    : 0;

                return (
                  <div
                    className="attendance-day"
                    key={item.date}
                  >
                    <span>
                      {item.date}
                    </span>

                    <div className="attendance-progress">
                      <div
                        className="attendance-present"
                        style={{
                          width: `${presentWidth}%`,
                        }}
                      />
                    </div>

                    <strong>
                      {item.present}
                    </strong>
                  </div>
                );
              }
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-heading">
            <div>
              <h3>
                Workforce by Company
              </h3>

              <p>
                Employee distribution
              </p>
            </div>

            <Building2 size={20} />
          </div>

          <div className="summary-list">
            {data.company_distribution?.map(
              (item) => (
                <div
                  className="summary-row"
                  key={
                    item.company__id
                  }
                >
                  <span>
                    {
                      item.company__name
                    }
                  </span>

                  <strong>
                    {item.total}
                  </strong>
                </div>
              )
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-heading">
            <div>
              <h3>
                Today's Attendance
              </h3>

              <p>
                Current workforce status
              </p>
            </div>

            <CalendarCheck
              size={20}
            />
          </div>

          <div className="dashboard-stat-list">
            <div>
              <span>
                Present
              </span>

              <strong>
                {
                  attendance.present ||
                  0
                }
              </strong>
            </div>

            <div>
              <span>
                Absent
              </span>

              <strong>
                {
                  attendance.absent ||
                  0
                }
              </strong>
            </div>

            <div>
              <span>
                Late
              </span>

              <strong>
                {attendance.late || 0}
              </strong>
            </div>

            <div>
              <span>
                On Leave
              </span>

              <strong>
                {
                  attendance.on_leave ||
                  0
                }
              </strong>
            </div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-heading">
            <div>
              <h3>
                Payroll Snapshot
              </h3>

              <p>
                Current month
              </p>
            </div>

            <WalletCards size={20} />
          </div>

          <div className="dashboard-stat-list">
            <div>
              <span>
                Gross Salary
              </span>

              <strong>
                {money(
                  payroll.gross
                )}
              </strong>
            </div>

            <div>
              <span>
                Overtime
              </span>

              <strong>
                {money(
                  payroll.overtime
                )}
              </strong>
            </div>

            <div>
              <span>
                PF Deductions
              </span>

              <strong>
                {money(
                  payroll.deductions
                )}
              </strong>
            </div>

            <div>
              <span>
                Net Payroll
              </span>

              <strong>
                {money(
                  payroll.net
                )}
              </strong>
            </div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-heading">
            <div>
              <h3>
                Recruitment
              </h3>

              <p>
                Hiring pipeline
              </p>
            </div>

            <BriefcaseBusiness
              size={20}
            />
          </div>

          <div className="dashboard-stat-list">
            <div>
              <span>
                Open Jobs
              </span>

              <strong>
                {
                  recruitment.open_jobs ||
                  0
                }
              </strong>
            </div>

            <div>
              <span>
                Candidates
              </span>

              <strong>
                {
                  recruitment.candidates ||
                  0
                }
              </strong>
            </div>

            <div>
              <span>
                Interviews
              </span>

              <strong>
                {
                  recruitment.interviews ||
                  0
                }
              </strong>
            </div>

            <div>
              <span>
                Selected
              </span>

              <strong>
                {
                  recruitment.selected ||
                  0
                }
              </strong>
            </div>
          </div>
        </div>

        <div className="dashboard-card large">
          <div className="card-heading">
            <div>
              <h3>
                Department Headcount
              </h3>

              <p>
                Workforce distribution by
                department
              </p>
            </div>
          </div>

          <div className="department-list">
            {data.department_distribution?.map(
              (department) => (
                <div
                  className="department-row"
                  key={
                    department.department__name ||
                    "Unassigned"
                  }
                >
                  <span>
                    {department.department__name ||
                      "Unassigned"}
                  </span>

                  <div className="department-line">
                    <div
                      style={{
                        width: `${Math.min(
                          department.total *
                            5,
                          100
                        )}%`,
                      }}
                    />
                  </div>

                  <strong>
                    {
                      department.total
                    }
                  </strong>
                </div>
              )
            )}
          </div>
        </div>

        <div className="dashboard-card large">
          <div className="card-heading">
            <div>
              <h3>
                Recent HR Activity
              </h3>

              <p>
                Recent employee attendance
                updates
              </p>
            </div>
          </div>

          <div className="activity-list">
            {data.recent_activity?.length ? (
              data.recent_activity.map(
                (item, index) => (
                  <div
                    className="activity-item"
                    key={`${item.employee_code}-${index}`}
                  >
                    <div className="activity-avatar">
                      {item.employee_name
                        ?.charAt(0)
                        ?.toUpperCase()}
                    </div>

                    <div className="activity-content">
                      <strong>
                        {
                          item.employee_name
                        }
                      </strong>

                      <span>
                        {
                          item.employee_code
                        }{" "}
                        ·{" "}
                        {
                          item.activity
                        }
                      </span>
                    </div>

                    <small>
                      {item.date}
                    </small>
                  </div>
                )
              )
            ) : (
              <p className="text-muted">
                No recent activity.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
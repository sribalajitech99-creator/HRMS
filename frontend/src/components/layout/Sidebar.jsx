import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Building2,
  Users,
  CalendarDays,
  Clock3,
  Wallet,
  BriefcaseBusiness,
  BarChart3,
  Settings,
  ShieldCheck,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";

function Sidebar({ mobileOpen = false, onMobileClose }) {
  const [collapsed, setCollapsed] = useState(() => {
    return localStorage.getItem("hrms-sidebar-collapsed") === "true";
  });

  const [openMenu, setOpenMenu] = useState("organization");

  useEffect(() => {
    localStorage.setItem(
      "hrms-sidebar-collapsed",
      collapsed.toString()
    );
  }, [collapsed]);

  const toggleMenu = (menu) => {
    if (collapsed) {
      setCollapsed(false);
      setOpenMenu(menu);
      return;
    }

    setOpenMenu((current) => (current === menu ? null : menu));
  };

  const menuButtonClass = (menu) =>
    `sidebar-link sidebar-menu-button ${
      openMenu === menu ? "menu-open" : ""
    }`;

  return (
    <aside
      className={`hrms-sidebar ${
        collapsed ? "sidebar-collapsed" : ""
      } ${
        mobileOpen ? "mobile-open" : ""
      }`}
    >
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <ShieldCheck size={24} />
        </div>

        {!collapsed && (
          <div className="sidebar-brand-text">
            <h5>Enterprise HRMS</h5>
            <span>People Management</span>
          </div>
        )}

        <button
          type="button"
          className="sidebar-collapse-btn"
          onClick={() => setCollapsed(!collapsed)}
          aria-label="Toggle sidebar"
        >
          {collapsed ? (
            <ChevronRight size={17} />
          ) : (
            <ChevronLeft size={17} />
          )}
        </button>

        <button
          type="button"
          className="sidebar-mobile-close"
          onClick={onMobileClose}
          aria-label="Close menu"
        >
          <X size={18} />
        </button>
      </div>

      <div className="sidebar-scroll">
        <nav className="sidebar-nav">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `sidebar-link ${
                isActive ? "active" : ""
              }`
            }
          >
            <LayoutDashboard size={18} />
            {!collapsed && <span>Dashboard</span>}
          </NavLink>

          {!collapsed && (
            <div className="sidebar-section-title">
              Organization
            </div>
          )}

          <button
            type="button"
            className={menuButtonClass("organization")}
            onClick={() => toggleMenu("organization")}
          >
            <Building2 size={18} />

            {!collapsed && (
              <>
                <span>Organization</span>
                <ChevronDown
                  size={15}
                  className={`sidebar-chevron ${
                    openMenu === "organization"
                      ? "rotate"
                      : ""
                  }`}
                />
              </>
            )}
          </button>

          {!collapsed &&
            openMenu === "organization" && (
              <div className="sidebar-submenu">
                <NavLink to="/companies">
                  Companies
                </NavLink>

                <NavLink to="/departments">
                  Departments
                </NavLink>

                <NavLink to="/designations">
                  Designations
                </NavLink>
              </div>
            )}

          {!collapsed && (
            <div className="sidebar-section-title">
              People
            </div>
          )}

          <NavLink to="/employees" className="sidebar-link">
            <Users size={18} />
            {!collapsed && <span>Employees</span>}
          </NavLink>

          {!collapsed && (
            <div className="sidebar-section-title">
              Time Management
            </div>
          )}

          <button
            type="button"
            className={menuButtonClass("time")}
            onClick={() => toggleMenu("time")}
          >
            <CalendarDays size={18} />

            {!collapsed && (
              <>
                <span>Attendance</span>
                <ChevronDown
                  size={15}
                  className={`sidebar-chevron ${
                    openMenu === "time" ? "rotate" : ""
                  }`}
                />
              </>
            )}
          </button>

          {!collapsed && openMenu === "time" && (
            <div className="sidebar-submenu">
              <NavLink to="/attendance">
                Daily Attendance
              </NavLink>

              <NavLink to="/attendance/monthly">
                Monthly Attendance
              </NavLink>

              <NavLink to="/attendance/regularization">
                Regularization
              </NavLink>
            </div>
          )}

          <NavLink to="/shifts" className="sidebar-link">
            <Clock3 size={18} />
            {!collapsed && <span>Shifts</span>}
          </NavLink>

          {!collapsed && (
            <div className="sidebar-section-title">
              Payroll
            </div>
          )}

          <button
            type="button"
            className={menuButtonClass("payroll")}
            onClick={() => toggleMenu("payroll")}
          >
            <Wallet size={18} />

            {!collapsed && (
              <>
                <span>Payroll</span>
                <ChevronDown
                  size={15}
                  className={`sidebar-chevron ${
                    openMenu === "payroll"
                      ? "rotate"
                      : ""
                  }`}
                />
              </>
            )}
          </button>

          {!collapsed &&
            openMenu === "payroll" && (
              <div className="sidebar-submenu">
                <NavLink to="/payroll">
                  Payroll Dashboard
                </NavLink>

                <NavLink to="/payroll/salary-structures">
                  Salary Structures
                </NavLink>

                <NavLink to="/payroll/payslips">
                  Payslips
                </NavLink>
              </div>
            )}

          {!collapsed && (
            <div className="sidebar-section-title">
              Recruitment
            </div>
          )}

          <NavLink
            to="/recruitment"
            className="sidebar-link"
          >
            <BriefcaseBusiness size={18} />
            {!collapsed && <span>Recruitment</span>}
          </NavLink>

          {!collapsed && (
            <div className="sidebar-section-title">
              Analytics
            </div>
          )}

          <NavLink
            to="/reports"
            className="sidebar-link"
          >
            <BarChart3 size={18} />
            {!collapsed && <span>Reports</span>}
          </NavLink>

          {!collapsed && (
            <div className="sidebar-section-title">
              Administration
            </div>
          )}

          <NavLink
            to="/settings"
            className="sidebar-link"
          >
            <Settings size={18} />
            {!collapsed && <span>Settings</span>}
          </NavLink>
        </nav>
      </div>
    </aside>
  );
}

export default Sidebar;
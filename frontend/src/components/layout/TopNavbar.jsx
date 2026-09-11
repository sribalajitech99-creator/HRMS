import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Bell,
  BriefcaseBusiness,
  Building2,
  ChevronDown,
  LogOut,
  Menu,
  Plus,
  Search,
  User,
  UserPlus,
  Users,
  X,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import api from "../../api/client";


export default function Topbar({ onMenuToggle }) {
  const navigate = useNavigate();

  /* =========================================================
     STATE
  ========================================================= */

  const [user, setUser] = useState(null);

  const [companies, setCompanies] = useState([]);

  const [selectedCompany, setSelectedCompany] = useState(
    () => localStorage.getItem("selected_company") || ""
  );

  const [search, setSearch] = useState("");

  const [searchLoading, setSearchLoading] =
    useState(false);

  const [showSearch, setShowSearch] =
    useState(false);

  const [searchResults, setSearchResults] =
    useState({
      employees: [],
      departments: [],
      designations: [],
    });

  const [quickAddOpen, setQuickAddOpen] =
    useState(false);

  const [notificationOpen, setNotificationOpen] =
    useState(false);

  const [profileOpen, setProfileOpen] =
    useState(false);

  const [notifications, setNotifications] =
    useState([]);

  const [notificationLoading, setNotificationLoading] =
    useState(false);


  /* =========================================================
     LOAD USER
  ========================================================= */

  useEffect(() => {
    async function loadUser() {
      try {
        const response =
          await api.get("/auth/me/");

        setUser(response.data);
      } catch (error) {
        console.error(
          "Unable to load current user:",
          error
        );
      }
    }

    loadUser();
  }, []);


  /* =========================================================
     LOAD COMPANIES
  ========================================================= */

  useEffect(() => {
    async function loadCompanies() {
      try {
        const response =
          await api.get("/companies/", {
            params: {
              page_size: 200,
            },
          });

        const data =
          response.data?.results ??
          response.data ??
          [];

        setCompanies(
          Array.isArray(data)
            ? data
            : []
        );
      } catch (error) {
        console.error(
          "Unable to load companies:",
          error
        );
      }
    }

    loadCompanies();
  }, []);


  /* =========================================================
     GLOBAL SEARCH
  ========================================================= */

  useEffect(() => {
    const query =
      search.trim();

    if (query.length < 2) {
      setShowSearch(false);

      setSearchResults({
        employees: [],
        departments: [],
        designations: [],
      });

      return;
    }

    const timer =
      setTimeout(
        async () => {
          setSearchLoading(true);

          try {
            const responses =
              await Promise.allSettled([
                api.get(
                  "/employees/",
                  {
                    params: {
                      search: query,
                      page_size: 5,
                    },
                  }
                ),

                api.get(
                  "/departments/",
                  {
                    params: {
                      search: query,
                      page_size: 5,
                    },
                  }
                ),

                api.get(
                  "/designations/",
                  {
                    params: {
                      search: query,
                      page_size: 5,
                    },
                  }
                ),
              ]);

            const getItems = (
              result
            ) => {
              if (
                result.status !==
                "fulfilled"
              ) {
                return [];
              }

              const data =
                result.value.data;

              if (
                Array.isArray(data)
              ) {
                return data.slice(
                  0,
                  5
                );
              }

              return (
                data?.results ?? []
              ).slice(0, 5);
            };

            setSearchResults({
              employees:
                getItems(
                  responses[0]
                ),

              departments:
                getItems(
                  responses[1]
                ),

              designations:
                getItems(
                  responses[2]
                ),
            });

            setShowSearch(true);

          } catch (error) {
            console.error(
              "Global search error:",
              error
            );

          } finally {
            setSearchLoading(false);
          }
        },
        300
      );

    return () =>
      clearTimeout(timer);

  }, [search]);


  /* =========================================================
     USER DISPLAY
  ========================================================= */

  const fullName =
    user?.full_name ||
    `${user?.first_name || ""} ${
      user?.last_name || ""
    }`.trim() ||
    user?.username ||
    "Admin User";

  const roleName =
    user?.role_name ||
    user?.role ||
    "Super Admin";

  const email =
    user?.email ||
    user?.work_email ||
    "";

  const initials =
    useMemo(() => {
      return (
        fullName
          .split(" ")
          .filter(Boolean)
          .slice(0, 2)
          .map(
            (word) =>
              word[0]
          )
          .join("")
          .toUpperCase() ||
        "AD"
      );
    }, [fullName]);


  /* =========================================================
     CLOSE TOPBAR POPUPS
  ========================================================= */

  const closeTopbarMenus = () => {
    setQuickAddOpen(false);
    setShowSearch(false);
  };


  /* =========================================================
     QUICK ADD
  ========================================================= */

  const quickAdd = (
    path
  ) => {
    closeTopbarMenus();

    navigate(
      `${path}?create=1`
    );
  };


  /* =========================================================
     SEARCH RESULT
  ========================================================= */

  const openSearchResult = (
    path,
    value
  ) => {
    setSearch("");

    setShowSearch(false);

    navigate(
      `${path}?search=${encodeURIComponent(
        value
      )}`
    );
  };


  /* =========================================================
     COMPANY
  ========================================================= */

  const changeCompany = (
    event
  ) => {
    const value =
      event.target.value;

    setSelectedCompany(
      value
    );

    localStorage.setItem(
      "selected_company",
      value
    );

    window.dispatchEvent(
      new CustomEvent(
        "hrmsCompanyChanged",
        {
          detail: {
            companyId:
              value,
          },
        }
      )
    );
  };


  /* =========================================================
     NOTIFICATION
  ========================================================= */

  const showNotifications =
    async () => {
      setProfileOpen(false);
      setQuickAddOpen(false);
      setShowSearch(false);

      setNotificationOpen(true);
      setNotificationLoading(true);

      try {
        const response =
          await api.get(
            "/notifications/",
            {
              params: {
                page_size: 50,
              },
            }
          );

        const data =
          response.data?.results ??
          response.data ??
          [];

        setNotifications(
          Array.isArray(data)
            ? data
            : []
        );

      } catch (error) {
        /*
          Notification API may not
          exist in backend yet.
        */

        console.log(
          "Notification API is not available yet."
        );

        setNotifications([]);

      } finally {
        setNotificationLoading(
          false
        );
      }
    };


  /* =========================================================
     PROFILE
  ========================================================= */

  const showProfile = () => {
    setNotificationOpen(
      false
    );

    setQuickAddOpen(
      false
    );

    setShowSearch(
      false
    );

    setProfileOpen(
      true
    );
  };


  /* =========================================================
     LOGOUT
  ========================================================= */

  const logout = () => {
    localStorage.removeItem(
      "access"
    );

    localStorage.removeItem(
      "refresh"
    );

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "refresh_token"
    );

    localStorage.removeItem(
      "user"
    );

    navigate(
      "/login",
      {
        replace: true,
      }
    );
  };


  /* =========================================================
     SEARCH COUNT
  ========================================================= */

  const resultCount =
    searchResults.employees.length +
    searchResults.departments.length +
    searchResults.designations.length;


  /* =========================================================
     UNREAD COUNT
  ========================================================= */

  const unreadCount =
    notifications.filter(
      (item) =>
        item.is_read === false
    ).length;


  /* =========================================================
     UI
  ========================================================= */

  return (
    <>
      <header className="hrms-topbar">

        {/* =================================================
            MOBILE MENU TOGGLE
        ================================================== */}

        <button
          type="button"
          className="topbar-menu-toggle"
          onClick={onMenuToggle}
          aria-label="Open menu"
        >
          <Menu size={22} />
        </button>

        {/* =================================================
            GLOBAL SEARCH
        ================================================== */}

        <div className="topbar-search-container">

          <div className="topbar-search">

            <Search
              size={18}
            />

            <input
              type="text"
              value={search}
              placeholder="Search employees, departments..."
              onFocus={() => {
                if (
                  search.trim()
                    .length >= 2
                ) {
                  setShowSearch(
                    true
                  );
                }
              }}
              onChange={(
                event
              ) => {
                setSearch(
                  event.target.value
                );
              }}
            />

            {search && (
              <button
                type="button"
                className="topbar-search-clear"
                onClick={() => {
                  setSearch("");
                  setShowSearch(
                    false
                  );
                }}
              >
                <X
                  size={15}
                />
              </button>
            )}

          </div>


          {/* SEARCH RESULT PANEL */}

          {showSearch && (

            <div className="global-search-panel">

              {searchLoading ? (

                <div className="topbar-empty-state">
                  Searching...
                </div>

              ) : resultCount ===
                0 ? (

                <div className="topbar-empty-state">
                  No matching records
                  found.
                </div>

              ) : (
                <>

                  {/* EMPLOYEES */}

                  {searchResults
                    .employees
                    .length > 0 && (

                    <div className="search-group">

                      <div className="search-group-heading">
                        Employees
                      </div>

                      {searchResults.employees.map(
                        (
                          employee
                        ) => {

                          const employeeName =
                            `${
                              employee.first_name ||
                              ""
                            } ${
                              employee.last_name ||
                              ""
                            }`.trim();

                          return (

                            <button
                              type="button"
                              className="global-search-item"
                              key={
                                employee.id
                              }
                              onClick={() =>
                                openSearchResult(
                                  "/employees",
                                  employee.employee_code ||
                                    employeeName
                                )
                              }
                            >

                              <span className="global-search-icon">
                                <User
                                  size={
                                    17
                                  }
                                />
                              </span>

                              <span className="global-search-text">

                                <strong>
                                  {employeeName ||
                                    "Employee"}
                                </strong>

                                <small>
                                  {employee.employee_code ||
                                    ""}

                                  {employee.department_name
                                    ? ` • ${employee.department_name}`
                                    : ""}
                                </small>

                              </span>

                            </button>

                          );
                        }
                      )}

                    </div>

                  )}


                  {/* DEPARTMENTS */}

                  {searchResults
                    .departments
                    .length > 0 && (

                    <div className="search-group">

                      <div className="search-group-heading">
                        Departments
                      </div>

                      {searchResults.departments.map(
                        (
                          department
                        ) => (

                          <button
                            type="button"
                            className="global-search-item"
                            key={
                              department.id
                            }
                            onClick={() =>
                              openSearchResult(
                                "/departments",
                                department.name
                              )
                            }
                          >

                            <span className="global-search-icon">
                              <Users
                                size={
                                  17
                                }
                              />
                            </span>

                            <span className="global-search-text">

                              <strong>
                                {
                                  department.name
                                }
                              </strong>

                              <small>
                                {department.company_name ||
                                  department.code ||
                                  ""}
                              </small>

                            </span>

                          </button>

                        )
                      )}

                    </div>

                  )}


                  {/* DESIGNATIONS */}

                  {searchResults
                    .designations
                    .length > 0 && (

                    <div className="search-group">

                      <div className="search-group-heading">
                        Designations
                      </div>

                      {searchResults.designations.map(
                        (
                          designation
                        ) => (

                          <button
                            type="button"
                            className="global-search-item"
                            key={
                              designation.id
                            }
                            onClick={() =>
                              openSearchResult(
                                "/designations",
                                designation.name
                              )
                            }
                          >

                            <span className="global-search-icon">
                              <BriefcaseBusiness
                                size={
                                  17
                                }
                              />
                            </span>

                            <span className="global-search-text">

                              <strong>
                                {
                                  designation.name
                                }
                              </strong>

                              <small>
                                {designation.department_name ||
                                  designation.company_name ||
                                  designation.code ||
                                  ""}
                              </small>

                            </span>

                          </button>

                        )
                      )}

                    </div>

                  )}

                </>
              )}

            </div>

          )}

        </div>


        {/* =================================================
            RIGHT AREA
        ================================================== */}

        <div className="topbar-actions">


          {/* COMPANY */}

          <select
            value={
              selectedCompany
            }
            onChange={
              changeCompany
            }
            className="form-select topbar-select"
          >

            <option value="">
              All Companies
            </option>

            {companies.map(
              (company) => (

                <option
                  value={
                    company.id
                  }
                  key={
                    company.id
                  }
                >
                  {company.code
                    ? `${company.code} - ${company.name}`
                    : company.name}
                </option>

              )
            )}

          </select>


          {/* =================================================
              QUICK ADD
          ================================================== */}

          <div className="quick-add-container">

            <button
              type="button"
              className="btn btn-success topbar-add-btn"
              onClick={() => {
                setQuickAddOpen(
                  (
                    current
                  ) =>
                    !current
                );

                setProfileOpen(
                  false
                );

                setNotificationOpen(
                  false
                );

                setShowSearch(
                  false
                );
              }}
            >

              <Plus
                size={17}
              />

              <span>
                Quick Add
              </span>

              <ChevronDown
                size={14}
              />

            </button>


            {quickAddOpen && (

              <div className="quick-add-dropdown">

                <div className="quick-add-title">
                  Quick Add
                </div>


                <button
                  type="button"
                  onClick={() =>
                    quickAdd(
                      "/employees"
                    )
                  }
                >

                  <span className="quick-add-icon">
                    <UserPlus
                      size={
                        18
                      }
                    />
                  </span>

                  <span>
                    <strong>
                      Employee
                    </strong>

                    <small>
                      Add employee
                      record
                    </small>
                  </span>

                </button>


                <button
                  type="button"
                  onClick={() =>
                    quickAdd(
                      "/companies"
                    )
                  }
                >

                  <span className="quick-add-icon">
                    <Building2
                      size={
                        18
                      }
                    />
                  </span>

                  <span>
                    <strong>
                      Company
                    </strong>

                    <small>
                      Add company
                    </small>
                  </span>

                </button>


                <button
                  type="button"
                  onClick={() =>
                    quickAdd(
                      "/departments"
                    )
                  }
                >

                  <span className="quick-add-icon">
                    <Users
                      size={
                        18
                      }
                    />
                  </span>

                  <span>
                    <strong>
                      Department
                    </strong>

                    <small>
                      Add department
                    </small>
                  </span>

                </button>


                <button
                  type="button"
                  onClick={() =>
                    quickAdd(
                      "/designations"
                    )
                  }
                >

                  <span className="quick-add-icon">
                    <BriefcaseBusiness
                      size={
                        18
                      }
                    />
                  </span>

                  <span>
                    <strong>
                      Designation
                    </strong>

                    <small>
                      Add designation
                    </small>
                  </span>

                </button>

              </div>

            )}

          </div>


          {/* =================================================
              NOTIFICATION
          ================================================== */}

          <button
            type="button"
            className="topbar-icon-btn"
            title="Notifications"
            onClick={
              showNotifications
            }
          >

            <Bell
              size={18}
            />

            {unreadCount >
              0 && (

              <span className="notification-count">
                {unreadCount >
                9
                  ? "9+"
                  : unreadCount}
              </span>

            )}

          </button>


          {/* =================================================
              PROFILE
          ================================================== */}

          <button
            type="button"
            className="topbar-profile"
            onClick={
              showProfile
            }
          >

            <span className="profile-avatar">
              {initials}
            </span>

            <span className="profile-info">

              <strong>
                {fullName}
              </strong>

              <span>
                {roleName}
              </span>

            </span>

            <ChevronDown
              size={15}
            />

          </button>

        </div>

      </header>


      {/* =====================================================
          DRAWER BACKDROP
      ====================================================== */}

      {(notificationOpen ||
        profileOpen) && (

        <div
          className="drawer-backdrop"
          onClick={() => {
            setNotificationOpen(
              false
            );

            setProfileOpen(
              false
            );
          }}
        />

      )}


      {/* =====================================================
          NOTIFICATION DRAWER
      ====================================================== */}

      <aside
        className={`right-drawer ${
          notificationOpen
            ? "open"
            : ""
        }`}
      >

        <div className="right-drawer-header">

          <div>

            <h4>
              Notifications
            </h4>

            <p>
              Recent HRMS
              notifications
            </p>

          </div>

          <button
            type="button"
            className="drawer-close-btn"
            onClick={() =>
              setNotificationOpen(
                false
              )
            }
          >
            <X
              size={20}
            />
          </button>

        </div>


        <div className="right-drawer-content">

          {notificationLoading ? (

            <div className="drawer-empty">

              <Bell
                size={30}
              />

              <h5>
                Loading...
              </h5>

            </div>

          ) : notifications.length ===
            0 ? (

            <div className="drawer-empty">

              <div className="drawer-empty-icon">
                <Bell
                  size={27}
                />
              </div>

              <h5>
                No notifications
              </h5>

              <p>
                There are currently no
                notifications to show.
              </p>

            </div>

          ) : (

            <div className="notification-list">

              {notifications.map(
                (
                  notification
                ) => (

                  <div
                    key={
                      notification.id
                    }
                    className={`notification-card ${
                      notification.is_read
                        ? ""
                        : "unread"
                    }`}
                  >

                    <div className="notification-card-icon">
                      <Bell
                        size={
                          16
                        }
                      />
                    </div>

                    <div>

                      <strong>
                        {notification.title ||
                          "Notification"}
                      </strong>

                      <p>
                        {notification.message ||
                          notification.description ||
                          ""}
                      </p>

                      {notification.created_at && (

                        <small>
                          {new Date(
                            notification.created_at
                          ).toLocaleString()}
                        </small>

                      )}

                    </div>

                  </div>

                )
              )}

            </div>

          )}

        </div>

      </aside>


      {/* =====================================================
          PROFILE DRAWER
      ====================================================== */}

      <aside
        className={`right-drawer ${
          profileOpen
            ? "open"
            : ""
        }`}
      >

        <div className="right-drawer-header">

          <div>

            <h4>
              Profile
            </h4>

            <p>
              User account information
            </p>

          </div>

          <button
            type="button"
            className="drawer-close-btn"
            onClick={() =>
              setProfileOpen(
                false
              )
            }
          >

            <X
              size={20}
            />

          </button>

        </div>


        <div className="profile-drawer-header">

          <div className="profile-large-avatar">
            {initials}
          </div>

          <div>

            <h5>
              {fullName}
            </h5>

            <span>
              {roleName}
            </span>

            {email && (
              <p>
                {email}
              </p>
            )}

          </div>

        </div>


        <div className="right-drawer-content">

          <div className="profile-details-card">

            <div className="profile-detail-row">

              <span>
                Username
              </span>

              <strong>
                {user?.username ||
                  "-"}
              </strong>

            </div>


            <div className="profile-detail-row">

              <span>
                Name
              </span>

              <strong>
                {fullName}
              </strong>

            </div>


            <div className="profile-detail-row">

              <span>
                Email
              </span>

              <strong>
                {email ||
                  "-"}
              </strong>

            </div>


            <div className="profile-detail-row">

              <span>
                Role
              </span>

              <strong>
                {roleName}
              </strong>

            </div>

          </div>


          <button
            type="button"
            className="profile-logout"
            onClick={
              logout
            }
          >

            <LogOut
              size={18}
            />

            Logout

          </button>

        </div>

      </aside>
    </>
  );
}
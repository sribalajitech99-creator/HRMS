import {
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import ProtectedRoute from "./ProtectedRoute";
import MainLayout from "../layouts/MainLayout";

import Login from "../pages/auth/Login";
import Dashboard from "../pages/dashboard/Dashboard";

import SettingsPage from "../pages/settings/SettingsPage";
import CompaniesPage from "../pages/settings/CompaniesPage";
import DepartmentsPage from "../pages/settings/DepartmentsPage";
import DesignationsPage from "../pages/settings/DesignationsPage";

import ReportsPage from "../pages/reports/ReportsPage";

import EmployeesPage from "../pages/employees/EmployeesPage";
import AttendancePage from "../pages/employees/AttendancePage";
import ShiftsPage from "../pages/employees/ShiftsPage";
import LeavePage from "../pages/employees/LeavePage";
import PayrollPage from "../pages/employees/PayrollPage";
import SalaryPage from "../pages/employees/SalaryPage";
import PayslipsPage from "../pages/employees/PayslipsPage";
import RecruitmentPage from "../pages/employees/RecruitmentPage";
import AssetsPage from "../pages/employees/AssetsPage";


export default function AppRoutes() {
  return (
    <Routes>

      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >

        <Route
          index
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        {/* ORGANIZATION */}
        <Route
          path="/companies"
          element={<CompaniesPage />}
        />

        <Route
          path="/departments"
          element={<DepartmentsPage />}
        />

        <Route
          path="/designations"
          element={<DesignationsPage />}
        />

        {/* EMPLOYEES */}
        <Route
          path="/employees"
          element={<EmployeesPage />}
        />

        {/* ATTENDANCE */}
        <Route
          path="/attendance"
          element={<AttendancePage />}
        />

        <Route
          path="/attendance/monthly"
          element={<AttendancePage />}
        />

        <Route
          path="/attendance/regularization"
          element={<AttendancePage />}
        />

        <Route
          path="/shifts"
          element={<ShiftsPage />}
        />

        {/* LEAVE */}
        <Route
          path="/leave"
          element={<LeavePage />}
        />

        {/* PAYROLL */}
        <Route
          path="/payroll"
          element={<PayrollPage />}
        />

        <Route
          path="/payroll/salary-structures"
          element={<SalaryPage />}
        />

        <Route
          path="/payroll/payslips"
          element={<PayslipsPage />}
        />

        {/* RECRUITMENT */}
        <Route
          path="/recruitment"
          element={<RecruitmentPage />}
        />

        {/* ASSETS */}
        <Route
          path="/assets"
          element={<AssetsPage />}
        />

        {/* REPORTS */}
        <Route
          path="/reports"
          element={<ReportsPage />}
        />

        {/* SETTINGS */}
        <Route
          path="/settings"
          element={<SettingsPage />}
        />

      </Route>

      <Route
        path="*"
        element={
          <Navigate
            to="/dashboard"
            replace
          />
        }
      />

    </Routes>
  );
}
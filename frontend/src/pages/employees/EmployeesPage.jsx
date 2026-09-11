import CrudPage from "../../components/common/CrudPage";

export default function EmployeesPage() {
  return (
    <CrudPage
      title="Employees"
      description="Manage the complete employee master and employment information."
      endpoint="/employees/"
      columns={[
        {
          key: "employee_code",
          label: "Employee ID",
        },
        {
          key: "full_name",
          label: "Employee",
          render: (row) => {
            const firstName = row.first_name || "";
            const lastName = row.last_name || "";

            return `${firstName} ${lastName}`.trim() || "-";
          },
        },
        {
          key: "company_name",
          label: "Company",
          render: (row) => row.company_name || "-",
        },
        {
          key: "department_name",
          label: "Department",
          render: (row) => row.department_name || "-",
        },
        {
          key: "designation_name",
          label: "Designation",
          render: (row) => row.designation_name || "-",
        },
        {
          key: "mobile",
          label: "Mobile",
          render: (row) => row.mobile || "-",
        },
        {
          key: "joining_date",
          label: "Joined",
          render: (row) => row.joining_date || "-",
        },
        {
          key: "status",
          label: "Status",
          render: (row) => {
            const status = row.status || "";

            const statusLabels = {
              ACTIVE: "Active",
              PROBATION: "Probation",
              NOTICE: "Notice Period",
              INACTIVE: "Inactive",
              EXITED: "Exited",
            };

            const badgeClasses = {
              ACTIVE: "bg-success",
              PROBATION: "bg-warning text-dark",
              NOTICE: "bg-info text-dark",
              INACTIVE: "bg-secondary",
              EXITED: "bg-danger",
            };

            return (
              <span
                className={`badge ${
                  badgeClasses[status] || "bg-secondary"
                }`}
              >
                {statusLabels[status] || status || "-"}
              </span>
            );
          },
        },
      ]}
      fields={[
        {
          name: "employee_code",
          label: "Employee Code",
          required: true,
        },

        {
          name: "first_name",
          label: "First Name",
          required: true,
        },

        {
          name: "last_name",
          label: "Last Name",
        },

        {
          name: "company",
          label: "Company",
          type: "select",
          source: "/companies/",
          required: true,
          optionLabel: (item) =>
            `${item.code || ""} - ${item.name || ""}`,
        },

        {
          name: "department",
          label: "Department",
          type: "select",
          source: "/departments/",
          nullable: true,
          optionLabel: (item) =>
            item.company_name
              ? `${item.name} - ${item.company_name}`
              : item.name,
        },

        {
          name: "designation",
          label: "Designation",
          type: "select",
          source: "/designations/",
          nullable: true,
          optionLabel: (item) =>
            item.department_name
              ? `${item.name} - ${item.department_name}`
              : item.name,
        },

        {
          name: "reporting_manager",
          label: "Reporting Manager",
          type: "select",
          source: "/employees/",
          nullable: true,
          optionLabel: (item) => {
            const name =
              `${item.first_name || ""} ${item.last_name || ""}`.trim();

            return `${item.employee_code || ""} - ${name}`;
          },
        },

        {
          name: "work_email",
          label: "Work Email",
          type: "email",
        },

        {
          name: "mobile",
          label: "Mobile",
        },

        {
          name: "date_of_birth",
          label: "Date of Birth",
          type: "date",
          nullable: true,
        },

        {
          name: "joining_date",
          label: "Joining Date",
          type: "date",
          required: true,
        },

        {
          name: "employment_type",
          label: "Employment Type",
          type: "select",
          defaultValue: "Permanent",
          options: [
            {
              value: "Permanent",
              label: "Permanent",
            },
            {
              value: "Contract",
              label: "Contract",
            },
            {
              value: "Temporary",
              label: "Temporary",
            },
            {
              value: "Intern",
              label: "Intern",
            },
          ],
        },

        {
          name: "status",
          label: "Status",
          type: "select",
          defaultValue: "ACTIVE",
          options: [
            {
              value: "ACTIVE",
              label: "Active",
            },
            {
              value: "PROBATION",
              label: "Probation",
            },
            {
              value: "NOTICE",
              label: "Notice Period",
            },
            {
              value: "INACTIVE",
              label: "Inactive",
            },
            {
              value: "EXITED",
              label: "Exited",
            },
          ],
        },

        {
          name: "current_address",
          label: "Current Address",
          type: "textarea",
          fullWidth: true,
        },

        {
          name: "permanent_address",
          label: "Permanent Address",
          type: "textarea",
          fullWidth: true,
        },

        {
          name: "bank_name",
          label: "Bank Name",
        },

        {
          name: "bank_account_number",
          label: "Bank Account Number",
        },

        {
          name: "ifsc_code",
          label: "IFSC Code",
        },

        {
          name: "pan_number",
          label: "PAN Number",
        },

        {
          name: "aadhaar_number",
          label: "Aadhaar Number",
        },
      ]}
    />
  );
}
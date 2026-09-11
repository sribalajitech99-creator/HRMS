import CrudPage from "../../components/common/CrudPage";

export default function CompaniesPage() {
  return (
    <CrudPage
      title="Companies"
      description="Manage companies in the HRMS."
      endpoint="/companies/"
      columns={[
        {
          key: "code",
          label: "Code",
        },
        {
          key: "name",
          label: "Company Name",
        },
        {
          key: "legal_name",
          label: "Legal Name",
        },
        {
          key: "employee_prefix",
          label: "Employee Prefix",
        },
        {
          key: "country",
          label: "Country",
        },
        {
          key: "is_active",
          label: "Status",
          render: (row) =>
            row.is_active ? (
              <span className="badge bg-success">
                Active
              </span>
            ) : (
              <span className="badge bg-secondary">
                Inactive
              </span>
            ),
        },
      ]}
      fields={[
        {
          name: "name",
          label: "Company Name",
          required: true,
        },
        {
          name: "code",
          label: "Company Code",
          required: true,
        },
        {
          name: "legal_name",
          label: "Legal Name",
        },
        {
          name: "employee_prefix",
          label: "Employee Prefix",
          required: true,
        },
        {
          name: "email",
          label: "Email",
          type: "email",
        },
        {
          name: "phone",
          label: "Phone",
        },
        {
          name: "address",
          label: "Address",
          type: "textarea",
          fullWidth: true,
        },
        {
          name: "city",
          label: "City",
        },
        {
          name: "state",
          label: "State",
        },
        {
          name: "country",
          label: "Country",
          defaultValue: "India",
        },
        {
          name: "currency",
          label: "Currency",
          defaultValue: "INR",
        },
        {
          name: "is_active",
          label: "Active",
          type: "checkbox",
          defaultValue: true,
        },
      ]}
    />
  );
}
import CrudPage from "../../components/common/CrudPage";

export default function DepartmentsPage() {
  return (
    <CrudPage
      title="Departments"
      description="Manage departments for each company."
      endpoint="/departments/"
      columns={[
        {
          key: "code",
          label: "Code",
        },
        {
          key: "name",
          label: "Department",
        },
        {
          key: "company_name",
          label: "Company",
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
          name: "company",
          label: "Company",
          type: "select",
          source: "/companies/",
          optionLabel: (item) =>
            `${item.code} - ${item.name}`,
          required: true,
        },
        {
          name: "name",
          label: "Department Name",
          required: true,
        },
        {
          name: "code",
          label: "Department Code",
          required: true,
        },
        {
          name: "description",
          label: "Description",
          type: "textarea",
          fullWidth: true,
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
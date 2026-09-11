import CrudPage from "../../components/common/CrudPage";

export default function DesignationsPage() {
  return (
    <CrudPage
      title="Designations"
      description="Configure employee job titles and levels."
      endpoint="/designations/"
      columns={[
        {
          key: "code",
          label: "Code",
        },
        {
          key: "name",
          label: "Designation",
        },
        {
          key: "department_name",
          label: "Department",
        },
        {
          key: "level",
          label: "Level",
        },
        {
          key: "is_active",
          label: "Active",
        },
      ]}
      fields={[
        {
          name: "company",
          label: "Company",
          type: "select",
          source: "/companies/",
          required: true,
        },
        {
          name: "department",
          label: "Department",
          type: "select",
          source: "/departments/",
          nullable: true,
        },
        {
          name: "name",
          label: "Designation",
          required: true,
        },
        {
          name: "code",
          label: "Designation Code",
          required: true,
        },
        {
          name: "level",
          label: "Level",
          type: "number",
          defaultValue: 1,
          min: 1,
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
import CrudPage from "../../components/common/CrudPage";


export default function ShiftsPage() {
  return (
    <CrudPage
      title="Shifts"
      description="Manage company shift timings for attendance."
      endpoint="/shifts/"
      columns={[
        {
          key: "code",
          label: "Code",
        },
        {
          key: "name",
          label: "Shift",
        },
        {
          key: "company_name",
          label: "Company",
        },
        {
          key: "start_time",
          label: "Start Time",
          render: (row) =>
            row.start_time
              ? row.start_time.slice(0, 5)
              : "-",
        },
        {
          key: "end_time",
          label: "End Time",
          render: (row) =>
            row.end_time
              ? row.end_time.slice(0, 5)
              : "-",
        },
        {
          key: "is_night_shift",
          label: "Night Shift",
          render: (row) =>
            row.is_night_shift ? (
              <span className="badge bg-dark">
                Yes
              </span>
            ) : (
              <span className="badge bg-light text-dark">
                No
              </span>
            ),
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
          required: true,
          optionLabel: (item) =>
            `${item.code} - ${item.name}`,
        },
        {
          name: "code",
          label: "Shift Code",
          required: true,
        },
        {
          name: "name",
          label: "Shift Name",
          required: true,
        },
        {
          name: "start_time",
          label: "Start Time",
          type: "time",
          required: true,
        },
        {
          name: "end_time",
          label: "End Time",
          type: "time",
          required: true,
        },
        {
          name: "is_night_shift",
          label: "Night Shift",
          type: "checkbox",
          defaultValue: false,
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
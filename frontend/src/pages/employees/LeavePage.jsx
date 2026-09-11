import CrudPage from "../../components/common/CrudPage";

export default function LeavePage() {
  return (
    <CrudPage
      title="Leave Requests"
      description="Review employee leave applications and approval status."
      endpoint="/leave-requests/"
      columns={[
        {
          key: "employee_code",
          label: "Employee",
        },
        {
          key: "leave_type_name",
          label: "Leave Type",
        },
        {
          key: "start_date",
          label: "From",
        },
        {
          key: "end_date",
          label: "To",
        },
        {
          key: "total_days",
          label: "Days",
        },
        {
          key: "status",
          label: "Status",
        },
      ]}
      fields={[
        {
          name: "employee",
          label: "Employee",
          type: "select",
          source: "/employees/",
          required: true,
        },
        {
          name: "leave_type",
          label: "Leave Type",
          type: "select",
          source: "/leave-types/",
          required: true,
        },
        {
          name: "start_date",
          label: "Start Date",
          type: "date",
          required: true,
        },
        {
          name: "end_date",
          label: "End Date",
          type: "date",
          required: true,
        },
        {
          name: "total_days",
          label: "Total Days",
          type: "number",
          step: "0.5",
          required: true,
        },
        {
          name: "reason",
          label: "Reason",
          type: "textarea",
          fullWidth: true,
          required: true,
        },
      ]}
      rowActions={[
        {
          label: "Approve",
          endpoint: (row) =>
            `/leave-requests/${row.id}/approve/`,
          className:
            "btn-outline-success",
          show: (row) =>
            row.status === "PENDING",
          confirm:
            "Approve this leave request?",
        },
        {
          label: "Reject",
          endpoint: (row) =>
            `/leave-requests/${row.id}/reject/`,
          className:
            "btn-outline-danger",
          show: (row) =>
            row.status === "PENDING",
          confirm:
            "Reject this leave request?",
        },
      ]}
    />
  );
}
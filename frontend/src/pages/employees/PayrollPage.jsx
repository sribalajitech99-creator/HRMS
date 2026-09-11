import CrudPage from "../../components/common/CrudPage";

const PAID = "PAID";
const CALCULATED = "CALCULATED";
const APPROVED = "APPROVED";

export default function PayrollPage() {
  return (
    <CrudPage
      title="Payroll Runs"
      description="Generate and process monthly company payroll."
      endpoint="/payroll-runs/"
      columns={[
        {
          key: "company_name",
          label: "Company",
        },
        {
          key: "month",
          label: "Month",
        },
        {
          key: "year",
          label: "Year",
        },
        {
          key: "pay_date",
          label: "Pay Date",
          render: (row) =>
            row.pay_date || "—",
        },
        {
          key: "status",
          label: "Status",
          render: (row) =>
            row.status_name ||
            row.status ||
            "—",
        },
        {
          key: "created_at",
          label: "Created",
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
          name: "month",
          label: "Month",
          type: "number",
          min: 1,
          max: 12,
          required: true,
        },
        {
          name: "year",
          label: "Year",
          type: "number",
          min: 2020,
          required: true,
        },
        {
          name: "pay_date",
          label: "Pay Date",
          type: "date",
          nullable: true,
        },
      ]}
      rowActions={[
        {
          label: "Calculate",
          endpoint: (row) =>
            `/payroll-runs/${row.id}/calculate/`,
          className:
            "btn-outline-success",
          confirm:
            "Calculate payroll and regenerate payslips?",
          hidden: (row) =>
            row.status ===
              APPROVED ||
            row.status === PAID,
        },
        {
          label: "Approve",
          endpoint: (row) =>
            `/payroll-runs/${row.id}/approve/`,
          className:
            "btn-outline-warning",
          confirm:
            "Approve this calculated payroll?",
          hidden: (row) =>
            row.status !==
            CALCULATED,
        },
        {
          label: "Mark Paid",
          endpoint: (row) =>
            `/payroll-runs/${row.id}/mark-paid/`,
          className:
            "btn-outline-dark",
          confirm:
            "Mark this payroll as paid?",
          hidden: (row) =>
            ![CALCULATED, APPROVED]
              .includes(row.status),
        },
      ]}
    />
  );
}
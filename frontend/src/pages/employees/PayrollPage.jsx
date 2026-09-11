import CrudPage from "../../components/common/CrudPage";

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
          key: "status",
          label: "Status",
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
        },
      ]}
    />
  );
}
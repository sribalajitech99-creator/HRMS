import CrudPage from "../../components/common/CrudPage";

function money(value) {
  return new Intl.NumberFormat(
    "en-IN",
    {
      style: "currency",
      currency: "INR",
    }
  ).format(Number(value || 0));
}

export default function PayslipsPage() {
  return (
    <CrudPage
      title="Payslips"
      description="View generated employee payroll results."
      endpoint="/payslips/"
      allowCreate={false}
      allowEdit={false}
      allowDelete={false}
      columns={[
        {
          key: "employee_name",
          label: "Employee",
        },
        {
          key: "gross_salary",
          label: "Gross",
          render: (row) =>
            money(row.gross_salary),
        },
        {
          key: "overtime_amount",
          label: "OT",
          render: (row) =>
            money(
              row.overtime_amount
            ),
        },
        {
          key: "deductions",
          label: "Deductions",
          render: (row) =>
            money(row.deductions),
        },
        {
          key: "net_salary",
          label: "Net Salary",
          render: (row) =>
            money(row.net_salary),
        },
      ]}
    />
  );
}
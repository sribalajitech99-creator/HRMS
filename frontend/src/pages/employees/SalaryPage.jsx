import CrudPage from "../../components/common/CrudPage";

export default function SalaryPage() {
  return (
    <CrudPage
      title="Employee Salaries"
      description="Configure employee salary structures."
      endpoint="/employee-salaries/"
      columns={[
        {
          key: "employee_name",
          label: "Employee",
        },
        {
          key: "basic_salary",
          label: "Basic",
        },
        {
          key: "hra",
          label: "HRA",
        },
        {
          key: "allowance",
          label: "Allowance",
        },
        {
          key: "effective_from",
          label: "Effective From",
        },
        {
          key: "is_active",
          label: "Active",
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
          name: "basic_salary",
          label: "Basic Salary",
          type: "number",
          step: "0.01",
          required: true,
        },
        {
          name: "hra",
          label: "HRA",
          type: "number",
          step: "0.01",
          defaultValue: 0,
        },
        {
          name: "allowance",
          label: "Allowance",
          type: "number",
          step: "0.01",
          defaultValue: 0,
        },
        {
          name: "effective_from",
          label: "Effective From",
          type: "date",
          required: true,
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
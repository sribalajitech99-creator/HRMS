import CrudPage from "../../components/common/CrudPage";

const NUMBER_FIELD = {
  type: "number",
  step: "0.01",
  defaultValue: 0,
};

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
          key: "dearness_allowance",
          label: "DA",
        },
        {
          key: "special_allowance",
          label: "Special",
        },
        {
          key: "bonus",
          label: "Bonus",
        },
        {
          key: "deductions",
          label: "Deductions",
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
          name: "dearness_allowance",
          label: "Dearness Allowance",
          ...NUMBER_FIELD,
        },
        {
          name: "conveyance_allowance",
          label: "Conveyance Allowance",
          ...NUMBER_FIELD,
        },
        {
          name: "medical_allowance",
          label: "Medical Allowance",
          ...NUMBER_FIELD,
        },
        {
          name: "special_allowance",
          label: "Special Allowance",
          ...NUMBER_FIELD,
        },
        {
          name: "other_allowance",
          label: "Other Allowance",
          ...NUMBER_FIELD,
        },
        {
          name: "bonus",
          label: "Bonus",
          ...NUMBER_FIELD,
        },
        {
          name: "pf",
          label: "PF Deductions",
          ...NUMBER_FIELD,
        },
        {
          name: "esi",
          label: "ESI",
          ...NUMBER_FIELD,
        },
        {
          name: "professional_tax",
          label: "Professional Tax",
          ...NUMBER_FIELD,
        },
        {
          name: "tds",
          label: "TDS",
          ...NUMBER_FIELD,
        },
        {
          name: "other_deduction",
          label: "Other Deduction",
          ...NUMBER_FIELD,
        },
        {
          name: "deductions",
          label: "Advance / Other",
          ...NUMBER_FIELD,
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
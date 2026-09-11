import CrudPage from "../../components/common/CrudPage";

export default function AssetsPage() {
  return (
    <CrudPage
      title="Assets"
      description="Manage employee and company assets."
      endpoint="/assets/"
      columns={[
        {
          key: "asset_code",
          label: "Asset Code",
        },
        {
          key: "category",
          label: "Category",
        },
        {
          key: "brand",
          label: "Brand",
        },
        {
          key: "model",
          label: "Model",
        },
        {
          key: "employee_name",
          label: "Assigned To",
        },
        {
          key: "status",
          label: "Status",
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
          name: "asset_code",
          label: "Asset Code",
          required: true,
        },
        {
          name: "category",
          label: "Category",
          required: true,
        },
        {
          name: "brand",
          label: "Brand",
        },
        {
          name: "model",
          label: "Model",
        },
        {
          name: "serial_number",
          label: "Serial Number",
        },
        {
          name: "assigned_employee",
          label: "Assigned Employee",
          type: "select",
          source: "/employees/",
          nullable: true,
        },
        {
          name: "status",
          label: "Status",
          type: "select",
          defaultValue: "AVAILABLE",
          options: [
            {
              value: "AVAILABLE",
              label: "Available",
            },
            {
              value: "ASSIGNED",
              label: "Assigned",
            },
            {
              value: "REPAIR",
              label: "Under Repair",
            },
            {
              value: "RETIRED",
              label: "Retired",
            },
          ],
        },
      ]}
    />
  );
}

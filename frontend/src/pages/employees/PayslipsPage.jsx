import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Download } from "lucide-react";

import api from "../../api/client";
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

const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

export default function PayslipsPage() {
  const [searchParams] = useSearchParams();
  const [downloading, setDownloading] = useState(false);

  const payrollRun = searchParams.get("payroll_run");

  const downloadAllPdf = async () => {
    setDownloading(true);
    try {
      const body = payrollRun
        ? { payroll_run: Number(payrollRun) }
        : {};

      const response = await api.post(
        "/payslips/bulk-pdf/",
        body,
        { responseType: "blob" }
      );

      const blob = new Blob([response.data]);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = payrollRun
        ? `Payslips_Run${payrollRun}.zip`
        : "All_Payslips.zip";
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(
        () => URL.revokeObjectURL(url),
        1000
      );
    } catch (err) {
      let msg = "Unable to download bulk PDF.\n";
      msg += "Error: " + (err.message || "unknown") + "\n";
      if (err.response) {
        msg += "Status: " + err.response.status + "\n";
        try {
          const text = await err.response.data.text();
          msg += "Body: " + text.substring(0, 200);
        } catch (e2) {
          msg += "Data type: " + typeof err.response.data;
        }
      }
      alert(msg);
    } finally {
      setDownloading(false);
    }
  };

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
          key: "basic_salary",
          label: "Basic",
          render: (row) =>
            money(row.basic_salary),
        },
        {
          key: "bonus",
          label: "Bonus",
          render: (row) =>
            money(row.bonus),
        },
        {
          key: "overtime_amount",
          label: "OT Amount",
          render: (row) =>
            money(
              row.overtime_amount
            ),
        },
        {
          key: "gross_salary",
          label: "Gross",
          render: (row) =>
            money(
              Number(
                row.gross_salary
              ) +
                Number(
                  row.overtime_amount
                )
            ),
        },
        {
          key: "pf",
          label: "PF Deduction",
          render: (row) =>
            money(row.pf),
        },
        {
          key: "deductions",
          label: "Total Deductions",
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
      rowActions={[
        {
          label: "Payslip",
          className:
            "btn-outline-primary",
          navigate: (row) =>
            `/payroll/payslips/${row.id}`,
        },
        {
          label: "Download PDF",
          className:
            "btn-outline-secondary",
          download: (row) =>
            `/payslips/${row.id}/pdf/`,
          fileName: (row) => {
            const [month, year] =
              row.period.split("-");

            const monthName =
              MONTHS[
                Number(month) - 1
              ] || month;

            return (
              `Payslip_${row.employee_code}_` +
              `${monthName}_${year}.pdf`
            );
          },
        },
      ]}
      headerActions={
        <button
          type="button"
          className="crud-add-btn"
          style={{
            background: "#1B5E20",
            color: "#fff",
            border: "none",
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
          }}
          onClick={downloadAllPdf}
          disabled={downloading}
        >
          <Download size={16} />
          {downloading
            ? "Downloading..."
            : "Download All PDF"}
        </button>
      }
    />
  );
}

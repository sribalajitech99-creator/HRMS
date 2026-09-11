import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  ArrowLeft,
  Download,
  Printer,
} from "lucide-react";

import api from "../../api/client";
import "../../styles/payslip.css";


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


function money(value) {
  return new Intl.NumberFormat(
    "en-IN",
    {
      style: "currency",
      currency: "INR",
      minimumFractionDigits: 2,
    }
  ).format(Number(
    value || 0
  ));
}


function PayRow({
  label,
  value,
}) {
  return (
    <div className="payslip-line">
      <span>{label}</span>
      <span>{money(value)}</span>
    </div>
  );
}


function InfoCell({
  label,
  value,
}) {
  return (
    <div className="payslip-emp-item">
      <label>{label}</label>
      <strong>{value || "—"}</strong>
    </div>
  );
}


export default function PayslipDocumentPage() {

  const {
    id,
  } = useParams();

  const navigate =
    useNavigate();

  const [payslip, setPayslip] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [downloading, setDownloading] =
    useState(false);


  useEffect(() => {

    let active = true;

    api
      .get(`/payslips/${id}/`)
      .then((response) => {

        if (active) {
          setPayslip(
            response.data
          );
        }
      })
      .catch((err) => {

        if (active) {
          setError(
            err.response
              ?.data?.detail ||
              "Unable to load payslip."
          );
        }
      })
      .finally(() => {

        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [id]);


  const downloadPdf = async () => {

    setDownloading(true);

    try {

      const response =
        await api.get(
          `/payslips/${id}/pdf/`,
          {
            responseType:
              "blob",
          }
        );

      const url =
        URL.createObjectURL(
          new Blob(
            [response.data]
          )
        );

      const link =
        document.createElement(
          "a"
        );

      const month =
        MONTHS[
          Number(
            payslip.month
          ) - 1
        ] ||
        payslip.month;

      link.href = url;

      link.download =
        `Payslip_${payslip.employee_code}_` +
        `${month}_${payslip.year}.pdf`;

      document.body.appendChild(
        link
      );

      link.click();

      link.remove();

      setTimeout(
        () =>
          URL.revokeObjectURL(
            url
          ),
        1000
      );

    } catch (err) {

      setError(
        err.response
          ?.data?.detail ||
          "Unable to download PDF."
      );

    } finally {

      setDownloading(false);
    }
  };


  if (loading) {
    return (
      <div className="p-5">
        Loading...
      </div>
    );
  }


  if (error || !payslip) {

    return (
      <div
        className="p-5 text-danger"
      >
        {error ||
          "Payslip not found."}
      </div>
    );
  }


  const monthName =
    MONTHS[
      Number(
        payslip.month
      ) - 1
    ] ||
    `${payslip.month}`;

  const periodLabel =
    `${monthName} ${payslip.year}`;

  const earningsLines = [
    {
      label: "Basic Salary",
      value:
        payslip.basic_salary,
    },
    {
      label: "Dearness Allowance",
      value:
        payslip.dearness_allowance,
    },
    {
      label: "Bonus",
      value: payslip.bonus,
    },
  ].filter(
    (line) =>
      Number(line.value) > 0
  );

  const deductionLines = [
    {
      label: "PF Deductions",
      value: payslip.pf,
    },
    {
      label: "Other / Advance",
      value:
        payslip.other_deduction,
    },
    {
      label: "LOP Deduction",
      value:
        payslip.lop_deduction,
    },
  ].filter(
    (line) =>
      Number(line.value) > 0
  );

  const gross =
    Number(
      payslip.gross_salary
    ) +
    Number(
      payslip.overtime_amount
    );

  const totalDeductions =
    Number(
      payslip.deductions
    );

  const net =
    Number(
      payslip.net_salary
    );


  return (
    <div className="payslip-page">

      <div className="payslip-toolbar">

        <button
          type="button"
          className="btn-link-back"
          onClick={() =>
            navigate(
              "/payroll/payslips"
            )
          }
        >

          <ArrowLeft
            size={16}
          />

          Back to Payslips

        </button>

        <div className="payslip-toolbar-actions">

          <button
            type="button"
            className="btn btn-sm btn-outline-secondary"
            onClick={
              downloadPdf
            }
            disabled={downloading}
          >

            <Download
              size={15}
            />

            &nbsp;
            {downloading
              ? "Downloading..."
              : "Download PDF"}

          </button>

          <button
            type="button"
            className="btn btn-sm btn-dark"
            onClick={() =>
              window.print()
            }
          >

            <Printer
              size={15}
            />

            &nbsp;Print

          </button>

        </div>

      </div>


      {error && (
        <div className="payslip-error">
          {error}
        </div>
      )}


      <div className="payslip-document">

        <div className="payslip-card">

          <div className="payslip-head">

            <h1 className="payslip-title">
              Salary Slip
            </h1>

            <p className="payslip-period">
              For the month of{" "}
              <strong>{periodLabel}</strong>
            </p>

          </div>


          <div className="payslip-emp">

            <InfoCell
              label="Employee"
              value={[
                payslip.employee_name,
                payslip.employee_code,
              ].filter(Boolean).join(" · ")}
            />

            <InfoCell
              label="Designation"
              value={
                payslip.designation_name
              }
            />

            <InfoCell
              label="Department"
              value={
                payslip.department_name
              }
            />

            <InfoCell
              label="Date of Joining"
              value={
                payslip.joining_date
              }
            />

          </div>


          <div className="payslip-breakdown">

            <div className="payslip-col">

              <h3>Earnings</h3>

              {earningsLines.map(
                (line) => (
                  <PayRow
                    key={line.label}
                    label={
                      line.label
                    }
                    value={
                      line.value
                    }
                  />
                )
              )}

              {earningsLines.length ===
                0 && (
                <div className="payslip-line zero">
                  <span>—</span>
                </div>
              )}

              <div className="payslip-line total">

                <span>
                  Gross Earnings
                </span>

                <span>
                  {money(gross)}
                </span>

              </div>

            </div>


            <div className="payslip-col">

              <h3>Deductions</h3>

              {deductionLines.map(
                (line) => (
                  <PayRow
                    key={line.label}
                    label={
                      line.label
                    }
                    value={
                      line.value
                    }
                  />
                )
              )}

              {deductionLines.length ===
                0 && (
                <div className="payslip-line zero">
                  <span>—</span>
                </div>
              )}

              <div className="payslip-line total">

                <span>
                  Total Deductions
                </span>

                <span>
                  {money(
                    totalDeductions
                  )}
                </span>

              </div>

            </div>

          </div>


          <div className="payslip-net">

            <span className="net-label">
              Net Pay
            </span>

            <span className="net-value">
              {money(net)}
            </span>

          </div>


          <div className="payslip-words">
            <strong>Amount in words: </strong>
            {payslip.amount_in_words}
          </div>


          <div className="payslip-attendance">

            {[
              {
                label:
                  "No of Days",
                value:
                  payslip.no_of_days,
              },
              {
                label:
                  "Working Days",
                value:
                  payslip.working_days,
              },
              {
                label:
                  "Per Day",
                value:
                  payslip.per_day_rate,
              },
              {
                label:
                  "Present",
                value:
                  payslip.present_days,
              },
              {
                label:
                  "Paid Leave",
                value:
                  payslip.paid_leave_days,
              },
              {
                label:
                  "Unpaid / LOP",
                value:
                  payslip.lop_days,
              },
              {
                label:
                  "Half Days",
                value:
                  payslip.half_days,
              },
              {
                label:
                  "Holidays",
                value:
                  payslip.holidays,
              },
              {
                label:
                  "Week Offs",
                value:
                  payslip.week_offs,
              },
              {
                label: "OT Hours",
                value:
                  payslip.ot_hours,
              },
            ].map(
              (item) => (
                <div
                  className="payslip-att-item"
                  key={item.label}
                >
                  <span>
                    {item.label}
                  </span>
                  <strong>
                    {item.value ??
                      0}
                  </strong>
                </div>
              )
            )}

          </div>


          <div className="payslip-payment">

            <div className="payslip-payment-head">
              Payment Details
            </div>

            <div className="payslip-payment-grid">

              <InfoCell
                label="Pay Date"
                value={
                  payslip.pay_date
                }
              />

              <InfoCell
                label="Bank Name"
                value={
                  payslip.bank_name
                }
              />

              <InfoCell
                label="Account Number"
                value={
                  payslip.bank_account
                }
              />

              <InfoCell
                label="IFSC Code"
                value={
                  payslip.ifsc_code
                }
              />

              <InfoCell
                label="Account Holder"
                value={
                  payslip.account_holder
                }
              />

            </div>

          </div>


          <div className="payslip-foot">

            This is a system-generated
            payslip. Net pay is before
            statutory remittances.

          </div>

        </div>

      </div>

    </div>
  );
}
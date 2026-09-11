import { useState } from "react";

import CrudPage from "../../components/common/CrudPage";

export default function RecruitmentPage() {
  const [tab, setTab] =
    useState("jobs");

  return (
    <div>
      <div className="d-flex gap-2 mb-3">
        <button
          className={`btn ${
            tab === "jobs"
              ? "btn-success"
              : "btn-outline-success"
          }`}
          onClick={() =>
            setTab("jobs")
          }
        >
          Job Openings
        </button>

        <button
          className={`btn ${
            tab === "candidates"
              ? "btn-success"
              : "btn-outline-success"
          }`}
          onClick={() =>
            setTab("candidates")
          }
        >
          Candidates
        </button>
      </div>

      {tab === "jobs" ? (
        <CrudPage
          title="Job Openings"
          description="Manage active recruitment vacancies."
          endpoint="/job-openings/"
          columns={[
            {
              key: "job_code",
              label: "Job Code",
            },
            {
              key: "title",
              label: "Position",
            },
            {
              key: "company_name",
              label: "Company",
            },
            {
              key: "department_name",
              label: "Department",
            },
            {
              key: "positions",
              label: "Vacancies",
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
              name: "department",
              label: "Department",
              type: "select",
              source: "/departments/",
              nullable: true,
            },
            {
              name: "job_code",
              label: "Job Code",
              required: true,
            },
            {
              name: "title",
              label: "Job Title",
              required: true,
            },
            {
              name: "positions",
              label: "Positions",
              type: "number",
              defaultValue: 1,
            },
            {
              name: "description",
              label: "Description",
              type: "textarea",
              fullWidth: true,
            },
            {
              name: "status",
              label: "Status",
              type: "select",
              defaultValue: "OPEN",
              options: [
                {
                  value: "OPEN",
                  label: "Open",
                },
                {
                  value: "ON_HOLD",
                  label: "On Hold",
                },
                {
                  value: "CLOSED",
                  label: "Closed",
                },
              ],
            },
          ]}
        />
      ) : (
        <CrudPage
          title="Candidates"
          description="Track candidates throughout the recruitment process."
          endpoint="/candidates/"
          columns={[
            {
              key: "name",
              label: "Candidate",
            },
            {
              key: "job_title",
              label: "Job",
            },
            {
              key: "email",
              label: "Email",
            },
            {
              key: "phone",
              label: "Phone",
            },
            {
              key: "experience",
              label: "Experience",
            },
            {
              key: "stage",
              label: "Stage",
            },
          ]}
          fields={[
            {
              name: "job",
              label: "Job Opening",
              type: "select",
              source: "/job-openings/",
              required: true,
            },
            {
              name: "name",
              label: "Candidate Name",
              required: true,
            },
            {
              name: "email",
              label: "Email",
              type: "email",
              required: true,
            },
            {
              name: "phone",
              label: "Phone",
              required: true,
            },
            {
              name: "experience",
              label: "Experience (Years)",
              type: "number",
              step: "0.1",
              defaultValue: 0,
            },
            {
              name: "stage",
              label: "Stage",
              type: "select",
              defaultValue: "APPLIED",
              options: [
                {
                  value: "APPLIED",
                  label: "Applied",
                },
                {
                  value: "SCREENING",
                  label: "Screening",
                },
                {
                  value: "INTERVIEW",
                  label: "Interview",
                },
                {
                  value: "SELECTED",
                  label: "Selected",
                },
                {
                  value: "REJECTED",
                  label: "Rejected",
                },
                {
                  value: "JOINED",
                  label: "Joined",
                },
              ],
            },
          ]}
        />
      )}
    </div>
  );
}
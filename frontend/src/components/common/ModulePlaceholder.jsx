import { Construction } from "lucide-react";

function ModulePlaceholder({ title, description }) {
  return (
    <div className="module-placeholder-page">
      <div className="mb-4">
        <h1 className="page-title">{title}</h1>

        <p className="page-description">
          {description}
        </p>
      </div>

      <div className="hrms-card p-5 text-center">
        <div
          style={{
            width: "64px",
            height: "64px",
            borderRadius: "16px",
            background: "#e9f5f0",
            color: "#147558",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 18px",
          }}
        >
          <Construction size={30} />
        </div>

        <h5 className="mb-2">
          {title}
        </h5>

        <p className="text-muted-custom mb-0">
          This module is under development.
        </p>
      </div>
    </div>
  );
}

export default ModulePlaceholder;
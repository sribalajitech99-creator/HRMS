import {
  Link,
} from "react-router-dom";

import {
  Building2,
  Layers,
  Briefcase,
  Landmark,
} from "lucide-react";

import "./settings.css";

const SETTINGS_MODULES = [
  {
    to: "/companies",
    icon: Building2,
    title: "Companies",
    description:
      "Manage company profiles, legal details, currency and status.",
  },
  {
    to: "/departments",
    icon: Layers,
    title: "Departments",
    description:
      "Configure departments for each company in the organization.",
  },
  {
    to: "/designations",
    icon: Briefcase,
    title: "Designations",
    description:
      "Define employee job titles, codes and reporting levels.",
  },
];

export default function SettingsPage() {
  return (
    <div className="settings-page">
      <div className="settings-header">
        <div className="settings-header-icon">
          <Landmark size={26} />
        </div>

        <div>
          <h1>Settings</h1>
          <p>
            Configure the core organizational structures that
            power the HRMS.
          </p>
        </div>
      </div>

      <div className="settings-grid">
        {SETTINGS_MODULES.map((module) => {
          const Icon = module.icon;

          return (
            <Link
              to={module.to}
              className="settings-card"
              key={module.to}
            >
              <div className="settings-card-icon">
                <Icon size={24} />
              </div>

              <h3>{module.title}</h3>

              <p>{module.description}</p>

              <span className="settings-card-link">
                Manage {module.title} →
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

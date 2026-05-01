import { AlertOctagon, AlertTriangle, CheckCircle } from "lucide-react";

const URGENCY_CONTENT = {
  high: {
    className: "urgency-high",
    label: "HIGH",
    headline: "Seek medical attention promptly",
    detail: "Risk signals indicate this should be reviewed by a clinician without delay.",
    Icon: AlertOctagon,
  },
  medium: {
    className: "urgency-medium",
    label: "MEDIUM",
    headline: "Schedule a medical visit",
    detail: "Symptoms deserve timely review, especially if they worsen or persist.",
    Icon: AlertTriangle,
  },
  low: {
    className: "urgency-low",
    label: "LOW",
    headline: "Monitor and seek care if worsening",
    detail: "Current inputs suggest lower immediate risk, with continued observation recommended.",
    Icon: CheckCircle,
  },
};

export default function UrgencyBadge({ urgency }) {
  const content = URGENCY_CONTENT[urgency] || URGENCY_CONTENT.medium;
  const Icon = content.Icon;

  return (
    <section className={`urgency-panel ${content.className}`} aria-label={`${content.label} triage result`}>
      <div className="urgency-badge">
        <Icon size={28} strokeWidth={2.4} aria-hidden="true" />
        <span>{content.label}</span>
      </div>
      <div className="urgency-copy">
        <h2>{content.headline}</h2>
        <p>{content.detail}</p>
      </div>
    </section>
  );
}

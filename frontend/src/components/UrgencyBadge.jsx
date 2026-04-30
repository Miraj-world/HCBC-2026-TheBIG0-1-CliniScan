const MAP = {
  high: {
    className: "urgency-high",
    text: "HIGH URGENCY - Seek medical attention promptly",
  },
  medium: {
    className: "urgency-medium",
    text: "MEDIUM URGENCY - Schedule a doctor visit",
  },
  low: {
    className: "urgency-low",
    text: "LOW URGENCY - Monitor and seek care if worsening",
  },
};

export default function UrgencyBadge({ urgency }) {
  const item = MAP[urgency] || MAP.medium;
  return <div className={`banner ${item.className}`}>{item.text}</div>;
}

export default function ConflictCallout({ conflict }) {
  if (!conflict?.conflict_detected) return null;

  return (
    <div className="banner banner-conflict stack gap-sm">
      <strong>Clinical mismatch detected.</strong>
      <p>Reported severity: {conflict.text_severity || "unknown"}</p>
      <p>Observed visual severity: {conflict.vision_severity || "unknown"}</p>
      <p>Visual evidence has been weighted more heavily in this assessment.</p>
    </div>
  );
}

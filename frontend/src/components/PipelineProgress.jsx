const STAGE_META = [
  { icon: "[1]", colorClass: "stage-blue" },
  { icon: "[2]", colorClass: "stage-green" },
  { icon: "[3]", colorClass: "stage-purple" },
  { icon: "[4]", colorClass: "stage-orange" },
  { icon: "[5]", colorClass: "stage-teal" },
];

export default function PipelineProgress({ stageIndex, stages }) {
  return (
    <section className="card stack gap-md">
      <h2>Processing</h2>
      <p>Executing layered pipeline...</p>
      <ul className="pipeline-list">
        {stages.map((stage, index) => {
          const state = index < stageIndex ? "complete" : index === stageIndex ? "running" : "pending";
          const marker = state === "complete" ? "[x]" : state === "running" ? "[>]" : "[ ]";
          return (
            <li key={stage} className={`pipeline-item ${state} ${STAGE_META[index]?.colorClass || ""}`}>
              <span className="pipeline-icon">{STAGE_META[index]?.icon || "[]"}</span>
              <span className="pipeline-marker">{marker}</span>
              <span>{stage}</span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

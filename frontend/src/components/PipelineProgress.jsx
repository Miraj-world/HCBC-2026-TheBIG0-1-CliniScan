import { Plus } from "lucide-react";

export default function PipelineProgress({ stageIndex, stages }) {
  const safeIndex = Math.min(stageIndex, stages.length - 1);
  const progress = `${((safeIndex + 1) / stages.length) * 100}%`;

  return (
    <section className="processing-card">
      <div className="section-heading center">
        <span className="eyebrow">Analysis in progress</span>
        <h2>Running layered triage workflow</h2>
        <p>CliniScan is structuring evidence, computing risk, and preparing the assessment summary.</p>
      </div>

      <div className="medical-loader" aria-hidden="true">
        <span className="orbit-ring orbit-indigo" />
        <span className="orbit-ring orbit-violet" />
        <span className="orbit-ring orbit-cyan" />
        <span className="medical-cross">
          <Plus size={38} strokeWidth={3} />
        </span>
      </div>

      <div className="processing-progress" aria-label="Analysis progress">
        <span style={{ width: progress }} />
      </div>

      <p key={stages[safeIndex]} className="processing-status">
        {stages[safeIndex]}
      </p>
    </section>
  );
}

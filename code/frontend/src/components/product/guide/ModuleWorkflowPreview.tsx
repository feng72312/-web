import { useState } from "react";
import type { WorkflowGuideConfig } from "../../../config/workflowSteps";

interface ModuleWorkflowPreviewProps {
  workflow: WorkflowGuideConfig;
  previewCount?: number;
}

export function ModuleWorkflowPreview({
  workflow,
  previewCount = 5,
}: ModuleWorkflowPreviewProps) {
  const [expanded, setExpanded] = useState(false);
  const steps = expanded ? workflow.steps : workflow.steps.slice(0, previewCount);
  const hasMore = workflow.steps.length > previewCount;

  return (
    <div className="module-workflow-preview">
      <header>
        <h3>{workflow.title}</h3>
        <p>{workflow.intro}</p>
      </header>
      <ol className="module-workflow-steps">
        {steps.map((step, index) => (
          <li key={step.title}>
            <span className="module-workflow-num">{index + 1}</span>
            <div>
              <strong>{step.title}</strong>
              <p>{step.detail}</p>
              {step.tip && <em>提示: {step.tip}</em>}
            </div>
          </li>
        ))}
      </ol>
      {hasMore && (
        <button
          type="button"
          className="home-btn-secondary module-workflow-toggle"
          onClick={() => setExpanded((v) => !v)}
        >
          {expanded ? "收起流程" : `查看完整流程 (${workflow.steps.length} 步)`}
        </button>
      )}
    </div>
  );
}

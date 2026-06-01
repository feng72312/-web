import { useState } from "react";
import { getWorkflowGuide } from "../config/workflowSteps";

interface WorkflowGuideProps {
  activeTab: string;
  disciplineLabel?: string;
}

export function WorkflowGuide({ activeTab, disciplineLabel }: WorkflowGuideProps) {
  const [collapsed, setCollapsed] = useState(false);
  const guide = getWorkflowGuide(activeTab);

  return (
    <aside
      className={collapsed ? "workflow-guide collapsed" : "workflow-guide"}
      aria-label="预测流程引导"
    >
      <div className="workflow-guide-header">
        <div>
          <p className="workflow-guide-eyebrow">操作引导</p>
          <h2 className="workflow-guide-title">{guide.title}</h2>
          {disciplineLabel && (
            <p className="workflow-guide-discipline">{disciplineLabel}</p>
          )}
        </div>
        <button
          type="button"
          className="workflow-guide-toggle"
          onClick={() => setCollapsed((prev) => !prev)}
          aria-expanded={!collapsed}
        >
          {collapsed ? "展开" : "收起"}
        </button>
      </div>

      {!collapsed && (
        <>
          <p className="workflow-guide-intro">{guide.intro}</p>
          <ol className="workflow-guide-steps">
            {guide.steps.map((step, index) => (
              <li key={step.title} className="workflow-guide-step">
                <span className="workflow-guide-step-num">{index + 1}</span>
                <div className="workflow-guide-step-body">
                  <strong className="workflow-guide-step-title">{step.title}</strong>
                  <p className="workflow-guide-step-detail">{step.detail}</p>
                  {step.tip && (
                    <p className="workflow-guide-step-tip">提示: {step.tip}</p>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </>
      )}
    </aside>
  );
}

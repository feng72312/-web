import { HOME_WORKFLOW_STEPS } from "../../../config/moduleGuideContent";

export function HomeWorkflowStory() {
  return (
    <section className="home-workflow-story">
      <header className="home-section-head">
        <p className="home-light-eyebrow">The Reading Journey</p>
        <h2>从疑问到答案，只需五步</h2>
        <p>过程清晰可见，每一步都知道系统正在做什么。</p>
      </header>
      <ol className="home-workflow-steps">
        {HOME_WORKFLOW_STEPS.map((step, index) => (
          <li key={step.title} className="home-workflow-step">
            <span className="home-workflow-num">{index + 1}</span>
            <div>
              <strong>{step.title}</strong>
              <p>{step.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}

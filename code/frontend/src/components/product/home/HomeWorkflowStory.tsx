import { HOME_WORKFLOW_STEPS } from "../../../config/moduleGuideContent";

export function HomeWorkflowStory() {
  return (
    <section className="home-workflow-story">
      <header className="home-section-head">
        <p className="home-light-eyebrow">Journey</p>
        <h2>一次问事, 五步安心</h2>
        <p>从说出疑惑到心里踏实, 全程有人帮你想、帮你说、陪你聊.</p>
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

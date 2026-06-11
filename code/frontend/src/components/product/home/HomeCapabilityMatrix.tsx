import { HOME_CAPABILITY_ITEMS } from "../../../config/moduleGuideContent";

export function HomeCapabilityMatrix() {
  return (
    <section className="home-capability-matrix">
      <header className="home-section-head">
        <p className="home-light-eyebrow">Why Us</p>
        <h2>为什么选择这里</h2>
        <p>传统功底、智能顾问与沉浸式体验三位一体, 问事更省心, 答案更入心.</p>
      </header>
      <div className="home-capability-grid">
        {HOME_CAPABILITY_ITEMS.map((item) => (
          <article key={item.title} className="home-capability-card">
            <h3>{item.title}</h3>
            <p>{item.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

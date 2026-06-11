import { getLayerOverview } from "../../../config/moduleGuideContent";

export function HomeDomainOverview() {
  const layers = getLayerOverview();

  return (
    <section className="home-domain-overview">
      <header className="home-section-head">
        <p className="home-light-eyebrow">Four Domains</p>
        <h2>四大问事方向</h2>
        <p>先想清楚你要什么答案, 再进预测模块, 向导会帮你挑最合适的术数.</p>
      </header>
      <div className="home-domain-grid">
        {layers.map((layer) => (
          <article key={layer.id} className={`home-domain-card theme-${layer.id}`}>
            <h3>{layer.label}</h3>
            <p className="home-domain-desc">{layer.description}</p>
            <ul className="home-domain-modules">
              {layer.modules.map((m) => (
                <li key={m.id}>{m.label}</li>
              ))}
              {layer.id === "utility" && (
                <li>合盘、诸葛神数、解梦、测字、起名等</li>
              )}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}

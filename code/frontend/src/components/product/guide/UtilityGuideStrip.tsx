import type { UtilityGuideItem } from "../../../config/moduleGuideContent";

interface UtilityGuideStripProps {
  items: UtilityGuideItem[];
  onSelect: (utilityId: string) => void;
}

export function UtilityGuideStrip({ items, onSelect }: UtilityGuideStripProps) {
  return (
    <section className="utility-guide-strip">
      <header className="home-section-head">
        <h3>实用工具</h3>
        <p>合盘、测字、解梦、起名等轻量问事, 点击直达对应工具.</p>
      </header>
      <div className="utility-guide-grid">
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            className={item.enabled ? "utility-guide-card" : "utility-guide-card disabled"}
            disabled={!item.enabled}
            onClick={() => onSelect(item.id)}
          >
            {item.image && (
              <img src={item.image.src} alt="" className="utility-guide-cover" loading="lazy" />
            )}
            <strong>{item.label}</strong>
            <span>{item.description}</span>
            {!item.enabled && <em>待开放</em>}
          </button>
        ))}
      </div>
    </section>
  );
}

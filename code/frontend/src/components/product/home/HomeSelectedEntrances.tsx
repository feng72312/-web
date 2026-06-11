import type { ModuleGuideItem } from "../../../config/moduleGuideContent";

interface HomeSelectedEntrancesProps {
  items: ModuleGuideItem[];
  onEnterModule: (moduleId: string) => void;
  onEnterModules: () => void;
}

const FEATURED_IDS = ["01", "02", "13", "06", "12"];

export function HomeSelectedEntrances({
  items,
  onEnterModule,
  onEnterModules,
}: HomeSelectedEntrancesProps) {
  const featured = FEATURED_IDS.map((id) => items.find((m) => m.id === id)).filter(
    (m): m is ModuleGuideItem => Boolean(m),
  );

  return (
    <section className="home-selected-entrances">
      <header className="home-section-head">
        <p className="home-light-eyebrow">Quick Start</p>
        <h2>精选入口</h2>
        <p>热门入口一键直达; 拿不定主意时, 向导会替你找到最合拍的那一门.</p>
      </header>
      <div className="home-entrance-grid">
        {featured.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`home-entrance-card theme-${item.theme}`}
            onClick={() => onEnterModule(item.id)}
          >
            {item.image && (
              <img src={item.image.src} alt="" className="home-entrance-cover" loading="lazy" />
            )}
            <strong>{item.label}</strong>
            <span>{item.tagline}</span>
          </button>
        ))}
      </div>
      <div className="home-entrance-more">
        <button type="button" className="home-btn-primary" onClick={onEnterModules}>
          打开术数选择向导
        </button>
      </div>
    </section>
  );
}

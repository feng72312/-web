import { ArrowUpRight } from "lucide-react";
import type { ModuleGuideItem } from "../../../config/moduleGuideContent";

interface HomeSelectedEntrancesProps {
  items: ModuleGuideItem[];
  onEnterModule: (moduleId: string) => void;
  onEnterModules: () => void;
}

const FEATURED_IDS = ["01", "02", "11"];

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
      <header className="home-section-head home-section-heading-row">
        <div>
          <p className="home-light-eyebrow">Selected Disciplines</p>
          <h2>从最常用的三门开始</h2>
          <p>看一生格局、问眼前成败、读十二宫人生细节，各有其所长。</p>
        </div>
        <button type="button" className="home-text-action" onClick={onEnterModules}>
          浏览全部术数
          <ArrowUpRight size={17} strokeWidth={1.8} aria-hidden="true" />
        </button>
      </header>
      <div className="home-entrance-grid">
        {featured.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`home-entrance-card theme-${item.theme}`}
            onClick={() => onEnterModule(item.id)}
          >
            <div className="home-entrance-media">
              {item.image && (
                <img
                  src={item.image.src}
                  alt={item.image.alt}
                  className="home-entrance-cover"
                  loading="lazy"
                />
              )}
              <span className="home-entrance-index">0{featured.indexOf(item) + 1}</span>
            </div>
            <span className="home-entrance-copy">
              <strong>{item.label}</strong>
              <span>{item.tagline}</span>
            </span>
            <ArrowUpRight className="home-entrance-arrow" size={19} strokeWidth={1.7} aria-hidden="true" />
          </button>
        ))}
      </div>
    </section>
  );
}

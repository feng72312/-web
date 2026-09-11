import { ArrowRight } from "lucide-react";
import type { ModuleGuideItem } from "../../../config/moduleGuideContent";

interface ModuleRecommendationCardProps {
  item: ModuleGuideItem;
  selected: boolean;
  onSelect: () => void;
  onEnter: () => void;
}

export function ModuleRecommendationCard({
  item,
  selected,
  onSelect,
  onEnter,
}: ModuleRecommendationCardProps) {
  return (
    <article
      className={
        selected
          ? `module-rec-card theme-${item.theme} selected`
          : `module-rec-card theme-${item.theme}`
      }
    >
      <button type="button" className="module-rec-select" onClick={onSelect}>
        {item.image && (
          <img src={item.image.src} alt="" className="module-rec-cover" loading="lazy" />
        )}
        <div className="module-rec-body">
          <h3>{item.label}</h3>
          <p className="module-rec-tagline">{item.tagline}</p>
          {item.recommendedFor.length > 0 && (
            <div className="module-rec-tags">
              {item.recommendedFor.slice(0, 3).map((t) => (
                <span key={t}>{t}</span>
              ))}
            </div>
          )}
          {item.typicalQuestions.length > 0 && (
            <p className="module-rec-example">
              例: {item.typicalQuestions.slice(0, 2).join(" / ")}
            </p>
          )}
        </div>
      </button>
      <button
        type="button"
        className="home-btn-primary module-rec-enter"
        disabled={!item.enabled}
        onClick={onEnter}
      >
        进入测算
        <ArrowRight size={16} strokeWidth={1.8} aria-hidden="true" />
      </button>
    </article>
  );
}

import type { HomeImageMeta } from "../../config/homeModuleImages";
import type { VisualThemeId } from "../../config/productModules";

interface ModuleShowcaseCardProps {
  id: string;
  label: string;
  tagline: string;
  theme: VisualThemeId;
  image?: HomeImageMeta;
  enabled?: boolean;
  hasVisualDemo?: boolean;
  onClick: () => void;
}

export function ModuleShowcaseCard({
  label,
  tagline,
  theme,
  image,
  enabled = true,
  hasVisualDemo = false,
  onClick,
}: ModuleShowcaseCardProps) {
  return (
    <button
      type="button"
      className={`module-showcase-card theme-${theme}`}
      disabled={!enabled}
      onClick={onClick}
    >
      <div className="module-showcase-visual" aria-hidden={image ? undefined : true}>
        {image ? (
          <img
            className="module-showcase-cover"
            src={image.src}
            alt=""
            loading="lazy"
            decoding="async"
          />
        ) : (
          <span className="module-showcase-sigil">*</span>
        )}
      </div>
      <div className="module-showcase-text">
        <strong>{label}</strong>
        <span>{tagline}</span>
        {hasVisualDemo && <em>强视觉实验版</em>}
        {!enabled && <em>待开发</em>}
      </div>
    </button>
  );
}

import type { ModuleShowcaseMeta, VisualThemeId } from "../../config/productModules";
import { LAYER_DESCRIPTIONS, LAYER_LABELS } from "../../config/productModules";
import { getDisciplineIntro } from "../../config/disciplineIntros";
import { getModuleHomeImage, getSectionHomeImage } from "../../config/homeModuleImages";
import type { UtilityId } from "../../utilities/registry";
import { ModuleShowcaseCard } from "./ModuleShowcaseCard";

interface HomeMethodSectionProps {
  theme: VisualThemeId;
  modules: ModuleShowcaseMeta[];
  utilityItems?: {
    id: UtilityId;
    label: string;
    tagline: string;
    theme: VisualThemeId;
    enabled: boolean;
  }[];
  onSelectModule: (moduleId: string) => void;
  onSelectUtility?: (utilityId: UtilityId) => void;
}

export function HomeMethodSection({
  theme,
  modules,
  utilityItems,
  onSelectModule,
  onSelectUtility,
}: HomeMethodSectionProps) {
  const sectionImage = getSectionHomeImage(theme);
  const itemCount = modules.length + (utilityItems?.length ?? 0);
  const sampleIntro =
    theme === "utility"
      ? getDisciplineIntro("12")
      : modules[0]
        ? getDisciplineIntro(modules[0].id)
        : null;

  return (
    <section className={`home-method-section theme-${theme}`}>
      <div className="home-method-hero">
        <div
          className={sectionImage ? "home-method-visual has-cover" : "home-method-visual"}
          aria-hidden="true"
          style={
            sectionImage
              ? { backgroundImage: `url(${sectionImage.src})` }
              : undefined
          }
        >
          <div className="home-method-visual-inner">
            <span className="home-method-visual-title">{LAYER_LABELS[theme]}</span>
            <span className="home-method-visual-sub">Destiny Layer</span>
          </div>
        </div>
        <div className="home-method-copy">
          <p className="product-eyebrow">{LAYER_LABELS[theme]}</p>
          <h2>{LAYER_LABELS[theme]}</h2>
          <p>{LAYER_DESCRIPTIONS[theme]}</p>
          {sampleIntro && (
            <ul className="home-method-advantages">
              {sampleIntro.advantages.slice(0, 3).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div
        className={
          itemCount === 1
            ? "home-method-grid home-method-grid--single"
            : "home-method-grid"
        }
      >
        {modules.map((module) => (
          <ModuleShowcaseCard
            key={module.id}
            id={module.id}
            label={module.label}
            tagline={module.tagline}
            theme={module.theme}
            image={getModuleHomeImage(module.id)}
            enabled={module.enabled}
            hasVisualDemo={module.hasVisualDemo}
            onClick={() => onSelectModule(module.id)}
          />
        ))}
        {theme === "utility" &&
          utilityItems?.map((item) => (
            <ModuleShowcaseCard
              key={item.id}
              id={item.id}
              label={item.label}
              tagline={item.tagline}
              theme={item.theme}
              image={getModuleHomeImage(item.id)}
              enabled={item.enabled}
              onClick={() => onSelectUtility?.(item.id)}
            />
          ))}
      </div>
    </section>
  );
}

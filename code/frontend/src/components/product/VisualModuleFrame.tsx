import type { ReactNode } from "react";
import { getDisciplineIntro } from "../../config/disciplineIntros";
import type { VisualThemeId } from "../../config/productModules";

interface VisualModuleFrameProps {
  moduleId: string;
  label: string;
  theme: VisualThemeId;
  hasVisualDemo?: boolean;
  onBack: () => void;
  children: ReactNode;
}

export function VisualModuleFrame({
  moduleId,
  label,
  theme,
  hasVisualDemo = false,
  onBack,
  children,
}: VisualModuleFrameProps) {
  const intro = getDisciplineIntro(moduleId);

  return (
    <div className={`visual-module-frame theme-${theme}`}>
      <header className="visual-module-head">
        <button type="button" className="product-ghost-button" onClick={onBack}>
          返回模块列表
        </button>
        <div className="visual-module-title">
          <p className="product-eyebrow">Prediction Module</p>
          <h2>{label}</h2>
          {intro?.subtitle && <span>{intro.subtitle}</span>}
        </div>
        <div className={`visual-module-banner theme-${theme}`} aria-hidden="true">
          <span>*</span>
        </div>
      </header>

      {intro && (
        <aside className="visual-module-intro">
          <p>{intro.category}</p>
          {hasVisualDemo && (
            <p className="visual-module-demo-hint">
              本模块支持「进入视觉实验版」, 可在模块内切换强视觉工作台.
            </p>
          )}
          <ul>
            {intro.advantages.slice(0, 4).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </aside>
      )}

      <div className="visual-module-body">{children}</div>
    </div>
  );
}

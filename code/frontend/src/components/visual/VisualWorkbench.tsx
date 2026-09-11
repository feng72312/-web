import { useEffect, type ReactNode } from "react";
import type { VisualTheme } from "./VisualSigil";
import { VisualSigil } from "./VisualSigil";

interface VisualWorkbenchProps {
  moduleId: string;
  title: string;
  subtitle?: string;
  theme: VisualTheme;
  error?: string;
  input: ReactNode;
  stage: ReactNode;
  oracle?: ReactNode;
  interpretation?: ReactNode;
  className?: string;
  inputPlacement?: "side" | "top";
}

export function VisualWorkbench({
  moduleId,
  title,
  subtitle,
  theme,
  error,
  input,
  stage,
  oracle,
  interpretation,
  className = "",
  inputPlacement = "side",
}: VisualWorkbenchProps) {
  useEffect(() => {
    document.body.classList.add("visual-workbench-immersive");
    return () => document.body.classList.remove("visual-workbench-immersive");
  }, []);

  return (
    <div className={`visual-workbench theme-${theme} ${className}`.trim()} data-module={moduleId}>
      <header className="visual-workbench-topbar">
        <div className="visual-workbench-brand">
          <VisualSigil theme={theme} size="sm" />
          <div>
            <p className="visual-eyebrow">Prediction Workbench</p>
            <h2>{title}</h2>
            {subtitle && <span className="visual-workbench-subtitle">{subtitle}</span>}
          </div>
        </div>
        <ol className="visual-workbench-phases" aria-label="测算流程">
          <li>
            <span>01</span>
            <strong>录入信息</strong>
          </li>
          <li>
            <span>02</span>
            <strong>查阅盘面</strong>
          </li>
          <li>
            <span>03</span>
            <strong>获取解读</strong>
          </li>
        </ol>
      </header>

      {error && <div className="visual-workbench-error">{error}</div>}

      <div
        className={
          inputPlacement === "top"
            ? "visual-workbench-grid visual-workbench-grid-top-input"
            : "visual-workbench-grid"
        }
      >
        {inputPlacement === "top" ? (
          <section className="visual-workbench-input-top">{input}</section>
        ) : (
          <aside className="visual-workbench-input">{input}</aside>
        )}
        <main className="visual-workbench-stage">{stage}</main>
        {oracle && <aside className="visual-workbench-oracle">{oracle}</aside>}
      </div>

      {interpretation && <footer className="visual-workbench-interpret">{interpretation}</footer>}
    </div>
  );
}

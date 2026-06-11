import type { ReactNode } from "react";

interface VisualPanelProps {
  title?: string;
  eyebrow?: string;
  hint?: string;
  accent?: boolean;
  children: ReactNode;
  actions?: ReactNode;
  className?: string;
}

export function VisualPanel({
  title,
  eyebrow,
  hint,
  accent = false,
  children,
  actions,
  className = "",
}: VisualPanelProps) {
  return (
    <section className={`visual-panel ${accent ? "accent" : ""} ${className}`.trim()}>
      {(title || eyebrow || hint) && (
        <header className="visual-panel-head">
          <div>
            {eyebrow && <p className="visual-eyebrow">{eyebrow}</p>}
            {title && <h3>{title}</h3>}
            {hint && <p className="visual-panel-hint">{hint}</p>}
          </div>
          {actions}
        </header>
      )}
      <div className="visual-panel-body">{children}</div>
    </section>
  );
}

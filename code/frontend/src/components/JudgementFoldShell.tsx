import type { ReactNode, Ref } from "react";
import { formatConfidenceBand } from "../utils/judgementDisplay";

export { formatConfidenceBand };

interface JudgementFoldShellProps {
  id?: string;
  title: string;
  hint?: string;
  forceOpen?: boolean;
  sectionRef?: Ref<HTMLElement>;
  className?: string;
  children: ReactNode;
}

export function JudgementFoldShell({
  id,
  title,
  hint,
  forceOpen = false,
  sectionRef,
  className = "bazi-report-card bazi-judgement-panel",
  children,
}: JudgementFoldShellProps) {
  return (
    <section ref={sectionRef} id={id} className={className}>
      <details className="judgement-fold-panel" open={forceOpen || undefined}>
        <summary className="judgement-fold-summary">
          <span className="judgement-fold-title">{title}</span>
          {hint ? <span className="judgement-fold-hint">{hint}</span> : null}
        </summary>
        <div className="judgement-fold-body">{children}</div>
      </details>
    </section>
  );
}

interface JudgementSubFoldProps {
  title: string;
  defaultOpen?: boolean;
  children: ReactNode;
}

export function JudgementSubFold({
  title,
  defaultOpen = false,
  children,
}: JudgementSubFoldProps) {
  return (
    <details className="judgement-sub-fold" open={defaultOpen || undefined}>
      <summary>{title}</summary>
      <div className="judgement-sub-fold-body">{children}</div>
    </details>
  );
}

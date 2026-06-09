import type { ReactNode } from "react";
import { cn } from "../../lib/cn";

interface ResultCardProps {
  title: string;
  children: ReactNode;
  className?: string;
  actions?: ReactNode;
}

export function ResultCard({ title, children, className, actions }: ResultCardProps) {
  return (
    <section className={cn("ds-result-card panel", className)}>
      <div className="ds-result-card-head">
        <h3>{title}</h3>
        {actions}
      </div>
      <div className="ds-result-card-body">{children}</div>
    </section>
  );
}

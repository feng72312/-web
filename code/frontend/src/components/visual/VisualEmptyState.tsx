import type { ReactNode } from "react";
import type { VisualTheme } from "./VisualSigil";
import { VisualSigil } from "./VisualSigil";

interface VisualEmptyStateProps {
  title: string;
  description: string;
  theme: VisualTheme;
  action?: ReactNode;
}

export function VisualEmptyState({ title, description, theme, action }: VisualEmptyStateProps) {
  return (
    <div className={`visual-empty theme-${theme}`}>
      <VisualSigil theme={theme} size="lg" />
      <strong>{title}</strong>
      <p>{description}</p>
      {action}
    </div>
  );
}

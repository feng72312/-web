import type { InterpretStyle } from "../utils/interpretStyle";

interface InterpretStyleButtonsProps {
  professionalLoading: boolean;
  plainLoading: boolean;
  disabled?: boolean;
  onProfessional: () => void;
  onPlain: () => void;
}

export function InterpretStyleButtons({
  professionalLoading,
  plainLoading,
  disabled = false,
  onProfessional,
  onPlain,
}: InterpretStyleButtonsProps) {
  return (
    <div className="action-row interpret-style-actions">
      <button
        type="button"
        className="primary-btn"
        disabled={disabled || professionalLoading || plainLoading}
        onClick={onProfessional}
      >
        {professionalLoading ? "命理师专用解读中..." : "命理师专用解读"}
      </button>
      <button
        type="button"
        className="secondary"
        disabled={disabled || professionalLoading || plainLoading}
        onClick={onPlain}
      >
        {plainLoading ? "AI深度解读中..." : "AI深度解读"}
      </button>
    </div>
  );
}

export type { InterpretStyle };

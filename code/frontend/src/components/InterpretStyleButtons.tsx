import type { InterpretStyle } from "../utils/interpretStyle";

interface InterpretStyleButtonsProps {
  professionalLoading: boolean;
  plainLoading: boolean;
  disabled?: boolean;
  onLoadingStart?: (style: InterpretStyle) => void;
  onProfessional: () => void;
  onPlain: () => void;
}

export function InterpretStyleButtons({
  professionalLoading,
  plainLoading,
  disabled = false,
  onLoadingStart,
  onProfessional,
  onPlain,
}: InterpretStyleButtonsProps) {
  const busy = disabled || professionalLoading || plainLoading;

  const handleClick = (style: InterpretStyle, action: () => void) => {
    if (busy) {
      return;
    }
    onLoadingStart?.(style);
    action();
  };

  return (
    <div className="action-row interpret-style-actions">
      <button
        type="button"
        className="primary-btn"
        disabled={busy}
        onClick={() => handleClick("plain", onPlain)}
      >
        {plainLoading ? "AI深度解读中..." : "AI深度解读"}
      </button>
      <button
        type="button"
        className="secondary"
        disabled={busy}
        onClick={() => handleClick("professional", onProfessional)}
      >
        {professionalLoading ? "命理师专用解读中..." : "命理师专用解读"}
      </button>
    </div>
  );
}

export type { InterpretStyle };

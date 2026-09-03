import type { InterpretStyle } from "../utils/interpretStyle";
import { useInterpretQueueNotice } from "../hooks/useInterpretQueueNotice";

interface InterpretStyleButtonsProps {
  professionalLoading: boolean;
  plainLoading: boolean;
  disabled?: boolean;
  loadingLabel?: string;
  onLoadingStart?: (style: InterpretStyle) => void;
  onProfessional: () => void;
  onPlain: () => void;
}

export function InterpretStyleButtons({
  professionalLoading,
  plainLoading,
  disabled = false,
  loadingLabel,
  onLoadingStart,
  onProfessional,
  onPlain,
}: InterpretStyleButtonsProps) {
  const queueNotice = useInterpretQueueNotice();
  const busy = disabled || professionalLoading || plainLoading;
  const plainLabel = plainLoading
    ? queueNotice || loadingLabel || "AI深度解读中..."
    : "AI深度解读";
  const proLabel = professionalLoading
    ? queueNotice || loadingLabel || "命理师专用解读中..."
    : "命理师专用解读";

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
        {plainLabel}
      </button>
      <button
        type="button"
        className="secondary"
        disabled={busy}
        onClick={() => handleClick("professional", onProfessional)}
      >
        {proLabel}
      </button>
    </div>
  );
}

export type { InterpretStyle };

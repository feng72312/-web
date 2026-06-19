import type { ConfidenceBand } from "../types/consensus";
import { formatConfidenceBand } from "../utils/judgementDisplay";

const BAND_FILL: Record<ConfidenceBand, number> = {
  strong: 85,
  medium: 55,
  weak: 25,
};

interface InterpretConfidenceStripProps {
  band?: ConfidenceBand | string;
  score?: number;
  conflicts?: string[];
}

export function InterpretConfidenceStrip({
  band = "medium",
  score,
  conflicts,
}: InterpretConfidenceStripProps) {
  const fill =
    score != null
      ? Math.min(100, Math.max(0, Math.round(score * 100)))
      : BAND_FILL[band as ConfidenceBand] ?? 50;
  const label = formatConfidenceBand(band) || "中等";

  return (
    <div className="interpret-confidence-strip" aria-label={`判盘依据置信度 ${label}`}>
      <div className="interpret-confidence-strip-head">
        <span className="interpret-confidence-strip-label">判盘依据置信度</span>
        <span className={`interpret-confidence-strip-band band-${band}`}>{label}</span>
      </div>
      <div className="interpret-confidence-strip-track" aria-hidden="true">
        <div
          className={`interpret-confidence-strip-fill band-${band}`}
          style={{ width: `${fill}%` }}
        />
      </div>
      {conflicts && conflicts.length > 0 ? (
        <p className="interpret-confidence-strip-note">
          存在 {conflicts.length} 处观点差异, 解读已按分层逻辑处理
        </p>
      ) : null}
    </div>
  );
}

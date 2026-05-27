import type { Chart } from "../types/bazi";
import { wuxingClass } from "../utils/wuxing";

const LABELS: Record<string, string> = {
  year: "年柱",
  month: "月柱",
  day: "日柱",
  hour: "时柱",
};

interface Props {
  chart: Chart;
  luckLoading?: boolean;
  onOpenDetail?: () => void;
  onOpenLuck?: () => void;
}

export function FourPillars({ chart, luckLoading = false, onOpenDetail, onOpenLuck }: Props) {
  const keys = ["year", "month", "day", "hour"] as const;

  return (
    <div className="pillars-entry">
      <div className="pillars-grid">
        {keys.map((key) => {
          const p = chart.pillars[key];
          const isDay = key === "day";
          return (
            <button
              key={key}
              type="button"
              className={`pillar-card pillar-click ${isDay ? "pillar-day" : ""}`}
              onClick={onOpenDetail}
              title="查看四柱详盘"
            >
              <div className="pillar-label">{LABELS[key]}</div>
              <div className="pillar-ganzhi">
                <span className={wuxingClass(p.ganWuxing)}>{p.gan}</span>
                <span className={wuxingClass(p.zhiWuxing)}>{p.zhi}</span>
              </div>
              <div className="pillar-meta">{p.nayin}</div>
              {isDay && <div className="pillar-tag">日主</div>}
            </button>
          );
        })}
      </div>

      <div className="pillars-actions">
        <button type="button" className="secondary" onClick={onOpenDetail}>
          四柱详盘
        </button>
        <button
          type="button"
          className="secondary"
          disabled={luckLoading}
          onClick={onOpenLuck}
        >
          {luckLoading ? "加载大运..." : "大运流年"}
        </button>
      </div>
    </div>
  );
}

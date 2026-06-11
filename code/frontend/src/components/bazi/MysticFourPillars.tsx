import type { Chart } from "../../types/bazi";
import { wuxingClass } from "../../utils/wuxing";

const LABELS: Record<string, string> = {
  year: "年柱",
  month: "月柱",
  day: "日柱",
  hour: "时柱",
};

interface MysticFourPillarsProps {
  chart: Chart;
  luckLoading?: boolean;
  onOpenDetail?: () => void;
  onOpenLuck?: () => void;
}

export function MysticFourPillars({
  chart,
  luckLoading = false,
  onOpenDetail,
  onOpenLuck,
}: MysticFourPillarsProps) {
  const keys = ["year", "month", "day", "hour"] as const;

  return (
    <div className="mystic-pillars-stage">
      <div className="mystic-pillars-grid">
        {keys.map((key) => {
          const pillar = chart.pillars[key];
          const isDay = key === "day";
          return (
            <button
              key={key}
              type="button"
              className={isDay ? "mystic-pillar-card day" : "mystic-pillar-card"}
              onClick={onOpenDetail}
              title="查看四柱详盘"
            >
              <span className="mystic-pillar-label">{LABELS[key]}</span>
              <div className="mystic-pillar-ganzhi">
                <span className={`mystic-stem ${wuxingClass(pillar.ganWuxing)}`}>
                  {pillar.gan}
                </span>
                <span className={`mystic-branch ${wuxingClass(pillar.zhiWuxing)}`}>
                  {pillar.zhi}
                </span>
              </div>
              <span className="mystic-pillar-nayin">{pillar.nayin}</span>
              <span className="mystic-pillar-shishen">{pillar.shishenGan}</span>
              {isDay && <em className="mystic-pillar-badge">日主</em>}
            </button>
          );
        })}
      </div>

      <div className="mystic-pillars-actions">
        <button type="button" className="bazi-ghost-button" onClick={onOpenDetail}>
          四柱详盘
        </button>
        <button
          type="button"
          className="bazi-gold-button"
          disabled={luckLoading}
          onClick={onOpenLuck}
        >
          {luckLoading ? "加载大运..." : "大运流年"}
        </button>
      </div>
    </div>
  );
}

import type { Chart } from "../../types/bazi";
import { wuxingClass } from "../../utils/wuxing";

const WUXING_ORDER = ["木", "火", "土", "金", "水"];

interface BaziReportHeaderProps {
  chart: Chart;
}

export function BaziReportHeader({ chart }: BaziReportHeaderProps) {
  const maxCount = Math.max(...WUXING_ORDER.map((wx) => chart.wuxingCount[wx] ?? 0), 1);

  return (
    <header className="bazi-report-header bazi-report-card">
      <div className="bazi-report-header-main">
        <div>
          <span className="bazi-card-eyebrow">命盘概览</span>
          <h3>{chart.input.name || "命主"}</h3>
        </div>
        <div className="bazi-report-header-tags">
          <span className="bazi-report-tag">
            日主 <strong className={wuxingClass(chart.dayMasterWuxing)}>{chart.dayMaster}</strong>
          </span>
          <span className="bazi-report-tag">
            大运 {chart.dayunForward ? "顺行" : "逆行"}
          </span>
        </div>
      </div>

      <div className="bazi-report-header-meta">
        <div className="bazi-report-meta-row">
          <span className="bazi-report-meta-label">公历</span>
          <span>{chart.solar}</span>
        </div>
        <div className="bazi-report-meta-row">
          <span className="bazi-report-meta-label">农历</span>
          <span>{chart.lunar}</span>
        </div>
        <div className="bazi-report-meta-row bazi-report-meta-pillars">
          <span className="bazi-report-meta-label">四柱</span>
          <span className="bazi-report-meta-ganzhi">
            {(["year", "month", "day", "hour"] as const).map((key) => (
              <span key={key} className="bazi-report-pillar-pair">
                <strong className={wuxingClass(chart.pillars[key].ganWuxing)}>
                  {chart.pillars[key].gan}
                </strong>
                <strong className={wuxingClass(chart.pillars[key].zhiWuxing)}>
                  {chart.pillars[key].zhi}
                </strong>
              </span>
            ))}
          </span>
        </div>
      </div>

      <div className="bazi-report-wuxing">
        <span className="bazi-card-eyebrow">五行分布</span>
        <div className="bazi-report-wuxing-grid">
          {WUXING_ORDER.map((wx) => {
            const count = chart.wuxingCount[wx] ?? 0;
            const width = Math.round((count / maxCount) * 100);
            return (
              <div key={wx} className="bazi-report-wuxing-row">
                <span className={`bazi-report-wuxing-name ${wuxingClass(wx)}`}>{wx}</span>
                <div className="bazi-report-wuxing-track">
                  <div
                    className={`bazi-report-wuxing-fill ${wuxingClass(wx)}`}
                    style={{ width: `${width}%` }}
                  />
                </div>
                <span className="bazi-report-wuxing-count">{count}</span>
              </div>
            );
          })}
        </div>
      </div>
    </header>
  );
}

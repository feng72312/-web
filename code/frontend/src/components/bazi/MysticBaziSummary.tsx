import type { Chart } from "../../types/bazi";
import { wuxingClass } from "../../utils/wuxing";

const WUXING_ORDER = ["木", "火", "土", "金", "水"];

interface MysticBaziSummaryProps {
  chart: Chart;
}

export function MysticBaziSummary({ chart }: MysticBaziSummaryProps) {
  const maxCount = Math.max(...WUXING_ORDER.map((wx) => chart.wuxingCount[wx] ?? 0), 1);

  return (
    <div className="mystic-bazi-summary">
      <div className="mystic-summary-row">
        <span className="mystic-summary-label">日主</span>
        <strong className={wuxingClass(chart.dayMasterWuxing)}>{chart.dayMaster}</strong>
      </div>
      <div className="mystic-summary-row">
        <span className="mystic-summary-label">公历</span>
        <span>{chart.solar}</span>
      </div>
      <div className="mystic-summary-row">
        <span className="mystic-summary-label">农历</span>
        <span>{chart.lunar}</span>
      </div>
      <div className="mystic-summary-row">
        <span className="mystic-summary-label">大运</span>
        <span>{chart.dayunForward ? "顺行" : "逆行"}</span>
      </div>

      <div className="mystic-wuxing-bars">
        <span className="mystic-card-eyebrow">五行分布</span>
        {WUXING_ORDER.map((wx) => {
          const count = chart.wuxingCount[wx] ?? 0;
          const width = Math.round((count / maxCount) * 100);
          return (
            <div key={wx} className="mystic-wuxing-bar-row">
              <span className={`mystic-wuxing-name ${wuxingClass(wx)}`}>{wx}</span>
              <div className="mystic-wuxing-track">
                <div
                  className={`mystic-wuxing-fill ${wuxingClass(wx)}`}
                  style={{ width: `${width}%` }}
                />
              </div>
              <span className="mystic-wuxing-count">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

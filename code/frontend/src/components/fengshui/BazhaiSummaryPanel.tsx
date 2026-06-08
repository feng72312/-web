import type { FengshuiChart } from "../../types/fengshui";

interface BazhaiSummaryPanelProps {
  chart: FengshuiChart;
}

export function BazhaiSummaryPanel({ chart }: BazhaiSummaryPanelProps) {
  if (!chart.mingGua || !chart.zhaiGua || !chart.directions) {
    return null;
  }
  const ji = chart.directions.filter((row) => row.auspicious);
  const xiong = chart.directions.filter((row) => !row.auspicious);

  return (
    <div className="fengshui-summary-panel">
      <h3>八宅摘要</h3>
      <dl className="qimen-meta-dl">
        <dt>命卦</dt>
        <dd>
          {chart.mingGua.alias} ({chart.mingGua.groupLabel})
        </dd>
        <dt>宅卦</dt>
        <dd>
          {chart.zhaiGua.label} / {chart.zhaiGua.alias} ({chart.zhaiGua.groupLabel})
        </dd>
        <dt>人宅相配</dt>
        <dd className={chart.compatible ? "fengshui-match-yes" : "fengshui-match-no"}>
          {chart.compatible ? "相配" : "不配"}
        </dd>
      </dl>

      <div className="fengshui-direction-groups">
        <section>
          <h4>四大吉方</h4>
          <ul>
            {ji.map((row) => (
              <li key={row.type}>
                {row.label} - {row.direction} ({row.trigram})
              </li>
            ))}
          </ul>
        </section>
        <section>
          <h4>四凶方</h4>
          <ul>
            {xiong.map((row) => (
              <li key={row.type}>
                {row.label} - {row.direction} ({row.trigram})
              </li>
            ))}
          </ul>
        </section>
      </div>

      {chart.advice && chart.advice.length > 0 && (
        <section className="fengshui-advice">
          <h4>布局参考</h4>
          <ul>
            {chart.advice.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

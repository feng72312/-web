import type { Chart, PillarDetailColumn } from "../../types/bazi";
import { ganWuxingClass, wuxingClass } from "../../utils/wuxing";

function ColoredHideStemLine({ text }: { text: string }) {
  const gan = text.charAt(0);
  const rest = text.slice(1);
  return (
    <div className="bazi-hide-stem-line">
      <span className={`bazi-hide-stem-gan ${ganWuxingClass(gan)}`}>{gan}</span>
      <span className="bazi-hide-stem-meta">{rest}</span>
    </div>
  );
}

const COLUMN_KEYS = ["year", "month", "day", "hour"] as const;
const COLUMN_LABELS: Record<(typeof COLUMN_KEYS)[number], string> = {
  year: "年柱",
  month: "月柱",
  day: "日柱",
  hour: "时柱",
};

function buildColumns(chart: Chart): PillarDetailColumn[] {
  if (chart.pillarDetail?.columns?.length) {
    return chart.pillarDetail.columns;
  }
  return COLUMN_KEYS.map((key) => {
    const pillar = chart.pillars[key];
    return {
      key,
      label: COLUMN_LABELS[key],
      shishen: pillar.shishenGan,
      gan: pillar.gan,
      zhi: pillar.zhi,
      ganWuxing: pillar.ganWuxing,
      zhiWuxing: pillar.zhiWuxing,
      hideStems: pillar.hideGan.map((gan, idx) => {
        const label = pillar.shishenZhi[idx];
        return label ? `${gan}(${label})` : gan;
      }),
      nayin: pillar.nayin,
      xunkong: "-",
      shenSha: [],
    };
  });
}

interface BaziPillarReportTableProps {
  chart: Chart;
}

export function BaziPillarReportTable({ chart }: BaziPillarReportTableProps) {
  const cols = buildColumns(chart);

  return (
    <section className="bazi-report-card bazi-pillar-report-table">
      <div className="bazi-report-section-head">
        <span className="bazi-card-eyebrow">四柱详盘</span>
        <h3>基本命盘</h3>
      </div>

      <div className="bazi-pillar-table-wrap">
        <table className="bazi-pillar-table detail-table">
          <thead>
            <tr>
              <th className="bazi-pillar-row-label">项目</th>
              {cols.map((col) => (
                <th key={col.key}>{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <th className="bazi-pillar-row-label">十神</th>
              {cols.map((col) => (
                <td key={col.key} className={col.key === "day" ? "day-role" : ""}>
                  {col.shishen}
                </td>
              ))}
            </tr>
            <tr className="detail-alt">
              <th className="bazi-pillar-row-label">天干</th>
              {cols.map((col) => (
                <td key={col.key} className="cell-ganzhi">
                  <span className={`gz-large bazi-report-ganzhi ${wuxingClass(col.ganWuxing)}`}>
                    {col.gan}
                  </span>
                </td>
              ))}
            </tr>
            <tr>
              <th className="bazi-pillar-row-label">地支</th>
              {cols.map((col) => (
                <td key={col.key} className="cell-ganzhi">
                  <span className={`gz-large bazi-report-ganzhi ${wuxingClass(col.zhiWuxing)}`}>
                    {col.zhi}
                  </span>
                </td>
              ))}
            </tr>
            <tr className="detail-alt">
              <th className="bazi-pillar-row-label">藏干</th>
              {cols.map((col) => (
                <td key={col.key} className="cell-stack">
                  {col.hideStems.length
                    ? col.hideStems.map((item) => (
                        <ColoredHideStemLine key={item} text={item} />
                      ))
                    : "-"}
                </td>
              ))}
            </tr>
            <tr>
              <th className="bazi-pillar-row-label">纳音</th>
              {cols.map((col) => (
                <td key={col.key}>{col.nayin}</td>
              ))}
            </tr>
            <tr className="detail-alt">
              <th className="bazi-pillar-row-label">空亡</th>
              {cols.map((col) => (
                <td key={col.key}>{col.xunkong || "-"}</td>
              ))}
            </tr>
            <tr>
              <th className="bazi-pillar-row-label">神煞</th>
              {cols.map((col) => (
                <td key={col.key} className="cell-stack">
                  {col.shenSha.length
                    ? col.shenSha.map((item) => <div key={item}>{item}</div>)
                    : "-"}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}

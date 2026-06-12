import type { Chart, PillarDetailColumn } from "../../types/bazi";
import { wuxingClass } from "../../utils/wuxing";
import { parseBaziRelations } from "./parseBaziRelations";

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
      hideStems: pillar.hideGan,
      nayin: pillar.nayin,
      xunkong: "-",
      shenSha: [],
    };
  });
}

interface BaziRelationDiagramProps {
  chart: Chart;
}

export function BaziRelationDiagram({ chart }: BaziRelationDiagramProps) {
  const columns = buildColumns(chart);
  const stemNotes = chart.pillarDetail?.stemNotes;
  const branchNotes = chart.pillarDetail?.branchNotes;
  const links = parseBaziRelations(columns, stemNotes, branchNotes);
  const hasNotes = Boolean(stemNotes || branchNotes);

  return (
    <section className="bazi-report-card bazi-relation-diagram">
      <div className="bazi-report-section-head">
        <span className="bazi-card-eyebrow">关系</span>
        <h3>智能四柱图示</h3>
      </div>

      <div className="bazi-relation-stage">
        <div className="bazi-relation-columns">
          {columns.map((col) => (
            <div key={col.key} className="bazi-relation-col">
              <span className="bazi-relation-col-label">{col.label}</span>
              <span className={`bazi-relation-gan ${wuxingClass(col.ganWuxing)}`}>{col.gan}</span>
              <span className={`bazi-relation-zhi ${wuxingClass(col.zhiWuxing)}`}>{col.zhi}</span>
            </div>
          ))}
        </div>

        {links.length > 0 ? (
          <div className="bazi-relation-links">
            {links.map((link) => (
              <div
                key={link.id}
                className={`bazi-relation-link ${link.layer === "stem" ? "stem" : "branch"}`}
                style={{
                  gridColumn: `${Math.min(link.fromIndex, link.toIndex) + 1} / ${Math.max(link.fromIndex, link.toIndex) + 2}`,
                }}
              >
                <span className="bazi-relation-link-line" />
                <span className="bazi-relation-link-label">{link.label}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="bazi-relation-empty">
            {hasNotes ? "暂无明显冲合害关系" : "暂无关系图示数据"}
          </p>
        )}
      </div>
    </section>
  );
}

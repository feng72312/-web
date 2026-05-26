import type { PillarDetail } from "../types/bazi";
import { wuxingClass } from "../utils/wuxing";

interface Props {
  detail: PillarDetail;
  onBack: () => void;
}

export function PillarDetailView({ detail, onBack }: Props) {
  const cols = detail.columns;

  return (
    <section className="chart-detail panel">
      <div className="chart-detail-header">
        <button type="button" className="secondary back-btn" onClick={onBack}>
          返回
        </button>
        <h2>四柱详盘</h2>
      </div>

      <div className="detail-table-wrap">
        <table className="detail-table">
          <thead>
            <tr className="detail-head">
              <th>四柱:</th>
              {cols.map((col) => (
                <th key={col.key}>{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <th className="row-label">十神</th>
              {cols.map((col) => (
                <td key={col.key} className={col.key === "day" ? "day-role" : ""}>
                  {col.shishen}
                </td>
              ))}
            </tr>
            <tr className="detail-alt">
              <th className="row-label">天干</th>
              {cols.map((col) => (
                <td key={col.key} className="cell-ganzhi">
                  <span className={`gz-large ${wuxingClass(col.ganWuxing)}`}>{col.gan}</span>
                </td>
              ))}
            </tr>
            <tr>
              <th className="row-label">地支</th>
              {cols.map((col) => (
                <td key={col.key} className="cell-ganzhi">
                  <span className={`gz-large ${wuxingClass(col.zhiWuxing)}`}>{col.zhi}</span>
                </td>
              ))}
            </tr>
            <tr className="detail-alt">
              <th className="row-label">藏干</th>
              {cols.map((col) => (
                <td key={col.key} className="cell-stack">
                  {col.hideStems.map((item) => (
                    <div key={item}>{item}</div>
                  ))}
                </td>
              ))}
            </tr>
            <tr>
              <th className="row-label">纳音</th>
              {cols.map((col) => (
                <td key={col.key}>{col.nayin}</td>
              ))}
            </tr>
            <tr className="detail-alt">
              <th className="row-label">空亡</th>
              {cols.map((col) => (
                <td key={col.key}>{col.xunkong}</td>
              ))}
            </tr>
            <tr>
              <th className="row-label">神煞</th>
              {cols.map((col) => (
                <td key={col.key} className="cell-stack">
                  {col.shenSha.length ? col.shenSha.map((item) => <div key={item}>{item}</div>) : "-"}
                </td>
              ))}
            </tr>
            <tr className="detail-note-row">
              <th className="row-label note-label">天干留意</th>
              <td colSpan={4}>{detail.stemNotes}</td>
            </tr>
            <tr className="detail-note-row detail-alt">
              <th className="row-label note-label">地支留意</th>
              <td colSpan={4}>{detail.branchNotes}</td>
            </tr>
            <tr className="detail-note-row">
              <th className="row-label note-label">称骨重量</th>
              <td colSpan={4}>{detail.boneWeight}</td>
            </tr>
            <tr className="detail-note-row detail-alt">
              <th className="row-label note-label">称骨评语</th>
              <td colSpan={4}>{detail.boneComment}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}

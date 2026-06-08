import type { XingmingChart } from "../../types/xingming";

interface Props {
  chart: XingmingChart;
}

export function XingmingBoard({ chart }: Props) {
  return (
    <div className="xingming-board">
      <div className="xingming-bodies">
        <h3>七政四余</h3>
        <ul>
          {chart.bodies.map((b) => (
            <li key={b.id}>
              {b.label} {b.mansion}宿 {b.mansionDegree.toFixed(1)}度
              {b.palace ? ` 落${b.palace}` : ""}
              {b.retrograde ? " 逆行" : ""}
            </li>
          ))}
        </ul>
      </div>
      <div className="xingming-palaces">
        <h3>十二宫</h3>
        <div className="xingming-palace-grid">
          {chart.palaces.map((p) => (
            <div key={p.index} className="xingming-palace-cell">
              <div className="xingming-palace-title">
                {p.name} {p.branch}
              </div>
              <div className="xingming-palace-stars">
                {[...p.majorStars, ...p.minorStars].map((s) => s.label).join(" ") || "-"}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="xingming-limits">
        <p>
          流年太岁: {chart.limits.taiSui.branch} 入{chart.limits.taiSui.palace}
        </p>
        <p>昼夜: {chart.meta.isDay ? "日生" : "夜生"}</p>
      </div>
    </div>
  );
}

import type { LiurenPan } from "../../types/liuren";

interface Props {
  pan: LiurenPan;
}

export function SiKeSanChuanPanel({ pan }: Props) {
  const sk = pan.siKe;
  const sc = pan.sanChuan;
  return (
    <div className="liuren-sike-panel chart-subpanel">
      <h3 className="chart-subpanel-title">四课三传</h3>
      <p className="meta-line">
        节气 {pan.jieqi} | 月将 {pan.yueJiang}
        {pan.geJu.sub ? ` | ${pan.geJu.sub}` : ""}
      </p>
      <div className="liuren-ke-grid">
        {(["yi", "er", "san", "si"] as const).map((k, i) => (
          <div key={k} className="liuren-ke-cell">
            <span className="ke-label">{i + 1}课</span>
            <span>{sk[k].pair}</span>
            <span className="ke-gen">{sk[k].general}</span>
          </div>
        ))}
      </div>
      <div className="liuren-chuan-row">
        {(["chu", "zhong", "mo"] as const).map((k, i) => (
          <div key={k} className="liuren-chuan-cell">
            <span className="ke-label">
              {i === 0 ? "初传" : i === 1 ? "中传" : "末传"}
            </span>
            <span>
              {sc[k].zhi} {sc[k].general}
            </span>
            <span className="ke-sub">
              {sc[k].liuQin} 空{sc[k].xunKong}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

import type { LiurenPan } from "../../types/liuren";

interface Props {
  pan: LiurenPan;
}

export function TianDiPanGrid({ pan }: Props) {
  const palaces = pan.tianDiPan.palaces ?? [];
  return (
    <div className="chart-subpanel">
      <h3 className="chart-subpanel-title">天地盘</h3>
      <div className="liuren-tdp-grid" role="grid" aria-label="天地盘">
      {palaces.map((p) => (
        <div key={p.earth} className="liuren-tdp-cell" role="gridcell">
          <div className="tdp-earth">{p.earth}</div>
          <div className="tdp-sky">{p.sky}</div>
          <div className="tdp-gen">{p.general}</div>
        </div>
      ))}
      </div>
    </div>
  );
}

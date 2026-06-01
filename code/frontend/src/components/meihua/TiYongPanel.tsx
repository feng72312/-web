import type { MeihuaChart } from "../../types/meihua";

interface Props {
  chart: MeihuaChart;
  loading?: boolean;
  onApplyMoving: (position: number) => void;
}

export function TiYongPanel({ chart, loading, onApplyMoving }: Props) {
  return (
    <section className="panel ti-yong-panel">
      <h2>体用</h2>
      <div className="ti-yong-grid">
        <div className="ti-yong-card">
          <span className="label">体卦</span>
          <strong>
            {chart.tiGua.name} ({chart.tiGua.element})
          </strong>
        </div>
        <div className="ti-yong-card">
          <span className="label">用卦</span>
          <strong>
            {chart.yongGua.name} ({chart.yongGua.element})
          </strong>
        </div>
        <div className="ti-yong-card wide">
          <span className="label">关系</span>
          <strong>{chart.tiYongRelation}</strong>
        </div>
      </div>
      {chart.isStatic && (
        <p className="hint">
          静卦已按「下卦为体、上卦为用」排盘。若需改体用，请指定动爻位 (1-6):
        </p>
      )}
      {chart.isStatic && (
        <div className="action-row">
          {[1, 2, 3, 4, 5, 6].map((pos) => (
            <button
              key={pos}
              type="button"
              className="secondary"
              disabled={loading}
              onClick={() => onApplyMoving(pos)}
            >
              动{pos}爻
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

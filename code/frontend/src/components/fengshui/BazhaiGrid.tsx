import type { FengshuiPalaceCell } from "../../types/fengshui";

const GRID_ORDER = ["巽", "离", "坤", "震", "中", "兑", "艮", "坎", "乾"];

interface BazhaiGridProps {
  palaces: FengshuiPalaceCell[];
}

export function BazhaiGrid({ palaces }: BazhaiGridProps) {
  const byName = Object.fromEntries(palaces.map((p) => [p.name, p]));

  return (
    <div className="qimen-grid fengshui-grid" role="grid" aria-label="八宅方位盘">
      {GRID_ORDER.map((name) => {
        if (name === "中") {
          return (
            <div key={name} className="qimen-cell qimen-cell-center fengshui-cell-center" role="gridcell">
              <span className="qimen-gong">中宫</span>
              <span className="fengshui-cell-hint">后天八卦方位</span>
            </div>
          );
        }
        const cell = byName[name];
        const tone = cell?.auspicious ? "ji" : cell ? "xiong" : "empty";
        return (
          <div
            key={name}
            className={`qimen-cell fengshui-cell fengshui-cell-${tone}`}
            role="gridcell"
          >
            <div className="qimen-cell-head">
              <span className="qimen-gong">{name}</span>
              {cell?.direction && <span className="fengshui-direction">{cell.direction}</span>}
            </div>
            {cell?.labels?.length ? (
              <div className="fengshui-labels">
                {cell.labels.map((label) => (
                  <span key={label} className="fengshui-label-tag">
                    {label}
                  </span>
                ))}
              </div>
            ) : (
              <div className="fengshui-labels muted">-</div>
            )}
          </div>
        );
      })}
    </div>
  );
}

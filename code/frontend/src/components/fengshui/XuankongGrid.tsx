import type { FengshuiStarCell } from "../../types/fengshui";

const GRID_ORDER = ["巽", "离", "坤", "震", "中", "兑", "艮", "坎", "乾"];

interface XuankongGridProps {
  cells: FengshuiStarCell[];
  title?: string;
}

export function XuankongGrid({ cells, title }: XuankongGridProps) {
  const byPalace = Object.fromEntries(cells.map((cell) => [cell.palace, cell]));

  return (
    <div className="xuankong-grid-wrap">
      {title && <h4 className="xuankong-grid-title">{title}</h4>}
      <div className="qimen-grid fengshui-grid" role="grid" aria-label={title ?? "玄空九宫"}>
        {GRID_ORDER.map((name) => {
          if (name === "中") {
            const cell = byPalace[name];
            return (
              <div key={name} className="qimen-cell qimen-cell-center fengshui-cell-center" role="gridcell">
                <span className="qimen-gong">{name}</span>
                <span className="xuankong-star-label">{cell?.label ?? cell?.star ?? "-"}</span>
              </div>
            );
          }
          const cell = byPalace[name];
          return (
            <div key={name} className="qimen-cell fengshui-cell fengshui-cell-ji" role="gridcell">
              <div className="qimen-cell-head">
                <span className="qimen-gong">{name}</span>
              </div>
              <div className="xuankong-star-label">{cell?.label ?? cell?.star ?? "-"}</div>
              {cell?.starName && <div className="xuankong-star-name">{cell.starName}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

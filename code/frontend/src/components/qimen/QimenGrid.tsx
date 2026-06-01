import type { PalaceCell } from "../../types/qimen";

const GRID_ORDER: string[] = [
  "巽",
  "离",
  "坤",
  "震",
  "中",
  "兑",
  "艮",
  "坎",
  "乾",
];

interface QimenGridProps {
  palaces: PalaceCell[];
}

export function QimenGrid({ palaces }: QimenGridProps) {
  const byName = Object.fromEntries(palaces.map((p) => [p.name, p]));

  return (
    <div className="qimen-grid" role="grid" aria-label="奇门九宫盘">
      {GRID_ORDER.map((name) => {
        const cell = byName[name];
        const isCenter = name === "中";
        return (
          <div
            key={name}
            className={isCenter ? "qimen-cell qimen-cell-center" : "qimen-cell"}
            role="gridcell"
          >
            <div className="qimen-cell-head">
              <span className="qimen-gong">{name}</span>
              {cell?.god && <span className="qimen-god">{cell.god}</span>}
            </div>
            {cell?.star && <div className="qimen-star">{cell.star}</div>}
            {cell?.door && <div className="qimen-door">{cell.door}</div>}
            <div className="qimen-stems">
              <span>地 {cell?.earth || "-"}</span>
              <span>天 {cell?.heaven || "-"}</span>
              <span>人 {cell?.human || "-"}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

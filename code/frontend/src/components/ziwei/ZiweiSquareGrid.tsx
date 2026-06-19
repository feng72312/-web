import type {
  ZiweiChart,
  ZiweiDisplayLayer,
  ZiweiHighlightMode,
  ZiweiJudgementOverlay,
  ZiweiPalace,
  ZiweiRuntimeLayer,
} from "../../types/ziwei";
import { getPalacePosition } from "./ziweiLayout";
import { ZiweiCenterPanel } from "./ZiweiCenterPanel";
import { ZiweiPalaceCell } from "./ZiweiPalaceCell";

interface ZiweiSquareGridProps {
  chart: ZiweiChart;
  targetYear?: number;
  selectedBranch: string;
  highlightBranches: Set<string>;
  highlightMode: ZiweiHighlightMode;
  activeLayers: Set<ZiweiDisplayLayer>;
  runtimeLayer: ZiweiRuntimeLayer;
  compact?: boolean;
  judgementOverlay?: ZiweiJudgementOverlay;
  onSelectPalace: (branch: string) => void;
}

function buildGridCells(palaces: ZiweiPalace[]): Array<ZiweiPalace | null> {
  const cells: Array<ZiweiPalace | null> = Array.from({ length: 16 }, () => null);
  for (const palace of palaces) {
    const pos = getPalacePosition(palace);
    if (!pos) {
      continue;
    }
    const index = (pos.row - 1) * 4 + (pos.col - 1);
    cells[index] = palace;
  }
  return cells;
}

export function ZiweiSquareGrid({
  chart,
  targetYear,
  selectedBranch,
  highlightBranches,
  highlightMode,
  activeLayers,
  runtimeLayer,
  compact = false,
  judgementOverlay,
  onSelectPalace,
}: ZiweiSquareGridProps) {
  const cells = buildGridCells(chart.palaces);
  return (
    <div className="ziwei-square-grid">
      {cells.map((palace, index) => {
        const row = Math.floor(index / 4) + 1;
        const col = (index % 4) + 1;
        const isCenter = row >= 2 && row <= 3 && col >= 2 && col <= 3;
        if (isCenter) {
          if (row === 2 && col === 2) {
            return (
              <div key="center" className="ziwei-square-center" style={{ gridRow: "2 / span 2", gridColumn: "2 / span 2" }}>
                <ZiweiCenterPanel chart={chart} targetYear={targetYear} />
              </div>
            );
          }
          return null;
        }
        if (!palace) {
          return <div key={`empty-${index}`} className="ziwei-square-empty" />;
        }
        return (
          <div
            key={palace.earthlyBranch}
            className="ziwei-square-slot"
            style={{ gridRow: row, gridColumn: col }}
          >
            <ZiweiPalaceCell
              palace={palace}
              chart={chart}
              selectedBranch={selectedBranch}
              highlightBranches={highlightBranches}
              highlightMode={highlightMode}
              activeLayers={activeLayers}
              runtimeLayer={runtimeLayer}
              compact={compact}
              judgementOverlay={judgementOverlay}
              onSelect={onSelectPalace}
            />
          </div>
        );
      })}
    </div>
  );
}

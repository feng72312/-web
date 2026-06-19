import { useMemo, useRef, useState } from "react";
import type {
  ZiweiChart,
  ZiweiDisplayLayer,
  ZiweiHighlightMode,
  ZiweiJudgementOverlay,
  ZiweiRuntimeLayer,
} from "../../types/ziwei";
import { findPalaceByBranch, findSoulPalace } from "./ziweiLayout";
import { getPalaceHighlightSet } from "./ziweiDisplay";
import { ZiweiExportBar } from "./ZiweiExportBar";
import { ZiweiLayerToolbar } from "./ZiweiLayerToolbar";
import { ZiweiPalaceDetailPanel } from "./ZiweiPalaceDetailPanel";
import { ZiweiSquareGrid } from "./ZiweiSquareGrid";
import { ZiweiTimeNavigator } from "./ZiweiTimeNavigator";

const DEFAULT_LAYERS: ZiweiDisplayLayer[] = ["native", "mutagen", "decadal", "yearly"];

interface ZiweiProChartBoardProps {
  chart: ZiweiChart;
  targetYear?: number;
  onTargetYearChange?: (year: number) => void;
  judgementOverlay?: ZiweiJudgementOverlay;
}

export function ZiweiProChartBoard({
  chart,
  targetYear,
  onTargetYearChange,
  judgementOverlay,
}: ZiweiProChartBoardProps) {
  const boardRef = useRef<HTMLDivElement | null>(null);
  const soulPalace = findSoulPalace(chart.palaces);
  const [selectedBranch, setSelectedBranch] = useState(soulPalace?.earthlyBranch ?? "");
  const [activeLayers, setActiveLayers] = useState<Set<ZiweiDisplayLayer>>(
    () => new Set(DEFAULT_LAYERS),
  );
  const [highlightMode, setHighlightMode] = useState<ZiweiHighlightMode>("none");
  const [runtimeLayer, setRuntimeLayer] = useState<ZiweiRuntimeLayer>("yearly");
  const [selectedDecadalIndex, setSelectedDecadalIndex] = useState<number | null>(null);

  const effectiveTargetYear = targetYear ?? chart.limits.yearly?.targetYear ?? new Date().getFullYear();
  const selectedPalace = useMemo(
    () => findPalaceByBranch(chart.palaces, selectedBranch) ?? soulPalace ?? chart.palaces[0],
    [chart.palaces, selectedBranch, soulPalace],
  );
  const highlightBranches = useMemo(
    () =>
      getPalaceHighlightSet(
        chart,
        selectedBranch,
        activeLayers.has("triad") || activeLayers.has("all"),
      ),
    [activeLayers, chart, selectedBranch],
  );

  const handleToggleLayer = (layer: ZiweiDisplayLayer) => {
    if (layer === "all") {
      setActiveLayers(
        new Set(["native", "mutagen", "malefic", "triad", "decadal", "yearly", "all"]),
      );
      return;
    }
    setActiveLayers((prev) => {
      const next = new Set(prev);
      if (next.has(layer)) {
        next.delete(layer);
        next.delete("all");
      } else {
        next.add(layer);
      }
      if (!next.size) {
        next.add("native");
      }
      return next;
    });
  };

  const handleSelectDecadal = (index: number) => {
    setSelectedDecadalIndex(index);
    setRuntimeLayer("decadal");
    const row = chart.limits.decadal.find((item) => item.index === index);
    if (!row) {
      return;
    }
    const palace = chart.palaces.find(
      (item) => item.name === row.palace || item.stemBranch === row.stemBranch,
    );
    if (palace) {
      setSelectedBranch(palace.earthlyBranch);
    }
  };

  return (
    <div className="ziwei-pro-board">
      <ZiweiExportBar boardRef={boardRef} />
      <ZiweiLayerToolbar
        activeLayers={activeLayers}
        highlightMode={highlightMode}
        onToggleLayer={handleToggleLayer}
        onHighlightModeChange={setHighlightMode}
      />
      <div className="ziwei-pro-layout" ref={boardRef}>
        <div className="ziwei-pro-chart-area">
          <ZiweiSquareGrid
            chart={chart}
            targetYear={effectiveTargetYear}
            selectedBranch={selectedBranch}
            highlightBranches={highlightBranches}
            highlightMode={highlightMode}
            activeLayers={activeLayers}
            runtimeLayer={runtimeLayer}
            judgementOverlay={judgementOverlay}
            onSelectPalace={setSelectedBranch}
          />
        </div>
        {selectedPalace ? (
          <ZiweiPalaceDetailPanel
            chart={chart}
            palace={selectedPalace}
            runtimeLayer={runtimeLayer}
          />
        ) : null}
      </div>
      <ZiweiTimeNavigator
        chart={chart}
        targetYear={effectiveTargetYear}
        runtimeLayer={runtimeLayer}
        selectedDecadalIndex={selectedDecadalIndex}
        onRuntimeLayerChange={setRuntimeLayer}
        onTargetYearChange={onTargetYearChange}
        onSelectDecadal={handleSelectDecadal}
      />
    </div>
  );
}

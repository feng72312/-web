import { useState } from "react";
import type { ZiweiChart, ZiweiDisplayLayer } from "../../types/ziwei";
import { ZiweiSquareGrid } from "./ZiweiSquareGrid";

const SIMPLE_LAYERS = new Set<ZiweiDisplayLayer>(["native", "mutagen", "decadal"]);

interface ZiweiSimpleChartBoardProps {
  chart: ZiweiChart;
}

export function ZiweiSimpleChartBoard({ chart }: ZiweiSimpleChartBoardProps) {
  const soulBranch = chart.meta.soulPalaceBranch;
  const [selectedBranch, setSelectedBranch] = useState(soulBranch);
  const selectedPalace = chart.palaces.find((item) => item.earthlyBranch === selectedBranch);

  return (
    <div className="ziwei-simple-board">
      <ZiweiSquareGrid
        chart={chart}
        selectedBranch={selectedBranch}
        highlightBranches={new Set()}
        highlightMode="none"
        activeLayers={SIMPLE_LAYERS}
        runtimeLayer="native"
        compact
        onSelectPalace={setSelectedBranch}
      />
      {selectedPalace ? (
        <div className="ziwei-simple-detail">
          <h4>
            {selectedPalace.name} {selectedPalace.stemBranch}
          </h4>
          <p>
            主星:{" "}
            {selectedPalace.majorStars.length
              ? selectedPalace.majorStars.map((star) => star.name).join(" ")
              : "无主星"}
          </p>
          {selectedPalace.decadalRange ? <p>大限 {selectedPalace.decadalRange}</p> : null}
        </div>
      ) : null}
    </div>
  );
}

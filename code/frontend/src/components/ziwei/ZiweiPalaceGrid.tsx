import { Suspense, lazy } from "react";
import type { ZiweiChart, ZiweiDisplayMode, ZiweiJudgementReport } from "../../types/ziwei";
import { buildJudgementOverlay } from "./ziweiJudgementDisplay";
import { ZiweiSimpleChartBoard } from "./ZiweiSimpleChartBoard";
import { ZiweiPatternTags } from "./ZiweiPatternTags";

const ZiweiProChartBoard = lazy(() =>
  import("./ZiweiProChartBoard").then((module) => ({ default: module.ZiweiProChartBoard })),
);

interface Props {
  chart: ZiweiChart;
  mode: ZiweiDisplayMode;
  targetYear?: number;
  onTargetYearChange?: (year: number) => void;
  judgement?: ZiweiJudgementReport | null;
}

export function ZiweiPalaceGrid({ chart, mode, targetYear, onTargetYearChange, judgement }: Props) {
  const overlay = buildJudgementOverlay(judgement);
  const patternTags = overlay?.patternLabels ?? [];

  if (mode === "simple") {
    return (
      <div className="ziwei-chart-with-overlay">
        <ZiweiPatternTags labels={patternTags} />
        <ZiweiSimpleChartBoard chart={chart} judgementOverlay={overlay} />
      </div>
    );
  }

  return (
    <div className="ziwei-chart-with-overlay">
      <ZiweiPatternTags labels={patternTags} />
      <Suspense fallback={<div className="ziwei-pro-loading">专业盘加载中...</div>}>
        <ZiweiProChartBoard
          chart={chart}
          targetYear={targetYear}
          onTargetYearChange={onTargetYearChange}
          judgementOverlay={overlay}
        />
      </Suspense>
    </div>
  );
}

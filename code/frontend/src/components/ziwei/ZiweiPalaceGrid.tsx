import { Suspense, lazy } from "react";
import type { ZiweiChart, ZiweiDisplayMode } from "../../types/ziwei";
import { ZiweiSimpleChartBoard } from "./ZiweiSimpleChartBoard";

const ZiweiProChartBoard = lazy(() =>
  import("./ZiweiProChartBoard").then((module) => ({ default: module.ZiweiProChartBoard })),
);

interface Props {
  chart: ZiweiChart;
  mode: ZiweiDisplayMode;
  targetYear?: number;
  onTargetYearChange?: (year: number) => void;
}

export function ZiweiPalaceGrid({ chart, mode, targetYear, onTargetYearChange }: Props) {
  if (mode === "simple") {
    return <ZiweiSimpleChartBoard chart={chart} />;
  }

  return (
    <Suspense fallback={<div className="ziwei-pro-loading">专业盘加载中...</div>}>
      <ZiweiProChartBoard
        chart={chart}
        targetYear={targetYear}
        onTargetYearChange={onTargetYearChange}
      />
    </Suspense>
  );
}

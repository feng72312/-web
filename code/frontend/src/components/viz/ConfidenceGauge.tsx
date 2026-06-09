import { lazy, Suspense } from "react";
import type { ConfidenceBand } from "../../types/consensus";

const ReactECharts = lazy(() => import("echarts-for-react"));

const BAND_SCORE: Record<ConfidenceBand, number> = {
  strong: 85,
  medium: 55,
  weak: 25,
};

interface ConfidenceGaugeProps {
  band?: ConfidenceBand;
  score?: number;
  height?: number;
}

export function ConfidenceGauge({ band = "medium", score, height = 160 }: ConfidenceGaugeProps) {
  const value = score != null ? Math.round(score * 100) : BAND_SCORE[band];
  const option = {
    series: [
      {
        type: "gauge",
        min: 0,
        max: 100,
        progress: { show: true, width: 12 },
        axisLine: { lineStyle: { width: 12 } },
        detail: { formatter: "{value}%", fontSize: 18 },
        data: [{ value }],
      },
    ],
  };
  return (
    <Suspense fallback={<div className="viz-skeleton">仪表盘加载中...</div>}>
      <ReactECharts option={option} style={{ height }} opts={{ renderer: "svg" }} />
    </Suspense>
  );
}

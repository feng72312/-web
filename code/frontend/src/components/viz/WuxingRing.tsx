import { lazy, Suspense } from "react";

const ReactECharts = lazy(() => import("echarts-for-react"));

interface WuxingRingProps {
  scores: { wood: number; fire: number; earth: number; metal: number; water: number };
  height?: number;
}

export function WuxingRing({ scores, height = 220 }: WuxingRingProps) {
  const option = {
    tooltip: { trigger: "item" },
    series: [
      {
        type: "pie",
        radius: ["48%", "72%"],
        label: { show: true, formatter: "{b}: {c}" },
        data: [
          { name: "木", value: scores.wood, itemStyle: { color: "var(--wood)" } },
          { name: "火", value: scores.fire, itemStyle: { color: "var(--fire)" } },
          { name: "土", value: scores.earth, itemStyle: { color: "var(--earth)" } },
          { name: "金", value: scores.metal, itemStyle: { color: "var(--metal)" } },
          { name: "水", value: scores.water, itemStyle: { color: "var(--water)" } },
        ],
      },
    ],
  };

  return (
    <Suspense fallback={<div className="viz-skeleton">图表加载中...</div>}>
      <ReactECharts option={option} style={{ height }} opts={{ renderer: "svg" }} />
    </Suspense>
  );
}

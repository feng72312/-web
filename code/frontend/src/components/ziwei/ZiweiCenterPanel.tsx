import type { ZiweiChart } from "../../types/ziwei";

interface ZiweiCenterPanelProps {
  chart: ZiweiChart;
  targetYear?: number;
}

export function ZiweiCenterPanel({ chart, targetYear }: ZiweiCenterPanelProps) {
  const { meta, fourPillars, input } = chart;
  return (
    <div className="ziwei-center-panel">
      <p className="ziwei-center-name">{input.name || "匿名"}</p>
      <p className="ziwei-center-bureau">{meta.bureau}</p>
      <p className="ziwei-center-meta">
        {meta.gender} / {meta.zodiac} / {meta.sign}
      </p>
      <div className="ziwei-center-pillars">
        <span>{fourPillars.year}</span>
        <span>{fourPillars.month}</span>
        <span>{fourPillars.day}</span>
        <span>{fourPillars.hour}</span>
      </div>
      <p className="ziwei-center-line">{chart.solarLabel}</p>
      <p className="ziwei-center-line">{chart.lunarLabel}</p>
      <p className="ziwei-center-line">真太阳 {chart.trueSolarTime}</p>
      <p className="ziwei-center-line">
        命主 {meta.soul} / 身主 {meta.body}
      </p>
      <p className="ziwei-center-line">
        命宫 {meta.soulPalaceBranch} / 身宫 {meta.bodyPalaceBranch}
      </p>
      {meta.timeRange ? <p className="ziwei-center-line">{meta.timeRange}</p> : null}
      {targetYear ? <p className="ziwei-center-line">流年参照 {targetYear}</p> : null}
      <div className="ziwei-center-legend">
        <span className="ziwei-legend-item ziwei-mutagen-lu">禄</span>
        <span className="ziwei-legend-item ziwei-mutagen-quan">权</span>
        <span className="ziwei-legend-item ziwei-mutagen-ke">科</span>
        <span className="ziwei-legend-item ziwei-mutagen-ji">忌</span>
        <span className="ziwei-legend-item soul">命</span>
        <span className="ziwei-legend-item body">身</span>
        <span className="ziwei-legend-item yearly">流年</span>
        <span className="ziwei-legend-item malefic">煞</span>
      </div>
    </div>
  );
}

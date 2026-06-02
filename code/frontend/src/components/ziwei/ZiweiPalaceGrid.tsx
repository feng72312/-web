import type { ZiweiChart } from "../../types/ziwei";

interface Props {
  chart: ZiweiChart;
}

function PalaceCard({ palace }: { palace: ZiweiChart["palaces"][0] }) {
  const major = palace.majorStars.map((s) => s.name).join(" ");
  const mutagen = palace.majorStars
    .filter((s) => s.mutagen)
    .map((s) => `${s.name}${s.mutagen}`)
    .join(" ");
  return (
    <div className={`ziwei-palace ${palace.isBody ? "body-palace" : ""}`}>
      <div className="ziwei-palace-head">
        <strong>{palace.name}</strong>
        <span>{palace.stemBranch}</span>
      </div>
      <div className="ziwei-palace-major">{major || "无主星"}</div>
      {mutagen && <div className="ziwei-palace-mutagen">{mutagen}</div>}
      {palace.decadalRange && (
        <div className="ziwei-palace-limit">限 {palace.decadalRange}</div>
      )}
    </div>
  );
}

export function ZiweiPalaceGrid({ chart }: Props) {
  const { meta, fourPillars } = chart;
  return (
    <div className="ziwei-chart-wrap">
      <div className="ziwei-center panel-inset">
        <p className="ziwei-bureau">{meta.bureau}</p>
        <p>
          {fourPillars.year} {fourPillars.month} {fourPillars.day} {fourPillars.hour}
        </p>
        <p>
          命主 {meta.soul} / 身主 {meta.body} / {meta.gender} / {meta.zodiac}
        </p>
        <p className="hint">真太阳 {chart.trueSolarTime}</p>
      </div>
      <div className="ziwei-palace-list">
        {chart.palaces.map((palace) => (
          <PalaceCard key={palace.index} palace={palace} />
        ))}
      </div>
    </div>
  );
}

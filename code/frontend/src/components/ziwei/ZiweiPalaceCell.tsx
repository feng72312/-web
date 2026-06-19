import type {
  ZiweiChart,
  ZiweiDisplayLayer,
  ZiweiHighlightMode,
  ZiweiJudgementOverlay,
  ZiweiPalace,
  ZiweiRuntimeLayer,
} from "../../types/ziwei";
import { MALEFIC_STAR_NAMES } from "./ziweiLayout";
import { formatAges, formatStar, getPalaceClassNames, mutagenClass } from "./ziweiDisplay";

interface ZiweiPalaceCellProps {
  palace: ZiweiPalace;
  chart: ZiweiChart;
  selectedBranch: string;
  highlightBranches: Set<string>;
  highlightMode: ZiweiHighlightMode;
  activeLayers: Set<ZiweiDisplayLayer>;
  runtimeLayer: ZiweiRuntimeLayer;
  compact?: boolean;
  judgementOverlay?: ZiweiJudgementOverlay;
  onSelect: (branch: string) => void;
}

export function ZiweiPalaceCell({
  palace,
  chart,
  selectedBranch,
  highlightBranches,
  highlightMode,
  activeLayers,
  runtimeLayer,
  compact = false,
  judgementOverlay,
  onSelect,
}: ZiweiPalaceCellProps) {
  const majorStars = palace.starGroups?.major ?? palace.majorStars;
  const minorStars = palace.starGroups?.minor ?? palace.minorStars;
  const adjStars = palace.starGroups?.adj ?? palace.adjStars;
  const showMutagen = activeLayers.has("mutagen") || activeLayers.has("all");
  const showMalefic = activeLayers.has("malefic") || activeLayers.has("all");
  const showDecadal = activeLayers.has("decadal") || activeLayers.has("all");
  const showYearly = activeLayers.has("yearly") || activeLayers.has("all");

  return (
    <button
      type="button"
      className={getPalaceClassNames({
        palace,
        selectedBranch,
        highlightBranches,
        highlightMode,
        activeLayers,
        runtimeLayer,
        chart,
        judgementOverlay,
      })}
      onClick={() => onSelect(palace.earthlyBranch)}
    >
      <div className="ziwei-palace-cell-head">
        <strong>{palace.name}</strong>
        <span>{palace.stemBranch}</span>
      </div>
      <div className="ziwei-palace-cell-badges">
        {palace.isSoul ? <span className="ziwei-badge soul">命</span> : null}
        {palace.isBody ? <span className="ziwei-badge body">身</span> : null}
        {palace.borrowedFromOpposite ? <span className="ziwei-badge borrowed">借</span> : null}
        {judgementOverlay?.limitPalaces.has(palace.name) ? (
          <span className="ziwei-badge limit-trigger">引动</span>
        ) : null}
        {showYearly &&
        chart.limits.yearly?.palaceNames &&
        Array.isArray(chart.limits.yearly.palaceNames) &&
        (chart.limits.yearly.palaceNames as string[]).includes(palace.name) ? (
          <span className="ziwei-badge yearly">流年</span>
        ) : null}
      </div>
      <div className="ziwei-palace-cell-major">
        {majorStars.length ? (
          majorStars.map((star) => (
            <span
              key={`${palace.earthlyBranch}-${star.name}`}
              className={showMutagen && star.mutagen ? mutagenClass(star.mutagen) : ""}
            >
              {formatStar(star)}
              {showMutagen && star.mutagen ? <em>{star.mutagen}</em> : null}
            </span>
          ))
        ) : (
          <span className="ziwei-empty-star">无主星</span>
        )}
      </div>
      {!compact && minorStars.length ? (
        <div className="ziwei-palace-cell-minor">
          {minorStars.map((star) => (
            <span
              key={`${palace.earthlyBranch}-m-${star.name}`}
              className={
                showMalefic && MALEFIC_STAR_NAMES.has(star.name) ? "ziwei-minor-star malefic" : ""
              }
            >
              {star.name}
            </span>
          ))}
        </div>
      ) : null}
      {!compact && adjStars.length ? (
        <div className="ziwei-palace-cell-adj">
          {adjStars.map((star) => (
            <span key={`${palace.earthlyBranch}-a-${star.name}`}>{star.name}</span>
          ))}
        </div>
      ) : null}
      {showDecadal && palace.decadalRange ? (
        <div className="ziwei-palace-cell-limit">限 {palace.decadalRange}</div>
      ) : null}
      {!compact && palace.minorAges.length ? (
        <div className="ziwei-palace-cell-ages">{formatAges(palace.minorAges)}</div>
      ) : null}
      {showMutagen && judgementOverlay?.showFlyingMutagen && palace.flyingMutagens?.outbound?.length ? (
        <div className="ziwei-flying-mutagens">
          {palace.flyingMutagens.outbound.slice(0, 3).map((row) => (
            <span key={`${row.star}-${row.mutagen}-${row.targetPalace}`} className="ziwei-fly-line">
              {row.mutagen}至{row.targetPalace}
            </span>
          ))}
        </div>
      ) : null}
    </button>
  );
}

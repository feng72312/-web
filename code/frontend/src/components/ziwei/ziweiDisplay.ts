import type {
  ZiweiActiveLimitLayer,
  ZiweiChart,
  ZiweiDisplayLayer,
  ZiweiHighlightMode,
  ZiweiJudgementOverlay,
  ZiweiPalace,
  ZiweiRuntimeLayer,
  ZiweiStar,
} from "../../types/ziwei";
import {
  MALEFIC_STAR_NAMES,
  MUTAGEN_CLASS_MAP,
  findPalaceByBranch,
  getOppositeBranch,
  getTriadBranches,
} from "./ziweiLayout";

export function formatStar(star: ZiweiStar): string {
  if (star.brightness) {
    return `${star.name}${star.brightness}`;
  }
  return star.name;
}

export function formatAges(ages: number[]): string {
  if (!ages.length) {
    return "";
  }
  return ages.join(" ");
}

export function mutagenClass(mutagen: string | null | undefined): string {
  if (!mutagen) {
    return "";
  }
  return MUTAGEN_CLASS_MAP[mutagen] ?? "ziwei-mutagen-other";
}

export function collectAllStars(palace: ZiweiPalace): ZiweiStar[] {
  if (palace.starGroups) {
    return [
      ...palace.starGroups.major,
      ...palace.starGroups.minor,
      ...palace.starGroups.adj,
    ];
  }
  return [...palace.majorStars, ...palace.minorStars, ...palace.adjStars];
}

export function palaceHasMalefic(palace: ZiweiPalace): boolean {
  if (typeof palace.hasMalefic === "boolean") {
    return palace.hasMalefic;
  }
  return collectAllStars(palace).some((star) => MALEFIC_STAR_NAMES.has(star.name));
}

export function getRelatedBranches(palace: ZiweiPalace, includeTriad: boolean): string[] {
  const branches = new Set<string>([palace.earthlyBranch]);
  const opposite = palace.oppositeBranch || getOppositeBranch(palace.earthlyBranch);
  if (opposite) {
    branches.add(opposite);
  }
  if (includeTriad) {
    const triad = palace.triadBranches?.length
      ? palace.triadBranches
      : getTriadBranches(palace.earthlyBranch);
    for (const branch of triad) {
      branches.add(branch);
    }
  }
  return Array.from(branches);
}

export function getPalaceHighlightSet(
  chart: ZiweiChart,
  selectedBranch: string,
  includeTriad: boolean,
): Set<string> {
  const palace = findPalaceByBranch(chart.palaces, selectedBranch);
  if (!palace) {
    return new Set([selectedBranch]);
  }
  return new Set(getRelatedBranches(palace, includeTriad));
}

export function isRuntimePalace(
  palace: ZiweiPalace,
  layer: ZiweiActiveLimitLayer | undefined,
): boolean {
  if (!layer?.available) {
    return false;
  }
  if (layer.palaceNames?.includes(palace.name)) {
    return true;
  }
  return false;
}

export function getActiveLayer(
  chart: ZiweiChart,
  runtimeLayer: ZiweiRuntimeLayer,
): ZiweiActiveLimitLayer | undefined {
  return chart.limits.active?.[runtimeLayer];
}

export function getPalaceClassNames(input: {
  palace: ZiweiPalace;
  selectedBranch: string;
  highlightBranches: Set<string>;
  highlightMode: ZiweiHighlightMode;
  activeLayers: Set<ZiweiDisplayLayer>;
  runtimeLayer: ZiweiRuntimeLayer;
  chart: ZiweiChart;
  judgementOverlay?: ZiweiJudgementOverlay;
}): string {
  const {
    palace,
    selectedBranch,
    highlightBranches,
    highlightMode,
    activeLayers,
    runtimeLayer,
    chart,
    judgementOverlay,
  } = input;
  const classes = ["ziwei-palace-cell"];
  const branch = palace.earthlyBranch;
  if (branch === selectedBranch) {
    classes.push("is-selected");
  }
  if (highlightBranches.has(branch) && branch !== selectedBranch) {
    if (branch === getOppositeBranch(selectedBranch)) {
      classes.push("is-opposite");
    } else {
      classes.push("is-triad");
    }
  }
  if (palace.isSoul) {
    classes.push("is-soul");
  }
  if (palace.isBody) {
    classes.push("is-body");
  }
  if (activeLayers.has("malefic") && palaceHasMalefic(palace)) {
    classes.push("has-malefic");
  }
  if (highlightMode === "mutagen" && (palace.mutagenStars?.length ?? 0) > 0) {
    classes.push("is-mutagen-highlight");
  }
  if (highlightMode === "malefic" && palaceHasMalefic(palace)) {
    classes.push("is-malefic-highlight");
  }
  const runtime = getActiveLayer(chart, runtimeLayer);
  if (
    (activeLayers.has("yearly") || activeLayers.has("decadal") || activeLayers.has("all")) &&
    isRuntimePalace(palace, runtime)
  ) {
    classes.push("is-runtime");
  }
  if (judgementOverlay?.limitPalaces.has(palace.name)) {
    classes.push("is-limit-trigger");
  }
  if (palace.borrowedFromOpposite) {
    classes.push("is-borrowed-opposite");
  }
  if (palace.riskFlags?.includes("mutagen_ji")) {
    classes.push("has-mutagen-ji");
  }
  return classes.join(" ");
}

export function majorStarSummary(palace: ZiweiPalace): string {
  const stars = palace.starGroups?.major ?? palace.majorStars;
  if (!stars.length) {
    return "无主星";
  }
  return stars.map(formatStar).join(" ");
}

import type { ZiweiJudgementReport, ZiweiJudgementOverlay } from "../../types/ziwei";

interface LimitEvent {
  natalHits?: string[];
  palaces?: string[];
}

export function buildJudgementOverlay(
  judgement: ZiweiJudgementReport | null | undefined,
): ZiweiJudgementOverlay | undefined {
  if (!judgement) {
    return undefined;
  }

  const limitPalaces = new Set<string>();
  const limitJudge = judgement.judges?.find((row) => row.role === "limit");
  const events = (limitJudge?.flags?.eventChain as LimitEvent[] | undefined) ?? [];
  for (const event of events) {
    for (const name of event.natalHits ?? []) {
      if (name) {
        limitPalaces.add(name);
      }
    }
    for (const name of event.palaces ?? []) {
      if (name) {
        limitPalaces.add(name);
      }
    }
  }

  const patternLabels: string[] = [];
  const patternJudge = judgement.judges?.find((row) => row.role === "pattern");
  const patternSummary = patternJudge?.summary ?? "";
  if (patternSummary.includes("命中格局:")) {
    const raw = patternSummary.split("命中格局:")[1]?.split(";")[0]?.trim() ?? "";
    for (const label of raw.split("、")) {
      const trimmed = label.trim();
      if (trimmed) {
        patternLabels.push(trimmed);
      }
    }
  }

  const school = judgement.rulesMeta?.chartSchool ?? judgement.enrichedChart?.meta?.chartSchool;
  return {
    limitPalaces,
    patternLabels,
    showFlyingMutagen: school === "feixing" || Boolean(judgement.judges?.some((row) => row.role === "mutagen")),
  };
}

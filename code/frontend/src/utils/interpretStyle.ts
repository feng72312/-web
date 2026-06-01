export type InterpretStyle = "professional" | "plain";

export interface DualInterpretSummaries {
  summary?: string;
  summaryProfessional?: string;
  summaryPlain?: string;
}

export function mergeInterpretSummary<T extends DualInterpretSummaries>(
  prev: T | null | undefined,
  summary: string,
  style: InterpretStyle,
): T {
  const base = { ...(prev ?? {}) } as T;
  base.summary = summary;
  if (style === "professional") {
    base.summaryProfessional = summary;
  } else {
    base.summaryPlain = summary;
  }
  return base;
}

export function hasAnyInterpretSummary(data: DualInterpretSummaries | null | undefined): boolean {
  if (!data) {
    return false;
  }
  return Boolean(data.summaryProfessional || data.summaryPlain || data.summary);
}

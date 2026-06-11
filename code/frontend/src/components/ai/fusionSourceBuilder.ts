import {
  FUSION_MAX_CHART_JSON_CHARS,
  FUSION_SOURCE_VERSION,
  type FusionChartSource,
  type FusionSourceModuleId,
} from "./fusionTypes";

interface BuildFusionSourceInput {
  moduleId: FusionSourceModuleId;
  moduleLabel: string;
  title: string;
  subtitle?: string;
  question?: string;
  chartSnapshot: Record<string, unknown>;
  summaryPlain?: string | null;
  summaryProfessional?: string | null;
  agentId?: string | null;
  sourceId?: string;
  createdAt?: string;
}

function stablePart(value: unknown): string {
  if (value == null) {
    return "";
  }
  return String(value).trim();
}

function buildSourceId(moduleId: string, chartSnapshot: Record<string, unknown>): string {
  const input =
    (chartSnapshot.input as Record<string, unknown> | undefined) ??
    (chartSnapshot.meta as Record<string, unknown> | undefined) ??
    chartSnapshot;
  const parts = [
    moduleId,
    stablePart(input.name),
    stablePart(input.year),
    stablePart(input.month),
    stablePart(input.day),
    stablePart(input.hour),
    stablePart(input.minute),
    stablePart(input.gender),
    stablePart(input.calendarType),
    stablePart(input.question),
    stablePart(chartSnapshot.dayMaster),
    stablePart((chartSnapshot.meta as Record<string, unknown> | undefined)?.bureau),
  ].filter(Boolean);
  return parts.join("|");
}

function trimChartSnapshot(snapshot: Record<string, unknown>): Record<string, unknown> {
  let text = JSON.stringify(snapshot);
  if (text.length <= FUSION_MAX_CHART_JSON_CHARS) {
    return snapshot;
  }
  const input = snapshot.input as Record<string, unknown> | undefined;
  const compact: Record<string, unknown> = {
    moduleHint: snapshot.moduleHint,
    dayMaster: snapshot.dayMaster,
    meta: snapshot.meta,
    input: input
      ? {
          name: input.name,
          year: input.year,
          month: input.month,
          day: input.day,
          hour: input.hour,
          minute: input.minute,
          gender: input.gender,
          calendarType: input.calendarType,
          question: input.question,
        }
      : undefined,
    fourPillars: snapshot.fourPillars,
    palaces: Array.isArray(snapshot.palaces)
      ? snapshot.palaces.slice(0, 12).map((palace) => {
          const row = palace as Record<string, unknown>;
          return {
            name: row.name,
            stemBranch: row.stemBranch,
            earthlyBranch: row.earthlyBranch,
            majorStars: row.majorStars,
            minorStars: row.minorStars,
            adjStars: row.adjStars,
            mutagenStars: row.mutagenStars,
            decadalRange: row.decadalRange,
            isSoul: row.isSoul,
            isBody: row.isBody,
          };
        })
      : undefined,
    limits: snapshot.limits,
    sections: Array.isArray(snapshot.sections) ? snapshot.sections.slice(0, 8) : undefined,
  };
  text = JSON.stringify(compact);
  if (text.length <= FUSION_MAX_CHART_JSON_CHARS) {
    return compact;
  }
  return {
    input: compact.input,
    dayMaster: compact.dayMaster,
    meta: compact.meta,
    truncated: true,
  };
}

export function buildFusionChartSource(input: BuildFusionSourceInput): FusionChartSource {
  const now = new Date().toISOString();
  const chartSnapshot = trimChartSnapshot(input.chartSnapshot);
  const sourceId = input.sourceId ?? buildSourceId(input.moduleId, chartSnapshot);
  return {
    sourceId,
    moduleId: input.moduleId,
    moduleLabel: input.moduleLabel,
    title: input.title,
    subtitle: input.subtitle?.trim() || undefined,
    question: input.question?.trim() || undefined,
    chartSnapshot,
    summaryPlain: input.summaryPlain?.trim() || undefined,
    summaryProfessional: input.summaryProfessional?.trim() || undefined,
    agentId: input.agentId?.trim() || undefined,
    createdAt: input.createdAt ?? now,
    updatedAt: now,
    sourceVersion: FUSION_SOURCE_VERSION,
  };
}

export function buildBaziFusionSource(input: {
  chart: Record<string, unknown>;
  question?: string;
  chartName?: string;
  subtitle?: string;
  summaryPlain?: string | null;
  summaryProfessional?: string | null;
  agentId?: string | null;
  sourceId?: string;
}): FusionChartSource {
  return buildFusionChartSource({
    moduleId: "01",
    moduleLabel: "八字",
    title: input.chartName || String(input.chart.dayMaster || "八字命盘"),
    subtitle: input.subtitle,
    question: input.question,
    chartSnapshot: {
      ...input.chart,
      moduleHint: "bazi",
    },
    summaryPlain: input.summaryPlain,
    summaryProfessional: input.summaryProfessional,
    agentId: input.agentId,
    sourceId: input.sourceId,
  });
}

export function buildZiweiFusionSource(input: {
  chart: Record<string, unknown>;
  question?: string;
  chartName?: string;
  subtitle?: string;
  summaryPlain?: string | null;
  summaryProfessional?: string | null;
  agentId?: string | null;
  sourceId?: string;
}): FusionChartSource {
  const meta = input.chart.meta as Record<string, unknown> | undefined;
  return buildFusionChartSource({
    moduleId: "11",
    moduleLabel: "紫微",
    title: input.chartName || String(meta?.bureau || "紫微命盘"),
    subtitle: input.subtitle,
    question: input.question,
    chartSnapshot: {
      ...input.chart,
      moduleHint: "ziwei",
    },
    summaryPlain: input.summaryPlain,
    summaryProfessional: input.summaryProfessional,
    agentId: input.agentId,
    sourceId: input.sourceId,
  });
}

export function buildFusionSessionTitle(sources: FusionChartSource[]): string {
  const labels = sources.map((item) => item.moduleLabel).join(" + ");
  const firstTitle = sources[0]?.title ?? "多盘融合";
  if (sources.length <= 2) {
    return `融合分析 · ${labels}`;
  }
  return `融合分析 · ${labels} · ${firstTitle}`;
}

import {
  FUSION_MAX_SOURCES,
  FUSION_SOURCE_VERSION,
  type FusionChartSource,
} from "./fusionTypes";

const STORAGE_KEY = "ziyun_fusion_chart_sources_v1";

function isValidSource(item: unknown): item is FusionChartSource {
  if (!item || typeof item !== "object") {
    return false;
  }
  const row = item as FusionChartSource;
  return (
    typeof row.sourceId === "string" &&
    typeof row.moduleId === "string" &&
    typeof row.moduleLabel === "string" &&
    typeof row.title === "string" &&
    typeof row.chartSnapshot === "object" &&
    row.chartSnapshot !== null &&
    typeof row.createdAt === "string" &&
    typeof row.updatedAt === "string"
  );
}

export function loadFusionSources(): FusionChartSource[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.filter(isValidSource);
  } catch {
    return [];
  }
}

function saveFusionSources(sources: FusionChartSource[]): FusionChartSource[] {
  const trimmed = sources.slice(0, FUSION_MAX_SOURCES);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
  return trimmed;
}

export function upsertFusionSource(source: FusionChartSource): FusionChartSource[] {
  const existing = loadFusionSources();
  const prior = existing.find((item) => item.sourceId === source.sourceId);
  const merged: FusionChartSource = {
    ...source,
    createdAt: prior?.createdAt ?? source.createdAt,
    sourceVersion: FUSION_SOURCE_VERSION,
    updatedAt: new Date().toISOString(),
  };
  const rest = existing.filter((item) => item.sourceId !== source.sourceId);
  const next = [merged, ...rest].slice(0, FUSION_MAX_SOURCES);
  return saveFusionSources(next);
}

export function removeFusionSource(sourceId: string): FusionChartSource[] {
  const next = loadFusionSources().filter((item) => item.sourceId !== sourceId);
  return saveFusionSources(next);
}

export function clearFusionSources(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export function getFusionSourceById(sourceId: string): FusionChartSource | null {
  return loadFusionSources().find((item) => item.sourceId === sourceId) ?? null;
}

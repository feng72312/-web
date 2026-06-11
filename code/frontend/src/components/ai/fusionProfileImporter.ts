import { fetchPaipan } from "../../services/api";
import {
  DEFAULT_ZIWEI_SETTINGS,
  formToPaipanRequest,
  listProfiles,
  profileToFormState,
  profileToZiweiSettings,
} from "../../services/profileStorage";
import { fetchZiweiChart } from "../../services/ziweiApi";
import type { PaipanRequest, SavedProfile } from "../../types/bazi";
import type { ZiweiChartRequest } from "../../types/ziwei";
import { buildBaziFusionSource, buildZiweiFusionSource } from "./fusionSourceBuilder";
import { loadFusionSources, upsertFusionSource } from "./fusionSourceStorage";
import type { FusionChartSource, FusionSourceModuleId } from "./fusionTypes";

const DEFAULT_BAZI_QUESTION = "请论此命主格局、用神喜忌与一生大势";
const DEFAULT_ZIWEI_QUESTION = "请论此命命宫格局、性情与当前大限流年";

export function profileFusionSourceId(
  profileId: string,
  moduleId: FusionSourceModuleId,
): string {
  return `profile|${profileId}|${moduleId}`;
}

function buildZiweiRequestFromProfile(
  profile: SavedProfile,
  question: string,
  targetYear: number,
): ZiweiChartRequest {
  const birth = formToPaipanRequest(profileToFormState(profile));
  const settings = profileToZiweiSettings(profile);
  return {
    name: birth.name,
    calendarType: birth.calendarType,
    year: birth.year,
    month: birth.month,
    day: birth.day,
    isLeapMonth: birth.isLeapMonth,
    hour: birth.hour,
    minute: birth.minute,
    gender: birth.gender,
    useTrueSolarTime: settings.useTrueSolarTime,
    longitude: settings.longitude,
    targetYear,
    detailLevel: "simple",
    question: question.trim(),
    rules: {
      leapMonthRule: settings.leapMonthRule,
      ziHourRule: settings.ziHourRule,
      mutagenTable: settings.mutagenTable ?? DEFAULT_ZIWEI_SETTINGS.mutagenTable,
      chartSchool: settings.chartSchool ?? DEFAULT_ZIWEI_SETTINGS.chartSchool,
    },
  };
}

export function hasProfileFusionSource(
  profileId: string,
  moduleId: FusionSourceModuleId,
): boolean {
  const sourceId = profileFusionSourceId(profileId, moduleId);
  return loadFusionSources().some((item) => item.sourceId === sourceId);
}

export async function loadBaziFusionSourceFromProfile(
  profile: SavedProfile,
  question = DEFAULT_BAZI_QUESTION,
): Promise<FusionChartSource> {
  const request: PaipanRequest = formToPaipanRequest(profileToFormState(profile));
  const paipan = await fetchPaipan(request);
  const source = buildBaziFusionSource({
    chart: paipan.chart as unknown as Record<string, unknown>,
    question,
    chartName: profile.name || paipan.chart.dayMaster || "八字命盘",
    subtitle: paipan.chart.dayMaster,
    sourceId: profileFusionSourceId(profile.id, "01"),
  });
  upsertFusionSource(source);
  return source;
}

export async function loadZiweiFusionSourceFromProfile(
  profile: SavedProfile,
  question = DEFAULT_ZIWEI_QUESTION,
  targetYear = new Date().getFullYear(),
): Promise<FusionChartSource> {
  const payload = await fetchZiweiChart(
    buildZiweiRequestFromProfile(profile, question, targetYear),
  );
  const chart = payload.chart;
  const source = buildZiweiFusionSource({
    chart: chart as unknown as Record<string, unknown>,
    question: chart.input.question ?? question,
    chartName: chart.meta.bureau,
    subtitle: chart.palaces[0]?.stemBranch ?? "",
    sourceId: profileFusionSourceId(profile.id, "11"),
  });
  upsertFusionSource(source);
  return source;
}

export async function hydrateAllBaziProfilesFromSaved(
  onProgress?: (loaded: number, total: number) => void,
): Promise<FusionChartSource[]> {
  const profiles = listProfiles();
  let loaded = 0;
  for (const profile of profiles) {
    if (hasProfileFusionSource(profile.id, "01")) {
      loaded += 1;
      onProgress?.(loaded, profiles.length);
      continue;
    }
    await loadBaziFusionSourceFromProfile(profile);
    loaded += 1;
    onProgress?.(loaded, profiles.length);
  }
  return loadFusionSources();
}

import type { CalendarType } from "./bazi";

export type XingmingSchool = "guolao_v1";
export type XingmingZiHourRule = "combined" | "split";
export type XingmingDayNightRule = "auto" | "day" | "night";

export interface XingmingRules {
  school: XingmingSchool;
  ziHourRule: XingmingZiHourRule;
  dayNightRule: XingmingDayNightRule;
}

export interface XingmingChartRequest {
  name: string;
  calendarType: CalendarType;
  year: number;
  month: number;
  day: number;
  isLeapMonth: boolean;
  hour: number;
  minute: number;
  second?: number;
  gender: number;
  useTrueSolarTime: boolean;
  longitude: number;
  latitude: number;
  targetYear?: number;
  question?: string;
  rules: XingmingRules;
}

export interface XingmingStarRef {
  id: string;
  label: string;
}

export interface XingmingPalace {
  index: number;
  name: string;
  branch: string;
  startLongitude: number;
  endLongitude: number;
  majorStars: XingmingStarRef[];
  minorStars: XingmingStarRef[];
  tags: string[];
}

export interface XingmingBody {
  id: string;
  label: string;
  longitude: number;
  mansion: string;
  mansionDegree: number;
  retrograde?: boolean | null;
  palace?: string;
}

export interface XingmingChart {
  input: XingmingChartRequest;
  trueSolarTime: string;
  fourPillars: Record<string, string>;
  meta: { engine: string; school: string; version: number; isDay: boolean };
  rulesMeta: Record<string, unknown>;
  bodies: XingmingBody[];
  palaces: XingmingPalace[];
  mingPalace: { name: string; branch: string; majorStars: XingmingStarRef[] };
  limits: {
    targetYear: number;
    taiSui: { branch: string; palace: string; palaceIndex: number };
    xian: { note: string; palace: string | null };
  };
}

import type { KnowledgeEvidenceItem } from "./bazi";

export interface XingmingInterpretation {
  query: string;
  knowledgeHits: Array<{ topic?: string; summary?: string }>;
  knowledgeEvidence?: KnowledgeEvidenceItem[];
  excerpts: Array<{ source: string; excerpt: string }>;
  cases: Array<Record<string, unknown>>;
  summary?: string | null;
  summaryProfessional?: string;
  summaryPlain?: string;
  agentId?: string | null;
}

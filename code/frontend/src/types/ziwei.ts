import type { CalendarType } from "./bazi";

export type ZiweiLeapMonthRule = "next_month" | "midmonth_split";
export type ZiweiZiHourRule = "combined" | "split";
export type ZiweiMutagenTable = "nan_pai" | "geng_beipai" | "wu_pai" | "ren_pai";

export interface ZiweiRules {
  leapMonthRule: ZiweiLeapMonthRule;
  ziHourRule: ZiweiZiHourRule;
  mutagenTable: ZiweiMutagenTable;
}

export interface ZiweiChartRequest {
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
  targetYear?: number;
  question?: string;
  rules: ZiweiRules;
}

export interface ZiweiStar {
  name: string;
  type: string;
  brightness: string | null;
  mutagen: string | null;
}

export interface ZiweiPalace {
  index: number;
  name: string;
  stemBranch: string;
  heavenlyStem: string;
  earthlyBranch: string;
  isBody: boolean;
  majorStars: ZiweiStar[];
  minorStars: ZiweiStar[];
  adjStars: ZiweiStar[];
  decadalRange: string;
  minorAges: number[];
}

export interface ZiweiChart {
  input: ZiweiChartRequest & { rules: ZiweiRules };
  rulesMeta: ZiweiRules & { warnings?: string[] };
  trueSolarTime: string;
  solarLabel: string;
  lunarLabel: string;
  fourPillars: Record<string, string>;
  meta: {
    bureau: string;
    soul: string;
    body: string;
    soulPalaceBranch: string;
    bodyPalaceBranch: string;
    gender: string;
    zodiac: string;
    sign: string;
    chineseDate: string;
    time: string;
    timeRange: string;
  };
  palaces: ZiweiPalace[];
  limits: {
    decadal: Array<{
      index: number;
      ageRange: string;
      palace: string;
      stemBranch: string;
    }>;
    minor: Array<{ age: number; palace: string; stemBranch: string }>;
    yearly: Record<string, unknown>;
    current: Record<string, unknown>;
  };
}

export interface ZiweiInterpretation {
  query: string;
  knowledgeHits: Array<Record<string, unknown>>;
  excerpts: Array<{ source: string; excerpt: string }>;
  summary: string;
  agentId?: string;
}

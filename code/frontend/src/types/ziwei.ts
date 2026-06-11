import type { CalendarType } from "./bazi";

export type ZiweiLeapMonthRule = "next_month" | "midmonth_split";
export type ZiweiZiHourRule = "combined" | "split";
export type ZiweiMutagenTable = "nan_pai" | "geng_beipai" | "wu_pai" | "ren_pai";
export type ZiweiChartSchool = "sanhe" | "feixing";

export type ZiweiRuntimeLayer =
  | "native"
  | "decadal"
  | "yearly"
  | "monthly"
  | "daily"
  | "hourly";

export type ZiweiDisplayLayer =
  | "native"
  | "mutagen"
  | "malefic"
  | "triad"
  | "decadal"
  | "yearly"
  | "all";

export type ZiweiHighlightMode = "none" | "mutagen" | "malefic";

export type ZiweiChartDetailLevel = "simple" | "pro";

export type ZiweiDisplayMode = ZiweiChartDetailLevel;

export interface ZiweiRules {
  leapMonthRule: ZiweiLeapMonthRule;
  ziHourRule: ZiweiZiHourRule;
  mutagenTable: ZiweiMutagenTable;
  chartSchool: ZiweiChartSchool;
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
  detailLevel?: ZiweiChartDetailLevel;
  question?: string;
  rules: ZiweiRules;
}

export interface ZiweiPalacePosition {
  row?: number;
  col?: number;
  branch?: string;
}

export interface ZiweiStar {
  name: string;
  type: string;
  brightness: string | null;
  mutagen: string | null;
  group?: "major" | "minor" | "adj";
}

export interface ZiweiStarGroups {
  major: ZiweiStar[];
  minor: ZiweiStar[];
  adj: ZiweiStar[];
}

export interface ZiweiMutagenStar {
  name: string;
  mutagen: string;
  group?: string;
  palaceName?: string;
  palaceBranch?: string;
}

export interface ZiweiFlyingMutagen {
  mutagen: string;
  star: string;
  targetPalace?: string;
  targetBranch?: string;
  sourcePalace?: string;
  sourceStem?: string;
  sourceBranch?: string;
}

export interface ZiweiFlyingMutagens {
  outbound: ZiweiFlyingMutagen[];
  inbound: ZiweiFlyingMutagen[];
}

export interface ZiweiPalace {
  index: number;
  name: string;
  stemBranch: string;
  heavenlyStem: string;
  earthlyBranch: string;
  isBody: boolean;
  isSoul?: boolean;
  position?: ZiweiPalacePosition;
  oppositeBranch?: string;
  triadBranches?: string[];
  majorStars: ZiweiStar[];
  minorStars: ZiweiStar[];
  adjStars: ZiweiStar[];
  starGroups?: ZiweiStarGroups;
  mutagenStars?: ZiweiMutagenStar[];
  hasMalefic?: boolean;
  brightnessSummary?: string;
  decadalRange: string;
  minorAges: number[];
  flyingMutagens?: ZiweiFlyingMutagens;
}

export interface ZiweiActiveLimitLayer {
  layer: ZiweiRuntimeLayer | string;
  available: boolean;
  reason?: string;
  name?: string;
  targetYear?: number;
  heavenlyStem?: string;
  earthlyBranch?: string;
  stemBranch?: string;
  palaceNames?: string[];
  palaceBranches?: string[];
  mutagens?: string[];
  mutagenStars?: ZiweiMutagenStar[];
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
    detailLevel?: ZiweiChartDetailLevel;
    chartSchool?: ZiweiChartSchool;
  };
  palaces: ZiweiPalace[];
  limits: {
    decadal: Array<{
      index: number;
      ageRange: string;
      palace: string;
      stemBranch: string;
      startAge?: number;
    }>;
    minor: Array<{ age: number; palace: string; stemBranch: string }>;
    yearly: Record<string, unknown>;
    current: Record<string, unknown>;
    active?: Partial<Record<ZiweiRuntimeLayer, ZiweiActiveLimitLayer>>;
  };
}

export interface ZiweiInterpretation {
  query: string;
  knowledgeHits: Array<Record<string, unknown>>;
  excerpts: Array<{ source: string; excerpt: string }>;
  summary: string;
  agentId?: string;
}

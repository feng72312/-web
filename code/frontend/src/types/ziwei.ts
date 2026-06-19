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
  triadEvidence?: Array<{ name: string; majorStars?: string[] }>;
  oppositeEvidence?: { name?: string; majorStars?: string[] };
  borrowedFromOpposite?: boolean;
  borrowedMajorStars?: string[];
  palaceStrength?: string;
  riskFlags?: string[];
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
  summaryPlain?: string;
  summaryProfessional?: string;
  judgement?: ZiweiJudgementReport;
  tieredEvidence?: ZiweiTieredEvidence;
  tieredEvidenceSummary?: ZiweiTieredEvidenceSummary;
}

export interface ZiweiJudgeVerdict {
  role: string;
  classic?: string;
  summary: string;
  stance?: string;
  ruleIds?: string[];
  confidenceBand?: string;
  boundary?: string;
  flags?: Record<string, unknown>;
}

export interface ZiweiJudgementStep {
  id: string;
  label: string;
  status: string;
  summary: string;
}

export interface ZiweiTieredEvidenceGroup {
  bucket: string;
  label: string;
  count: number;
  preview?: string[];
}

export interface ZiweiTieredEvidenceSummary {
  groups?: ZiweiTieredEvidenceGroup[];
  total?: number;
  caseOverreachRisk?: boolean;
  note?: string;
}

export interface ZiweiTieredEvidence {
  primaryEvidence?: Array<{ source: string; excerpt: string; authorityTier?: string }>;
  secondaryEvidence?: Array<{ source: string; excerpt: string; authorityTier?: string }>;
  schoolCommentary?: Array<{ source: string; excerpt: string; authorityTier?: string }>;
  caseReference?: Array<{ source: string; excerpt: string }>;
  excludedOrUnreadable?: Array<{ source: string; excerpt: string }>;
}

export interface ZiweiJudgementReport {
  steps?: ZiweiJudgementStep[];
  topic?: {
    topicId?: string;
    topicLabel?: string;
    targetPalaces?: string[];
    confidence?: number;
  };
  judges?: ZiweiJudgeVerdict[];
  arbitration?: {
    conflicts?: string[];
    finalBoundaries?: string[];
    confidenceScore?: number;
    confidenceBand?: "strong" | "medium" | "weak";
    summary?: string;
  };
  evidenceChain?: Array<{
    conclusion: string;
    ruleId?: string;
    primaryClassic?: string;
    quote?: string;
    boundary?: string;
  }>;
  tieredEvidence?: ZiweiTieredEvidence;
  tieredEvidenceSummary?: ZiweiTieredEvidenceSummary;
  enrichedChart?: ZiweiChart;
  rulesMeta?: ZiweiRules & { warnings?: string[] };
}

export const ZIWEI_JUDGE_ROLE_LABELS: Record<string, string> = {
  topic: "占事分类",
  palace: "宫位裁判",
  star: "星曜裁判",
  mutagen: "四化裁判",
  pattern: "格局裁判",
  limit: "限运裁判",
  cross_school: "法派仲裁",
};

export const ZIWEI_TIERED_BUCKET_LABELS: Record<keyof ZiweiTieredEvidence, string> = {
  primaryEvidence: "主裁典籍",
  secondaryEvidence: "辅助古籍",
  schoolCommentary: "派别视角",
  caseReference: "命例参考",
  excludedOrUnreadable: "不可用资料",
};

export interface ZiweiJudgementOverlay {
  limitPalaces: Set<string>;
  patternLabels: string[];
  showFlyingMutagen: boolean;
}

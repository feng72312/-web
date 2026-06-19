export type CastMethod = "coin" | "number" | "time";

export interface KongPoState {
  xunKong?: boolean;
  yuePo?: boolean;
}

export interface LiuyaoLine {
  position: number;
  value: number;
  isMoving: boolean;
  isYang: boolean;
  branch: string;
  stem: string;
  liuqin: string;
  liushen: string;
  isShi: boolean;
  isYing: boolean;
  lineStrength?: string;
  kongPoState?: KongPoState;
  riskFlags?: string[];
}

export interface LiuyaoChart {
  input: {
    question: string;
    method: CastMethod;
  };
  benGua: {
    name: string;
    lower: string;
    upper: string;
    palace: string;
    palaceElement: string;
  };
  bianGua: { name: string; lower?: string; upper?: string } | null;
  lines: LiuyaoLine[];
  movingLines: number[];
  shiYing: { shi: number; ying: number };
  monthJian: string;
  dayChen: string;
  dayGan: string;
  meta?: { castNote?: string; lineValues?: number[]; rules?: string };
  riskFlags?: {
    benLiuChong?: boolean;
    bianLiuChong?: boolean;
    movingCount?: number;
  };
}

export interface YongShenResult {
  yongShen: string;
  position: number;
  reason: string;
  source: string;
  confidence?: number;
  topicId?: string;
  ruleId?: string;
  override?: boolean;
}

export interface LiuyaoJudgeVerdict {
  role: string;
  classic?: string;
  summary: string;
  stance?: string;
  ruleIds?: string[];
  confidenceBand?: string;
  boundary?: string;
  flags?: Record<string, unknown>;
}

export interface LiuyaoJudgementStep {
  id: string;
  label: string;
  status: string;
  summary: string;
}

export interface TieredEvidenceGroup {
  bucket: string;
  label: string;
  count: number;
  preview?: string[];
}

export interface TieredEvidenceSummary {
  groups?: TieredEvidenceGroup[];
  total?: number;
  caseOverreachRisk?: boolean;
  note?: string;
}

export interface TieredEvidence {
  primaryEvidence?: Array<{ source: string; excerpt: string; authorityTier?: string }>;
  secondaryEvidence?: Array<{ source: string; excerpt: string; authorityTier?: string }>;
  caseReference?: Array<{ source: string; excerpt: string }>;
  modernSupport?: Array<{ source: string; excerpt: string }>;
  excludedOrLowTrust?: Array<{ source: string; excerpt: string }>;
}

export interface LiuyaoJudgementReport {
  steps?: LiuyaoJudgementStep[];
  topic?: {
    topicId?: string;
    topicLabel?: string;
    candidateYongShen?: string;
    confidence?: number;
  };
  yongShen?: YongShenResult;
  judges?: LiuyaoJudgeVerdict[];
  arbitration?: {
    judgeOpinions?: LiuyaoJudgeVerdict[];
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
  tieredEvidence?: TieredEvidence;
  tieredEvidenceSummary?: TieredEvidenceSummary;
  enrichedChart?: LiuyaoChart;
}

export interface LiuyaoDivineRequest {
  question: string;
  method: CastMethod;
  coinLines?: number[];
  numbers?: number[];
  year?: number;
  month?: number;
  day?: number;
  hour?: number;
  minute?: number;
  second?: number;
  calendarType?: "solar" | "lunar";
  isLeapMonth?: boolean;
}

export interface LiuyaoInterpretation {
  query: string;
  yongShen: YongShenResult;
  excerpts: Array<{ source: string; excerpt: string; authorityTier?: string }>;
  summary: string;
  summaryProfessional?: string;
  summaryPlain?: string;
  agentId?: string;
  judgement?: LiuyaoJudgementReport;
  tieredEvidence?: TieredEvidence;
  tieredEvidenceSummary?: TieredEvidenceSummary;
  confidence?: number;
  confidenceBand?: string;
  conflicts?: string[];
}

export const LIUQIN_OPTIONS = ["父母", "兄弟", "子孙", "妻财", "官鬼"];

export const JUDGE_ROLE_LABELS: Record<string, string> = {
  topic: "占事分类",
  yong_shen: "用神定位",
  wang_shuai: "旺衰空破",
  sheng_ke: "生克原忌",
  dong_bian: "动变六冲",
  shi_ying: "世应关系",
  liu_shen: "六神辅助",
  ying_qi: "应期边界",
};

export const TIERED_BUCKET_LABELS: Record<string, string> = {
  primaryEvidence: "主裁典籍",
  secondaryEvidence: "辅助古籍",
  caseReference: "卦例参考",
  modernSupport: "现代补充",
  excludedOrLowTrust: "低信排除",
};

import type { ComponentType } from "react";
import type { ZiHourPhase } from "../utils/timeSlots";

export type CalendarType = "solar" | "lunar";

export interface PaipanRequest {
  name: string;
  calendarType: CalendarType;
  year: number;
  month: number;
  day: number;
  isLeapMonth: boolean;
  hour: number;
  minute: number;
  gender: number;
}

export interface BirthFormState {
  activeProfileId: string | null;
  name: string;
  calendarType: CalendarType;
  year: number;
  month: number;
  day: number;
  isLeapMonth: boolean;
  hourSlot: number;
  ziHourPhase: ZiHourPhase;
  minute: number;
  gender: number;
}

export interface BaziProfileSettings {
  /** Reserved for per-profile bazi options */
}

export interface ZiweiProfileSettings {
  useTrueSolarTime: boolean;
  longitude: number;
  leapMonthRule: "next_month" | "midmonth_split";
  ziHourRule: "combined" | "split";
  mutagenTable?: "nan_pai" | "geng_beipai" | "wu_pai" | "ren_pai";
  chartSchool?: "sanhe" | "feixing";
}

export interface SavedProfile {
  id: string;
  name: string;
  calendarType: CalendarType;
  year: number;
  month: number;
  day: number;
  isLeapMonth: boolean;
  hourSlot: number;
  ziHourPhase?: ZiHourPhase;
  minute: number;
  gender: number;
  baziSettings?: BaziProfileSettings;
  ziweiSettings?: ZiweiProfileSettings;
  createdAt: string;
  updatedAt: string;
}

export interface Pillar {
  gan: string;
  zhi: string;
  ganzhi: string;
  ganWuxing: string;
  zhiWuxing: string;
  nayin: string;
  hideGan: string[];
  shishenGan: string;
  shishenZhi: string[];
}

export interface FlowPillar {
  gan: string;
  zhi: string;
  ganzhi: string;
  shishenGan: string;
  hideStems: string[];
  xunkong: string;
  ganWuxing: string;
  zhiWuxing: string;
  shenSha?: string[];
}

export interface PillarDetailColumn {
  key: "year" | "month" | "day" | "hour";
  label: string;
  shishen: string;
  gan: string;
  zhi: string;
  ganWuxing: string;
  zhiWuxing: string;
  hideStems: string[];
  nayin: string;
  xunkong: string;
  shenSha: string[];
}

export interface PillarDetail {
  columns: PillarDetailColumn[];
  stemNotes: string;
  branchNotes: string;
  boneWeight: string;
  boneComment: string;
}

export interface LiuyueItem {
  index: number;
  ganzhi: string;
  monthLabel: string;
  xunkong: string;
  pillar: FlowPillar;
}

export interface LiunianItem {
  year: number;
  age: number;
  ganzhi: string;
  xunkong: string;
  pillar: FlowPillar;
  liuyue: LiuyueItem[];
}

export interface DayunTimelineItem {
  index: number;
  ganzhi: string;
  startAge: number;
  endAge: number;
  startYear: number;
  endYear: number;
  xunkong: string;
  pillar: FlowPillar;
  liunian: LiunianItem[];
}

export interface LiuriDay {
  date: string;
  day: number;
  ganzhi: string;
  gan: string;
  zhi: string;
  shishenGan: string;
  hideStems: string[];
  xunkong: string;
  ganWuxing: string;
  zhiWuxing: string;
  shenSha?: string[];
}

export interface LuckTimeline {
  current: {
    dayunIndex: number;
    liunianYear: number;
    liuyueIndex: number;
    liuriDate: string;
  };
  birthYear: number;
  genderRole: string;
  dayMaster: string;
  dayunStart: Record<string, number>;
  dayunForward: boolean;
  birthPillars: Record<"year" | "month" | "day" | "hour", FlowPillar>;
  dayun: DayunTimelineItem[];
  liuriByYear: Record<string, Record<string, LiuriDay[]>>;
  jieqi: string[];
}

export interface Chart {
  input: PaipanRequest & { second?: number };
  solar: string;
  lunar: string;
  pillars: Record<"year" | "month" | "day" | "hour", Pillar>;
  dayMaster: string;
  dayMasterWuxing: string;
  wuxingCount: Record<string, number>;
  dayun: Array<{
    index: number;
    ganzhi: string;
    startAge: number;
    endAge: number;
    startYear: number;
  }>;
  dayunStart: Record<string, number>;
  dayunForward: boolean;
  meta: {
    rules: Record<string, string | number>;
    inputLabel?: string;
    calendarType?: CalendarType;
  };
  pillarDetail?: PillarDetail;
  luckTimeline?: LuckTimeline;
}

export interface AnalysisSection {
  id: string;
  name: string;
  order: number;
  data: Record<string, unknown>;
}

export interface PaipanResponse {
  chart: Chart;
  sections: AnalysisSection[];
  modules: Array<{ id: string; name: string; order: number }>;
}

export interface KnowledgeClaimEvidence {
  classic: string;
  chapter: string;
  quote: string;
  conclusion: string;
  role: string;
  sourceFile?: string;
  sourceCategory?: string;
}

export interface KnowledgeEvidenceItem {
  id: string;
  topic: string;
  summary: string;
  agreementLevel: string;
  sourceTier: string;
  domain: string;
  claims: KnowledgeClaimEvidence[];
}

export interface FusionChannelBlock {
  channel: string;
  summary: string;
  stance: string;
  available: boolean;
  error?: string;
  query?: string;
  excerpts?: Array<{ source?: string; excerpt?: string }>;
  knowledgeEvidence?: KnowledgeEvidenceItem[];
  benGuaName?: string;
  castNote?: string;
  yongShen?: { yongShen: string; position: number; reason?: string };
}

export interface FusionBlock {
  question: string;
  questionScope: "life_outline" | "event_detail" | "mixed";
  agreed: boolean;
  preferredChannel: string;
  weightNote: string;
  bazi: FusionChannelBlock;
  liuyao: FusionChannelBlock;
  merged: { summary: string };
}

export interface TripleFusionBlock {
  question: string;
  questionScope: string;
  preferredChannel: string;
  bazi: FusionChannelBlock;
  ziwei: FusionChannelBlock;
  xingming: FusionChannelBlock;
  merged: { summary: string };
}

export interface ConsensusBlock {
  question?: string;
  fusionMode?: string;
  leadDiscipline?: string;
  confidenceScore?: number;
  confidenceBand?: "strong" | "medium" | "weak";
  consensusPoints?: string[];
  conflictPoints?: string[];
  conflictExplanation?: string;
  merged?: { summary?: string };
}

export interface JudgeVerdict {
  role: string;
  classic: string;
  summary: string;
  stance: string;
  ruleIds?: string[];
  confidenceBand?: "strong" | "medium" | "weak";
  conclusionKind?: string;
  boundary?: string;
}

export interface JudgementStep {
  id: string;
  label: string;
  status: string;
  summary: string;
}

export interface EvidenceChainItem {
  conclusion: string;
  ruleId?: string;
  primaryClassic?: string;
  quote?: string;
  secondary?: string[];
  conflicts?: string[];
  boundary?: string;
  confidence?: "strong" | "medium" | "weak";
  conclusionKind?: string;
}

export interface TieredEvidenceSummaryGroup {
  bucket: string;
  label: string;
  count: number;
  preview: string[];
}

export interface TieredEvidenceSummary {
  groups?: TieredEvidenceSummaryGroup[];
  total?: number;
  caseOverreachRisk?: boolean;
  note?: string;
}

export interface TieredEvidence {
  primaryEvidence?: Array<Record<string, unknown>>;
  secondaryEvidence?: Array<Record<string, unknown>>;
  caseReference?: Array<Record<string, unknown>>;
  excludedOrLowTrust?: Array<Record<string, unknown>>;
}

export interface InterpretSegmentRuleRef {
  ruleId: string;
  classic?: string;
  role?: string;
  conclusion?: string;
  verified?: boolean;
}

export interface InterpretSegmentEvidenceRef {
  ruleId: string;
  classic?: string;
  conclusion?: string;
}

export interface InterpretSegment {
  text: string;
  rawText?: string;
  ruleIdRefs?: InterpretSegmentRuleRef[];
  evidenceRefs?: InterpretSegmentEvidenceRef[];
  kind: "anchored" | "inference";
}

export interface InterpretSegmentStats {
  total: number;
  anchored: number;
  inference: number;
  anchoredRatio: number;
}

export interface BaziJudgementReport {
  steps?: JudgementStep[];
  arbitration?: {
    judgeOpinions?: JudgeVerdict[];
    conflicts?: string[];
    finalBoundaries?: string[];
    confidenceScore?: number;
    confidenceBand?: "strong" | "medium" | "weak";
  };
  evidenceChain?: EvidenceChainItem[];
  tieredEvidence?: TieredEvidence;
  tieredEvidenceSummary?: TieredEvidenceSummary;
  lookupKeys?: Record<string, unknown>;
  ruleIdRefs?: Array<{
    ruleId: string;
    classic?: string;
    role?: string;
    conclusion?: string;
  }>;
}

export interface Interpretation {
  query: string;
  excerpts: Array<{ source: string; excerpt: string; authorityTier?: string; evidenceRole?: string }>;
  summary: string;
  summaryProfessional?: string;
  summaryPlain?: string;
  agentId?: string;
  confidenceBand?: "strong" | "medium" | "weak";
  confidenceScore?: number;
  consensus?: ConsensusBlock;
  questionConsensus?: ConsensusBlock;
  fusion?: FusionBlock;
  tripleFusion?: TripleFusionBlock;
  baziZiweiFusion?: Record<string, unknown>;
  judgement?: BaziJudgementReport;
  tieredEvidence?: TieredEvidence;
  tieredEvidenceSummary?: TieredEvidenceSummary;
  knowledgeEvidence?: KnowledgeEvidenceItem[];
  ruleIdRefs?: BaziJudgementReport["ruleIdRefs"];
  segments?: InterpretSegment[];
  segmentStats?: InterpretSegmentStats;
  confidenceNote?: string;
}

export interface InterpretResponse extends PaipanResponse {
  interpretation: Interpretation;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatStatus {
  enabled: boolean;
  model: string;
  models: ChatModelOption[];
  cursorEnabled?: boolean;
  deepseekEnabled?: boolean;
}

export interface ChatModelOption {
  id: string;
  label: string;
  tag: string;
  provider: string;
  tier?: string;
  tierRank?: number;
}

export interface SectionModuleProps {
  section: AnalysisSection;
  chart: Chart;
}

export interface SectionModuleDefinition {
  id: string;
  order: number;
  Component: ComponentType<SectionModuleProps>;
}

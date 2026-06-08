export type FengshuiMethod = "bazhai" | "xuankong";
export type FengshuiScene = "residence" | "shop" | "office";

export interface FengshuiChartRequest {
  question: string;
  method?: FengshuiMethod;
  scene?: FengshuiScene;
  birthYear: number;
  gender: 0 | 1;
  sittingMountain: string;
  buildYear?: number;
  flowYear?: number;
}

export interface FengshuiGuaInfo {
  number: number;
  name: string;
  alias: string;
  direction: string;
  group: "dongsi" | "xisi";
  groupLabel: string;
  sitting?: string;
  facing?: string;
  label?: string;
}

export interface FengshuiPeriodInfo {
  number: number;
  label: string;
  yuan: string;
  rangeStart: number;
  rangeEnd: number;
}

export interface FengshuiStarCell {
  palace: string;
  star?: number;
  starName?: string;
  kind?: string;
  yunStar?: number;
  shanStar?: number;
  xiangStar?: number;
  label?: string;
  yunName?: string;
  shanName?: string;
  xiangName?: string;
}

export interface FengshuiXuankongPan {
  period: FengshuiPeriodInfo;
  sitting: string;
  facing: string;
  label: string;
  sittingStarCenter: number;
  facingStarCenter: number;
  shanFly: string;
  xiangFly: string;
  yunPan: FengshuiStarCell[];
  shanPan: FengshuiStarCell[];
  xiangPan: FengshuiStarCell[];
  combinedPan: FengshuiStarCell[];
  flowYear?: number;
  flowPan?: FengshuiStarCell[];
}

export interface FengshuiDirection {
  type: string;
  label: string;
  auspicious: boolean;
  trigram: string;
  direction: string;
}

export interface FengshuiPalaceCell {
  name: string;
  direction: string;
  labels: string[];
  auspicious: boolean;
}

export interface FengshuiMountain {
  id: string;
  name: string;
  trigram: string;
  facing: string;
  label: string;
}

export interface FengshuiChart {
  input: FengshuiChartRequest;
  mingGua?: FengshuiGuaInfo;
  zhaiGua?: FengshuiGuaInfo;
  compatible?: boolean;
  directions?: FengshuiDirection[];
  palaces?: FengshuiPalaceCell[];
  advice?: string[];
  xuankong?: FengshuiXuankongPan;
  meta?: Record<string, unknown>;
}

export interface FengshuiInterpretation {
  query: string;
  knowledgeHits?: Array<{ topic?: string; summary?: string }>;
  excerpts: Array<{ source?: string; excerpt?: string }>;
  summary: string;
  summaryProfessional?: string;
  summaryPlain?: string;
  agentId?: string;
}

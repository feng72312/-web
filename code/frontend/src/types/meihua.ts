export type MeihuaCastMethod = "number" | "time";

export interface MeihuaLine {
  position: number;
  value: number;
  isMoving: boolean;
  isYang: boolean;
  inLower: boolean;
}

export interface MeihuaGuaInfo {
  name: string;
  lower: string;
  upper: string;
  lowerElement?: string;
  upperElement?: string;
}

export interface MeihuaTrigramInfo {
  name: string;
  element: string;
}

export interface MeihuaChart {
  input: {
    question: string;
    method: MeihuaCastMethod;
    movingPositionOverride?: number;
  };
  benGua: MeihuaGuaInfo;
  bianGua: MeihuaGuaInfo | null;
  huGua: MeihuaGuaInfo | null;
  lines: MeihuaLine[];
  movingLines: number[];
  tiGua: MeihuaTrigramInfo;
  yongGua: MeihuaTrigramInfo;
  tiYongRelation: string;
  isStatic: boolean;
  meta?: { castNote?: string; lineValues?: number[] };
}

export interface MeihuaDivineRequest {
  question: string;
  method: MeihuaCastMethod;
  numbers?: number[];
  year?: number;
  month?: number;
  day?: number;
  hour?: number;
  minute?: number;
  second?: number;
  calendarType?: "solar" | "lunar";
  isLeapMonth?: boolean;
  movingPositionOverride?: number;
}

export interface MeihuaInterpretation {
  query: string;
  tiYong: {
    tiGua: MeihuaTrigramInfo;
    yongGua: MeihuaTrigramInfo;
    relation: string;
    isStatic: boolean;
  };
  knowledgeHits?: Array<{ topic: string; summary: string }>;
  excerpts: Array<{ source: string; excerpt: string }>;
  summary: string;
  summaryProfessional?: string;
  summaryPlain?: string;
  agentId?: string;
}

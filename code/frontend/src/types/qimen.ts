export type QimenCategory = "shizhan" | "xingzhan";
export type QimenMethod = "chaibu" | "zhirun" | "maoshan";

export interface BirthProfileSummary {
  year: string;
  month: string;
  day: string;
  hour: string;
  gender: string;
  summary: string;
}

export interface QimenChartRequest {
  question: string;
  category: QimenCategory;
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second?: number;
  calendarType?: "solar" | "lunar";
  isLeapMonth?: boolean;
  useTrueSolarTime?: boolean;
  longitude?: number;
  direction?: string;
  method?: QimenMethod;
  juOverride?: number | null;
  birthProfile?: BirthProfileSummary | null;
}

export interface PalaceCell {
  index: number;
  name: string;
  earth: string;
  heaven: string;
  human: string;
  star: string;
  door: string;
  god: string;
}

export interface JuInfo {
  dunType: string;
  juNumber: number;
  yuan: string;
  jieqi: string;
  juName: string;
  fuTou?: string;
  xunShou?: string;
}

export interface ZhiFuZhiShi {
  zhiFuStar: string;
  zhiFuGong: string;
  zhiFuGan: string;
  zhiShiDoor: string;
  zhiShiGong: string;
}

export interface QimenChart {
  input: QimenChartRequest & { question: string };
  ju: JuInfo;
  zhiFuZhiShi: ZhiFuZhiShi;
  palaces: PalaceCell[];
  fourPillars: { year: string; month: string; day: string; hour: string };
  trueSolarTime: string;
  meta?: Record<string, unknown>;
  birthProfile?: BirthProfileSummary;
}

export interface QimenInterpretation {
  query: string;
  ju?: JuInfo;
  zhiFuZhiShi?: ZhiFuZhiShi;
  knowledgeHits?: Array<{ topic?: string; summary?: string }>;
  excerpts: Array<{ source?: string; excerpt?: string }>;
  summary: string;
  summaryProfessional?: string;
  summaryPlain?: string;
  agentId?: string;
}

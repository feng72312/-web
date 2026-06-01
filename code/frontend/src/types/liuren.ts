export type LiurenCategory = "shizhan" | "xingzhan";
export type LiurenCastMethod = "liuren" | "jinkou" | "both";

export interface LiurenChartRequest {
  question: string;
  castMethod?: LiurenCastMethod;
  category?: LiurenCategory;
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
  jinkouDifen?: string;
  guiRenMode?: number;
}

export interface KeEntry {
  pair: string;
  general: string;
}

export interface ChuanEntry {
  zhi: string;
  general: string;
  liuQin: string;
  xunKong: string;
}

export interface LiurenPan {
  fourPillars: { year: string; month: string; day: string; hour: string };
  jieqi: string;
  lunarMonth: string;
  yueJiang: string;
  siKe: { yi: KeEntry; er: KeEntry; san: KeEntry; si: KeEntry };
  sanChuan: { chu: ChuanEntry; zhong: ChuanEntry; mo: ChuanEntry };
  tianDiPan: {
    earth: string[];
    sky: string[];
    generals: string[];
    palaces: Array<{ earth: string; sky: string; general: string }>;
  };
  geJu: { name: string; sub: string };
  shenSha: Record<string, string>;
  trueSolarTime: string;
  meta?: Record<string, unknown>;
}

export interface JinkouPan {
  renYuan: string;
  guiShen: string[];
  jiangShen: string[];
  difen: string;
  fourPillars: { year: string; month: string; day: string; hour: string };
}

export interface LiurenChart {
  input: LiurenChartRequest;
  liuren?: LiurenPan;
  jinkou?: JinkouPan;
  trueSolarTime: string;
  meta?: Record<string, unknown>;
}

export interface LiurenInterpretation {
  query: string;
  knowledgeHits?: Array<{ topic?: string; summary?: string }>;
  excerpts: Array<{ source?: string; excerpt?: string }>;
  summary: string;
  summaryProfessional?: string;
  summaryPlain?: string;
  agentId?: string;
}

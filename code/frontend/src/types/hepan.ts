export type HepanScene = "romance" | "marriage" | "partnership";
export type HepanDiscipline = "auto" | "bazi" | "ziwei";

export interface HepanPersonRequest {
  name: string;
  calendarType: "solar" | "lunar";
  year: number;
  month: number;
  day: number;
  isLeapMonth: boolean;
  hour: number;
  minute: number;
  second?: number;
  gender: number;
}

export interface HepanChartRequest {
  personA: HepanPersonRequest;
  personB: HepanPersonRequest;
  scene: HepanScene;
  discipline: HepanDiscipline;
  question?: string;
  useTrueSolarTime?: boolean;
  longitude?: number;
  targetYear?: number | null;
  ziweiRules?: {
    leapMonthRule: "next_month" | "midmonth_split";
    ziHourRule: "combined" | "split";
    mutagenTable: "nan_pai" | "geng_beipai" | "wu_pai" | "ren_pai";
  };
}

export interface HepanCrossNote {
  id: string;
  level: "fit" | "caution" | "neutral";
  dimension: string;
  title: string;
  detail: string;
  source: "bazi" | "ziwei";
}

export interface HepanPersonCharts {
  name: string;
  gender: number;
  baziChart?: Record<string, unknown> | null;
  ziweiChart?: Record<string, unknown> | null;
}

export interface HepanChartResponse {
  scene: HepanScene;
  discipline: "bazi" | "ziwei";
  personA: HepanPersonCharts;
  personB: HepanPersonCharts;
  crossNotes: HepanCrossNote[];
  summaryTags: string[];
  question: string;
}

export interface HepanInterpretation {
  query: string;
  excerpts: Array<{ source: string; excerpt: string }>;
  summary?: string | null;
  agentId?: string | null;
}

export interface HepanSceneOption {
  id: HepanScene;
  label: string;
  defaultDiscipline: "bazi" | "ziwei";
  defaultQuestion: string;
}

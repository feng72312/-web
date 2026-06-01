export type CastMethod = "coin" | "number" | "time";

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
  bianGua: { name: string } | null;
  lines: LiuyaoLine[];
  movingLines: number[];
  shiYing: { shi: number; ying: number };
  monthJian: string;
  dayChen: string;
  dayGan: string;
  meta?: { castNote?: string };
}

export interface YongShenResult {
  yongShen: string;
  position: number;
  reason: string;
  source: string;
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
  excerpts: Array<{ source: string; excerpt: string }>;
  summary: string;
  summaryProfessional?: string;
  summaryPlain?: string;
  agentId?: string;
}

export const LIUQIN_OPTIONS = ["父母", "兄弟", "子孙", "妻财", "官鬼"];

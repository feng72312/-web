import type { ComponentType } from "react";

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
  minute: number;
  gender: number;
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
  minute: number;
  gender: number;
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

export interface Interpretation {
  query: string;
  excerpts: Array<{ source: string; excerpt: string }>;
  summary: string;
  agentId?: string;
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

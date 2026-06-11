export type FusionSourceModuleId =
  | "01"
  | "02"
  | "03"
  | "04"
  | "05"
  | "06"
  | "09"
  | "11"
  | "12"
  | "12:hepan"
  | "13"
  | string;

export interface FusionChartSource {
  sourceId: string;
  moduleId: FusionSourceModuleId;
  moduleLabel: string;
  title: string;
  subtitle?: string;
  question?: string;
  chartSnapshot: Record<string, unknown>;
  summaryPlain?: string;
  summaryProfessional?: string;
  agentId?: string;
  createdAt: string;
  updatedAt: string;
  sourceVersion: number;
}

export interface FusionChatInitSourceInput {
  moduleId: string;
  moduleLabel: string;
  title: string;
  question?: string;
  chartSnapshot: Record<string, unknown>;
  summaryPlain?: string;
  summaryProfessional?: string;
  createdAt?: string;
}

export interface FusionChatInitResult {
  agentId: string;
  title: string;
  scenario: string;
  sourceCount: number;
}

export const FUSION_SOURCE_VERSION = 1;
export const FUSION_MAX_SOURCES = 50;
export const FUSION_MAX_CHART_JSON_CHARS = 80_000;

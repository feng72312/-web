export interface ZhugeDivineResult {
  chars: string;
  rawStrokes: number[];
  reducedStrokes: number[];
  qianNo: number;
  qianText: string;
  steps: string[];
  missingText: boolean;
}

export interface JiemengMatch {
  section: string;
  text: string;
  score: string;
}

export interface JiemengSearchResult {
  dream: string;
  matches: JiemengMatch[];
}

export interface UtilsRagExcerpt {
  source?: string;
  excerpt?: string;
  text?: string;
  content?: string;
  file_name?: string;
}

export interface UtilsInterpretation {
  tool: string;
  payload: Record<string, unknown>;
  query?: string;
  excerpts: UtilsRagExcerpt[];
  summary?: string | null;
  summaryProfessional?: string | null;
  summaryPlain?: string | null;
  agentId?: string | null;
}

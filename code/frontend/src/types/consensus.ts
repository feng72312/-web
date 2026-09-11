export type ConfidenceBand = "strong" | "medium" | "weak";

export interface ConsensusPayload {
  question?: string;
  fusionMode?: "chart" | "question" | "mixed";
  leadDiscipline?: string;
  confidenceScore?: number;
  confidenceBand?: ConfidenceBand;
  consensusPoints?: string[];
  conflictPoints?: string[];
  conflictExplanation?: string;
  scope?: string;
  merged?: { summary?: string };
}

export interface UnifiedInterpretation {
  query?: string;
  summary?: string | null;
  summaryProfessional?: string | null;
  summaryPlain?: string | null;
  excerpts?: Array<{ text?: string; source?: string }>;
  confidenceBand?: ConfidenceBand;
  confidenceScore?: number;
  consensus?: ConsensusPayload;
  questionConsensus?: ConsensusPayload;
  riskTips?: string[];
  actionItems?: string[];
}

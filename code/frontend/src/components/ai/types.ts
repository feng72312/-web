import type { GeneralChatScenario } from "../../services/chatApi";

export type AiChatSessionSource = "general" | "module" | "fusion";

export interface AiChatSession {
  agentId: string;
  title: string;
  scenario: GeneralChatScenario;
  createdAt: string;
  source: AiChatSessionSource;
  moduleId?: string;
  moduleLabel?: string;
  subtitle?: string;
  fusionSourceIds?: string[];
  fusionSourceLabels?: string[];
}

export type AiThreadMessageStatus = "complete" | "running" | "error";

export interface AiThreadMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  status?: AiThreadMessageStatus;
  errorText?: string;
}

export interface AiScenarioConfig {
  id: GeneralChatScenario;
  label: string;
  title: string;
  description: string;
  quickPrompts: string[];
}

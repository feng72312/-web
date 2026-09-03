import type { AiChatSession } from "./types";

interface ModuleChatSessionInput {
  agentId: string;
  moduleId: string;
  moduleLabel: string;
  question?: string | null;
  chartName?: string | null;
  subtitle?: string | null;
}

const TITLE_PART_MAX = 28;

export function compactTitlePart(
  value: string | null | undefined,
  fallback = "",
): string {
  const cleaned = String(value ?? "")
    .replace(/\s+/g, " ")
    .trim();
  const text = cleaned || String(fallback ?? "");
  if (text.length <= TITLE_PART_MAX) {
    return text;
  }
  return `${text.slice(0, TITLE_PART_MAX - 1)}...`;
}

export function buildGeneralChatTitle(
  baseTitle: string,
  options?: { initialPrompt?: string; createdAt?: string },
): string {
  const createdAt = options?.createdAt ? new Date(options.createdAt) : new Date();
  const stamp = createdAt.toLocaleString("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  const prompt = compactTitlePart(options?.initialPrompt);
  if (prompt) {
    return `${baseTitle} · ${prompt}`;
  }
  return `${baseTitle} · ${stamp}`;
}

export function buildModuleChatTitle(
  moduleLabel: string,
  question?: string | null,
  chartName?: string | null,
): string {
  const compactQuestion = compactTitlePart(question);
  const compactChartName = compactTitlePart(chartName);
  if (compactQuestion && compactChartName) {
    return `${moduleLabel} · ${compactQuestion} / ${compactChartName}`;
  }
  if (compactQuestion) {
    return `${moduleLabel} · ${compactQuestion}`;
  }
  if (compactChartName) {
    return `${moduleLabel} · ${compactChartName}`;
  }
  return `${moduleLabel}会话`;
}

export function createModuleChatSessionRecord({
  agentId,
  moduleId,
  moduleLabel,
  question,
  chartName,
  subtitle,
}: ModuleChatSessionInput): AiChatSession {
  return {
    agentId,
    title: buildModuleChatTitle(moduleLabel, question, chartName),
    scenario: "review_result",
    createdAt: new Date().toISOString(),
    source: "module",
    moduleId,
    moduleLabel,
    subtitle: compactTitlePart(subtitle),
  };
}

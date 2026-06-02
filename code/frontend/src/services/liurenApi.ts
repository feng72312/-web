import type {
  LiurenChart,
  LiurenChartRequest,
  LiurenInterpretation,
} from "../types/liuren";
import { API_BASE } from "./config";
import { jsonDeviceHeaders, parseQuotaError } from "./deviceHeaders";
import type { InterpretStyle } from "../utils/interpretStyle";
import { refreshQuotaBar } from "../utils/quotaEvents";

async function postJson<T>(path: string, body: unknown, modelId?: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: await jsonDeviceHeaders(modelId),
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    if (response.status === 402) {
      refreshQuotaBar();
    }
    throw new Error(parseQuotaError(text, response.status) || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchLiurenChart(
  body: LiurenChartRequest,
): Promise<{ chart: LiurenChart }> {
  return postJson("/liuren/chart", body);
}

export function fetchLiurenRagSearch(
  chart: LiurenChart,
  question?: string,
): Promise<{ query: string; excerpts: LiurenInterpretation["excerpts"] }> {
  return postJson("/liuren/rag/search", { chart, question });
}

export async function fetchLiurenInterpret(
  chart: LiurenChart,
  excerpts?: LiurenInterpretation["excerpts"],
  model?: string,
  style?: InterpretStyle,
): Promise<{ chart: LiurenChart; interpretation: LiurenInterpretation }> {
  const result = await postJson<{ chart: LiurenChart; interpretation: LiurenInterpretation }>(
    "/liuren/interpret",
    { chart, excerpts, model, style },
    model,
  );
  refreshQuotaBar();
  return result;
}

export function initLiurenChatSession(
  chart: LiurenChart,
  excerpts?: LiurenInterpretation["excerpts"],
  knowledgeHits?: LiurenInterpretation["knowledgeHits"],
): Promise<{ agentId: string }> {
  return postJson("/liuren/chat/init", { chart, excerpts, knowledgeHits });
}

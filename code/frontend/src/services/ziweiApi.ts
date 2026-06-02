import type { ZiweiChart, ZiweiChartRequest, ZiweiInterpretation } from "../types/ziwei";
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

export function fetchZiweiChart(body: ZiweiChartRequest): Promise<{ chart: ZiweiChart }> {
  return postJson("/ziwei/chart", body);
}

export async function fetchZiweiInterpret(
  chart: ZiweiChart,
  excerpts?: ZiweiInterpretation["excerpts"],
  model?: string,
  style?: InterpretStyle,
  question?: string,
): Promise<{ chart: ZiweiChart; interpretation: ZiweiInterpretation }> {
  const result = await postJson<{ chart: ZiweiChart; interpretation: ZiweiInterpretation }>(
    "/ziwei/interpret",
    { chart, excerpts, model, style, question },
    model,
  );
  refreshQuotaBar();
  return result;
}

export function initZiweiChatSession(
  chart: ZiweiChart,
  excerpts?: ZiweiInterpretation["excerpts"],
  knowledgeHits?: ZiweiInterpretation["knowledgeHits"],
): Promise<{ agentId: string }> {
  return postJson("/ziwei/chat/init", { chart, excerpts, knowledgeHits });
}

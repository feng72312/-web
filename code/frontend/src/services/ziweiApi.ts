import type { ZiweiChart, ZiweiChartRequest, ZiweiInterpretation } from "../types/ziwei";
import { API_BASE } from "./config";
import { jsonDeviceHeaders, jsonPublicHeaders, parseQuotaError } from "./deviceHeaders";
import { fetchWithTimeout, parseResponseJson } from "./httpJson";
import type { InterpretStyle } from "../utils/interpretStyle";
import { refreshQuotaBar } from "../utils/quotaEvents";

async function postJson<T>(
  path: string,
  body: unknown,
  options?: { modelId?: string; auth?: boolean },
): Promise<T> {
  const headers =
    options?.auth === false
      ? jsonPublicHeaders()
      : await jsonDeviceHeaders(options?.modelId);
  const response = await fetchWithTimeout(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    if (response.status === 402) {
      refreshQuotaBar();
    }
    throw new Error(parseQuotaError(text, response.status) || `Request failed: ${response.status}`);
  }
  return parseResponseJson<T>(response);
}

export function fetchZiweiChart(body: ZiweiChartRequest): Promise<{ chart: ZiweiChart }> {
  return postJson("/ziwei/chart", body, { auth: false });
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
    { modelId: model },
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

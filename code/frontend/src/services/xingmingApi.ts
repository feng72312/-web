import type { XingmingChart, XingmingChartRequest, XingmingInterpretation } from "../types/xingming";
import type { ZiweiChart } from "../types/ziwei";
import type { PaipanResponse } from "../types/bazi";
import { API_BASE } from "./config";
import { jsonDeviceHeaders, parseQuotaError } from "./deviceHeaders";
import { postInterpretJson } from "./interpretHttp";
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

export function fetchXingmingChart(body: XingmingChartRequest): Promise<{ chart: XingmingChart }> {
  return postJson("/xingming/chart", body);
}

export async function fetchXingmingInterpret(
  chart: XingmingChart,
  excerpts?: XingmingInterpretation["excerpts"],
  model?: string,
  style?: InterpretStyle,
  question?: string,
  crossCharts?: { baziChart?: PaipanResponse["chart"]; ziweiChart?: ZiweiChart },
): Promise<{ chart: XingmingChart; interpretation: XingmingInterpretation }> {
  const result = await postInterpretJson<{ chart: XingmingChart; interpretation: XingmingInterpretation }>(
    "/xingming/interpret",
    { chart, excerpts, model, style, question, crossCharts },
    { modelId: model },
  );
  refreshQuotaBar();
  return result;
}

export function initXingmingChatSession(
  chart: XingmingChart,
  excerpts?: XingmingInterpretation["excerpts"],
  knowledgeHits?: XingmingInterpretation["knowledgeHits"],
  cases?: XingmingInterpretation["cases"],
  crossCharts?: { baziChart?: PaipanResponse["chart"]; ziweiChart?: ZiweiChart },
): Promise<{ agentId: string }> {
  return postJson("/xingming/chat/init", { chart, excerpts, knowledgeHits, cases, crossCharts });
}

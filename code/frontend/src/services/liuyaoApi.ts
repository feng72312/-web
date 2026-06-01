import type {
  LiuyaoChart,
  LiuyaoDivineRequest,
  LiuyaoInterpretation,
  YongShenResult,
} from "../types/liuyao";
import { API_BASE } from "./config";
import { jsonDeviceHeaders, parseQuotaError } from "./deviceHeaders";
import type { InterpretStyle } from "../utils/interpretStyle";
import { refreshQuotaBar } from "../utils/quotaEvents";

async function postJson<T>(path: string, body: unknown, modelId?: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: jsonDeviceHeaders(modelId),
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

export function fetchLiuyaoDivine(
  body: LiuyaoDivineRequest,
): Promise<{ chart: LiuyaoChart }> {
  return postJson("/liuyao/divine", body);
}

export function fetchInferYongShen(
  chart: LiuyaoChart,
  question: string,
  model?: string,
): Promise<YongShenResult> {
  return postJson("/liuyao/infer-yong-shen", { chart, question, model });
}

export function overrideYongShen(
  chart: LiuyaoChart,
  yongShen: string,
  position?: number,
): Promise<YongShenResult> {
  return postJson("/liuyao/yong-shen", { chart, yongShen, position });
}

export function fetchLiuyaoRagSearch(
  chart: LiuyaoChart,
  yongShen: YongShenResult,
  question?: string,
): Promise<{ query: string; excerpts: LiuyaoInterpretation["excerpts"] }> {
  return postJson("/liuyao/rag/search", { chart, yongShen, question });
}

export async function fetchLiuyaoInterpret(
  chart: LiuyaoChart,
  yongShen?: YongShenResult,
  excerpts?: LiuyaoInterpretation["excerpts"],
  model?: string,
  style?: InterpretStyle,
): Promise<{ chart: LiuyaoChart; interpretation: LiuyaoInterpretation }> {
  const result = await postJson<{ chart: LiuyaoChart; interpretation: LiuyaoInterpretation }>(
    "/liuyao/interpret",
    {
      chart,
      yongShen,
      excerpts,
      model,
      style,
    },
    model,
  );
  refreshQuotaBar();
  return result;
}

export function initLiuyaoChatSession(
  chart: LiuyaoChart,
  yongShen: YongShenResult,
  excerpts?: LiuyaoInterpretation["excerpts"],
): Promise<{ agentId: string }> {
  return postJson("/liuyao/chat/init", { chart, yongShen, excerpts });
}

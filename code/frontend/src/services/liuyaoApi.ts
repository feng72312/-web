import type {
  LiuyaoChart,
  LiuyaoDivineRequest,
  LiuyaoInterpretation,
  YongShenResult,
} from "../types/liuyao";
import { API_BASE } from "./config";

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
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

export function fetchLiuyaoInterpret(
  chart: LiuyaoChart,
  yongShen?: YongShenResult,
  excerpts?: LiuyaoInterpretation["excerpts"],
  model?: string,
): Promise<{ chart: LiuyaoChart; interpretation: LiuyaoInterpretation }> {
  return postJson("/liuyao/interpret", {
    chart,
    yongShen,
    excerpts,
    model,
  });
}

export function initLiuyaoChatSession(
  chart: LiuyaoChart,
  yongShen: YongShenResult,
  excerpts?: LiuyaoInterpretation["excerpts"],
): Promise<{ agentId: string }> {
  return postJson("/liuyao/chat/init", { chart, yongShen, excerpts });
}

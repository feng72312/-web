import type {
  HepanChartRequest,
  HepanChartResponse,
  HepanInterpretation,
  HepanSceneOption,
} from "../types/hepan";
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

export async function fetchHepanScenes(): Promise<{ scenes: HepanSceneOption[] }> {
  const response = await fetch(`${API_BASE}/hepan/scenes`);
  if (!response.ok) {
    throw new Error("Failed to load hepan scenes");
  }
  return response.json() as Promise<{ scenes: HepanSceneOption[] }>;
}

export function fetchHepanChart(body: HepanChartRequest): Promise<HepanChartResponse> {
  return postJson<HepanChartResponse>("/hepan/chart", body);
}

export async function fetchHepanInterpret(
  hepan: HepanChartResponse,
  options?: {
    question?: string;
    excerpts?: HepanInterpretation["excerpts"];
    model?: string;
    style?: InterpretStyle;
  },
): Promise<{ hepan: HepanChartResponse; interpretation: HepanInterpretation }> {
  const result = await postJson<{ hepan: HepanChartResponse; interpretation: HepanInterpretation }>(
    "/hepan/interpret",
    {
      hepan,
      question: options?.question,
      excerpts: options?.excerpts,
      model: options?.model,
      style: options?.style,
    },
    options?.model,
  );
  refreshQuotaBar();
  return result;
}

export function initHepanChatSession(
  hepan: HepanChartResponse,
  excerpts?: HepanInterpretation["excerpts"],
): Promise<{ agentId: string }> {
  return postJson("/hepan/chat/init", { hepan, excerpts });
}

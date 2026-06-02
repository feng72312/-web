import type {
  BirthProfileSummary,
  QimenChart,
  QimenChartRequest,
  QimenInterpretation,
} from "../types/qimen";
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

export function fetchQimenChart(
  body: QimenChartRequest,
): Promise<{ chart: QimenChart }> {
  return postJson("/qimen/chart", body);
}

export function fetchQimenRagSearch(
  chart: QimenChart,
  question?: string,
): Promise<{ query: string; excerpts: QimenInterpretation["excerpts"] }> {
  return postJson("/qimen/rag/search", { chart, question });
}

export async function fetchQimenInterpret(
  chart: QimenChart,
  excerpts?: QimenInterpretation["excerpts"],
  model?: string,
  birthProfile?: BirthProfileSummary | null,
  style?: InterpretStyle,
): Promise<{ chart: QimenChart; interpretation: QimenInterpretation }> {
  const result = await postJson<{ chart: QimenChart; interpretation: QimenInterpretation }>(
    "/qimen/interpret",
    { chart, excerpts, model, birthProfile, style },
    model,
  );
  refreshQuotaBar();
  return result;
}

export function initQimenChatSession(
  chart: QimenChart,
  excerpts?: QimenInterpretation["excerpts"],
  knowledgeHits?: QimenInterpretation["knowledgeHits"],
  birthProfile?: BirthProfileSummary | null,
): Promise<{ agentId: string }> {
  return postJson("/qimen/chat/init", {
    chart,
    excerpts,
    knowledgeHits,
    birthProfile,
  });
}

export function fetchQimenMethods(): Promise<{
  methods: Array<{ id: string; label: string; implemented: boolean }>;
}> {
  return fetch(`${API_BASE}/qimen/methods`).then((r) => {
    if (!r.ok) throw new Error(`methods failed: ${r.status}`);
    return r.json();
  });
}

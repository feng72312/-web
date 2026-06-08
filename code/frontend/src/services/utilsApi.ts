import type {
  JiemengSearchResult,
  UtilsInterpretation,
  ZhugeDivineResult,
} from "../types/utils";
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

export function fetchZhugeDivine(
  chars: string,
  strokes?: number[],
  question?: string,
): Promise<ZhugeDivineResult> {
  return postJson<ZhugeDivineResult>("/utils/zhuge/divine", { chars, strokes, question });
}

export function fetchJiemengSearch(dream: string, limit = 8): Promise<JiemengSearchResult> {
  return postJson<JiemengSearchResult>("/utils/jiemeng/search", { dream, limit });
}

export function fetchNamingAnalyze(body: {
  surname: string;
  givenName?: string;
  strokeOverrides?: Record<string, number>;
  birth?: import("../types/naming").NamingBirthInput | null;
}): Promise<{ analysis: import("../types/naming").NamingAnalysis }> {
  return postJson("/utils/naming/analyze", body);
}

export function fetchNamingLookup(chars: string): Promise<{
  chars: string;
  entries: import("../types/naming").NamingShuowenEntry[];
}> {
  return postJson("/utils/naming/lookup", { chars });
}

export function fetchUtilsInterpret(
  tool: "zhuge" | "jiemeng" | "cewen" | "naming",
  payload: Record<string, unknown>,
  options?: {
    question?: string;
    excerpts?: UtilsInterpretation["excerpts"];
    model?: string;
    style?: InterpretStyle;
  },
): Promise<{ interpretation: UtilsInterpretation }> {
  return postJson("/utils/interpret", {
    tool,
    payload,
    question: options?.question,
    excerpts: options?.excerpts,
    model: options?.model,
    style: options?.style,
  }, options?.model).then((result) => {
    refreshQuotaBar();
    return result;
  });
}

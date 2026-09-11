import type {
  InterpretResponse,
  LiuriDay,
  PaipanRequest,
  PaipanResponse,
} from "../types/bazi";
import type { InterpretStyle } from "../utils/interpretStyle";
import { API_BASE } from "./config";
import { withAccessCodeRetry } from "./accessRetry";
import { jsonDeviceHeaders, jsonPublicHeaders, parseApiErrorMessage, parseQuotaError, throwIfAccessCodeRequired } from "./deviceHeaders";
import { fetchWithTimeout, INTERPRET_TIMEOUT_MS, parseResponseJson } from "./httpJson";
import { postInterpretJson } from "./interpretHttp";
import { refreshQuotaBar } from "../utils/quotaEvents";
import { readSseStream } from "./sse";

export class HttpStatusError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "HttpStatusError";
    this.status = status;
  }
}

async function postJsonOnce<T>(
  path: string,
  body: unknown,
  options?: { modelId?: string; auth?: boolean; timeoutMs?: number },
): Promise<T> {
  const headers =
    options?.auth === false
      ? jsonPublicHeaders()
      : await jsonDeviceHeaders(options?.modelId);
  const response = await fetchWithTimeout(
    `${API_BASE}${path}`,
    {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    },
    options?.timeoutMs,
  );
  if (!response.ok) {
    const text = await response.text();
    throwIfAccessCodeRequired(text, response.status);
    throw new Error(parseQuotaError(text, response.status) || `Request failed: ${response.status}`);
  }
  return parseResponseJson<T>(response);
}

async function postJson<T>(
  path: string,
  body: unknown,
  options?: { modelId?: string; auth?: boolean; timeoutMs?: number },
): Promise<T> {
  return withAccessCodeRetry(() => postJsonOnce<T>(path, body, options));
}

export function fetchPaipan(body: PaipanRequest): Promise<PaipanResponse> {
  return postJson<PaipanResponse>("/paipan", body, { auth: false });
}

export function fetchPaipanJudgement(
  body: PaipanRequest & { question?: string },
): Promise<{ chart: PaipanResponse["chart"]; sections: PaipanResponse["sections"]; judgement: import("../types/bazi").BaziJudgementReport }> {
  return postJson("/paipan/judgement", body, { auth: false });
}

export function fetchLuckTimeline(
  body: PaipanRequest,
): Promise<{ luckTimeline: NonNullable<PaipanResponse["chart"]["luckTimeline"]> }> {
  return postJson("/paipan/luck-timeline", body, { auth: false });
}

export interface RagSearchResult {
  query: string;
  excerpts: InterpretResponse["interpretation"]["excerpts"];
}

export function fetchRagSearch(body: PaipanRequest): Promise<RagSearchResult> {
  return postJson<RagSearchResult>("/rag/search", body);
}

export async function fetchInterpret(
  body: PaipanRequest,
  options?: {
    excerpts?: InterpretResponse["interpretation"]["excerpts"];
    question?: string;
    model?: string;
    style?: InterpretStyle;
    fusionMode?: "bazi_liuyao" | "bazi_ziwei" | "triple";
    fusion?: boolean;
  },
): Promise<InterpretResponse> {
  const useFusion = options?.fusion === true && Boolean(options?.fusionMode);
  const payload = {
    ...body,
    fusion: useFusion,
    ...(useFusion ? { fusionMode: options?.fusionMode } : {}),
    ...(options?.excerpts ? { excerpts: options.excerpts } : {}),
    ...(options?.question ? { question: options.question } : {}),
    ...(options?.model ? { model: options.model } : {}),
    ...(options?.style ? { style: options.style } : {}),
  };
  const result = await postInterpretJson<InterpretResponse>("/interpret", payload, {
    modelId: options?.model,
    timeoutMs: INTERPRET_TIMEOUT_MS,
  });
  refreshQuotaBar();
  return result;
}

export function fetchInterpretStream(
  body: PaipanRequest,
  options: {
    excerpts?: InterpretResponse["interpretation"]["excerpts"];
    question?: string;
    model?: string;
    style?: InterpretStyle;
  } | undefined,
  handlers: {
    onStage: (text: string) => void;
    onDelta: (text: string) => void;
    onDone: (result: InterpretResponse) => void;
    onError: (msg: string, status?: number) => void;
  },
): AbortController {
  const controller = new AbortController();
  const payload = {
    ...body,
    fusion: false,
    ...(options?.excerpts ? { excerpts: options.excerpts } : {}),
    ...(options?.question ? { question: options.question } : {}),
    ...(options?.model ? { model: options.model } : {}),
    ...(options?.style ? { style: options.style } : {}),
  };

  void (async () => {
    try {
      await withAccessCodeRetry(async () => {
        const response = await fetch(`${API_BASE}/interpret/stream`, {
          method: "POST",
          headers: await jsonDeviceHeaders(options?.model),
          body: JSON.stringify(payload),
          signal: controller.signal,
        });
        if (!response.ok) {
          const text = await response.text();
          throwIfAccessCodeRequired(text, response.status);
          throw new HttpStatusError(
            response.status,
            parseApiErrorMessage(text, response.status),
          );
        }
        await readSseStream<{
          type: string;
          text?: string;
          message?: string;
          chart?: InterpretResponse["chart"];
          sections?: InterpretResponse["sections"];
          modules?: InterpretResponse["modules"];
          interpretation?: InterpretResponse["interpretation"];
        }>(response, (event) => {
          if (event.type === "stage" && event.text) {
            handlers.onStage(event.text);
          } else if (event.type === "delta" && event.text) {
            handlers.onDelta(event.text);
          } else if (event.type === "done" && event.interpretation) {
            refreshQuotaBar();
            handlers.onDone({
              chart: event.chart as InterpretResponse["chart"],
              sections: event.sections ?? [],
              modules: event.modules ?? [],
              interpretation: event.interpretation,
            });
          } else if (event.type === "error") {
            handlers.onError(event.message ?? "stream error");
          }
        });
      });
    } catch (err) {
      if (controller.signal.aborted) {
        return;
      }
      if (err instanceof HttpStatusError) {
        handlers.onError(err.message, err.status);
        return;
      }
      handlers.onError(err instanceof Error ? err.message : "stream failed");
    }
  })();

  return controller;
}

export async function fetchLiuri(
  year: number,
  dayMaster: string,
  options?: {
    dayZhi?: string;
    yearGan?: string;
    yearZhi?: string;
    monthZhi?: string;
    gender?: number;
  },
): Promise<{ year: number; months: Record<string, LiuriDay[]> }> {
  const params = new URLSearchParams({ dayMaster });
  if (options?.dayZhi) params.set("dayZhi", options.dayZhi);
  if (options?.yearGan) params.set("yearGan", options.yearGan);
  if (options?.yearZhi) params.set("yearZhi", options.yearZhi);
  if (options?.monthZhi) params.set("monthZhi", options.monthZhi);
  if (options?.gender !== undefined) params.set("gender", String(options.gender));
  const response = await fetch(`${API_BASE}/liuri/${year}?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

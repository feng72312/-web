import type { ChatMessage, ChatStatus } from "../types/bazi";
import { API_BASE } from "./config";
import { jsonDeviceHeaders, parseApiErrorMessage, parseQuotaError } from "./deviceHeaders";
import { refreshQuotaBar } from "../utils/quotaEvents";
const CHAT_INIT_TIMEOUT_MS = 120_000;

function networkErrorMessage(path: string, err: unknown): string {
  if (err instanceof Error && err.name === "AbortError") {
    return `请求超时 (${path}), 请稍后重试或检查 Cursor 服务`;
  }
  if (err instanceof TypeError) {
    return (
      `无法连接后端 (${path}). 请确认后端已启动并已重启加载最新代码, ` +
      `且前端通过 http://127.0.0.1:5173 访问`
    );
  }
  return err instanceof Error ? err.message : "请求失败";
}

async function postJsonWithTimeout<T>(
  path: string,
  body: unknown,
  timeoutMs: number,
): Promise<T> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!response.ok) {
      const text = await response.text();
      if (response.status === 404 && path.includes("/chat/init")) {
        throw new Error(
          "后端缺少 /chat/init 接口, 请重启后端 (关闭旧窗口后重新运行 start-all.bat)",
        );
      }
      throw new Error(text || `Request failed: ${response.status}`);
    }
    return response.json() as Promise<T>;
  } catch (err) {
    throw new Error(networkErrorMessage(path, err));
  } finally {
    window.clearTimeout(timer);
  }
}

export async function fetchChatStatus(): Promise<ChatStatus> {
  const response = await fetch(`${API_BASE}/chat/status`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<ChatStatus>;
}

export interface ChatInterpretSeedInput {
  summaryPlain?: string;
  summaryProfessional?: string;
  model?: string;
}

export async function seedChatInterpretation(
  agentId: string,
  input: ChatInterpretSeedInput,
): Promise<{ agentId: string; added: number }> {
  const response = await fetch(`${API_BASE}/chat/seed-interpretation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      agentId,
      summaryPlain: input.summaryPlain,
      summaryProfessional: input.summaryProfessional,
      model: input.model,
    }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<{ agentId: string; added: number }>;
}

export async function fetchChatHistory(agentId: string): Promise<ChatMessage[]> {
  const response = await fetch(`${API_BASE}/chat/history/${encodeURIComponent(agentId)}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  const data = (await response.json()) as { messages: ChatMessage[] };
  return data.messages ?? [];
}

export async function initChatSession(
  chart: Record<string, unknown>,
  sections: Array<Record<string, unknown>>,
): Promise<string> {
  const data = await postJsonWithTimeout<{ agentId: string }>(
    "/chat/init",
    { chart, sections },
    CHAT_INIT_TIMEOUT_MS,
  );
  return data.agentId;
}

export type GeneralChatScenario =
  | "general"
  | "choose_method"
  | "prepare_question"
  | "explain_terms"
  | "review_result";

export interface GeneralChatSessionInit {
  agentId: string;
  title: string;
  scenario: GeneralChatScenario;
}

export interface InitGeneralChatOptions {
  scenario?: GeneralChatScenario;
  title?: string;
  initialPrompt?: string;
}

export async function initGeneralChatSession(
  options: InitGeneralChatOptions = {},
): Promise<GeneralChatSessionInit> {
  const data = await postJsonWithTimeout<GeneralChatSessionInit>(
    "/chat/init/general",
    {
      scenario: options.scenario ?? "general",
      title: options.title,
      initialPrompt: options.initialPrompt,
    },
    CHAT_INIT_TIMEOUT_MS,
  );
  return data;
}

export interface FusionChatInitInput {
  title?: string;
  sources: Array<{
    moduleId: string;
    moduleLabel: string;
    title: string;
    question?: string;
    chartSnapshot: Record<string, unknown>;
    summaryPlain?: string;
    summaryProfessional?: string;
    createdAt?: string;
  }>;
}

export interface FusionChatInitResponse {
  agentId: string;
  title: string;
  scenario: GeneralChatScenario;
  sourceCount: number;
}

export async function initFusionChatSession(
  input: FusionChatInitInput,
): Promise<FusionChatInitResponse> {
  return postJsonWithTimeout<FusionChatInitResponse>(
    "/chat/init/fusion",
    input,
    CHAT_INIT_TIMEOUT_MS,
  );
}

export async function sendChatMessage(agentId: string, message: string): Promise<string> {
  const response = await fetch(`${API_BASE}/chat/send`, {
    method: "POST",
    headers: await jsonDeviceHeaders(),
    body: JSON.stringify({ agentId, message }),
  });
  if (!response.ok) {
    const text = await response.text();
    if (response.status === 402) {
      refreshQuotaBar();
    }
    throw new Error(parseApiErrorMessage(text, response.status));
  }
  refreshQuotaBar();
  const data = (await response.json()) as { text: string };
  return data.text;
}

export function streamChatMessage(
  agentId: string,
  message: string,
  model: string,
  onDelta: (text: string) => void,
  onDone: (runId: string) => void,
  onError: (msg: string) => void,
  onAbort?: () => void,
): AbortController {
  const controller = new AbortController();

  void (async () => {
    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: await jsonDeviceHeaders(model),
        body: JSON.stringify({ agentId, message, model }),
        signal: controller.signal,
      });
      if (!response.ok) {
        const text = await response.text();
        if (response.status === 402) {
          refreshQuotaBar();
        }
        throw new Error(parseApiErrorMessage(text, response.status));
      }
      if (!response.body) {
        throw new Error("empty response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() ?? "";

        for (const part of parts) {
          const line = part
            .split("\n")
            .find((item) => item.startsWith("data: "));
          if (!line) {
            continue;
          }
          const payload = JSON.parse(line.slice(6)) as {
            type: string;
            text?: string;
            runId?: string;
            message?: string;
          };
          if (payload.type === "delta" && payload.text) {
            onDelta(payload.text);
          } else if (payload.type === "done" && payload.runId) {
            refreshQuotaBar();
            onDone(payload.runId);
          } else if (payload.type === "error") {
            onError(payload.message ?? "stream error");
          }
        }
      }
    } catch (err) {
      if (controller.signal.aborted) {
        onAbort?.();
        return;
      }
      onError(err instanceof Error ? err.message : "stream failed");
    }
  })();

  return controller;
}

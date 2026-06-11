import type { AiThreadMessage } from "./types";

const STORAGE_PREFIX = "ziyun_ai_chat_thread_v1:";
const MAX_MESSAGES = 80;

function storageKey(agentId: string): string {
  return `${STORAGE_PREFIX}${agentId}`;
}

function normalizeMessage(message: AiThreadMessage): AiThreadMessage | null {
  if (
    typeof message.id !== "string" ||
    (message.role !== "user" && message.role !== "assistant") ||
    typeof message.content !== "string"
  ) {
    return null;
  }
  return {
    id: message.id,
    role: message.role,
    content: message.content,
    status:
      message.role === "assistant"
        ? message.status === "running"
          ? "complete"
          : message.status
        : undefined,
    errorText: message.errorText,
  };
}

export function loadThreadMessages(agentId: string): AiThreadMessage[] {
  try {
    const raw = localStorage.getItem(storageKey(agentId));
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as AiThreadMessage[];
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed
      .map(normalizeMessage)
      .filter((item): item is AiThreadMessage => Boolean(item));
  } catch {
    return [];
  }
}

export function clearThreadMessages(agentId: string): void {
  try {
    localStorage.removeItem(storageKey(agentId));
  } catch {
    // ignore
  }
}

export function saveThreadMessages(
  agentId: string,
  messages: AiThreadMessage[],
): void {
  const normalized = messages
    .map(normalizeMessage)
    .filter((item): item is AiThreadMessage => Boolean(item))
    .slice(-MAX_MESSAGES);
  if (normalized.length === 0) {
    return;
  }
  localStorage.setItem(storageKey(agentId), JSON.stringify(normalized));
}

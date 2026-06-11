import type { AiChatSession } from "./types";

const STORAGE_KEY = "ziyun_ai_chat_sessions_v1";
const MAX_SESSIONS = 30;

export function loadRecentSessions(): AiChatSession[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as AiChatSession[];
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.filter(
      (item) =>
        typeof item.agentId === "string" &&
        typeof item.title === "string" &&
        typeof item.scenario === "string",
    );
  } catch {
    return [];
  }
}

export function saveRecentSessions(sessions: AiChatSession[]): void {
  const trimmed = sessions.slice(0, MAX_SESSIONS);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
}

export function upsertRecentSession(session: AiChatSession): AiChatSession[] {
  const existing = loadRecentSessions().filter(
    (item) => item.agentId !== session.agentId,
  );
  const next = [session, ...existing].slice(0, MAX_SESSIONS);
  saveRecentSessions(next);
  return next;
}

export function removeRecentSession(agentId: string): AiChatSession[] {
  const next = loadRecentSessions().filter((item) => item.agentId !== agentId);
  saveRecentSessions(next);
  return next;
}

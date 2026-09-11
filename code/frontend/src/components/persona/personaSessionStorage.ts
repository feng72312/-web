import type { PersonaChatSession } from "../../types/persona";

const STORAGE_KEY = "ziyun_persona_chat_sessions_v1";
const MAX_SESSIONS = 20;

export function loadPersonaSessions(): PersonaChatSession[] {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]") as unknown;
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.filter(
      (item): item is PersonaChatSession =>
        typeof item === "object" &&
        item !== null &&
        typeof (item as PersonaChatSession).agentId === "string" &&
        typeof (item as PersonaChatSession).personaId === "string" &&
        typeof (item as PersonaChatSession).title === "string",
    );
  } catch {
    return [];
  }
}

export function upsertPersonaSession(
  session: PersonaChatSession,
): PersonaChatSession[] {
  const next = [
    session,
    ...loadPersonaSessions().filter((item) => item.agentId !== session.agentId),
  ].slice(0, MAX_SESSIONS);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next;
}

export function removePersonaSession(agentId: string): PersonaChatSession[] {
  const next = loadPersonaSessions().filter((item) => item.agentId !== agentId);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next;
}

import { withAccessCodeRetry } from "./accessRetry";
import { API_BASE } from "./config";
import {
  jsonPublicHeaders,
  parseApiErrorMessage,
  throwIfAccessCodeRequired,
} from "./deviceHeaders";
import type {
  PersonaChatInitResponse,
  PersonaCatalogResponse,
  PersonaDetail,
} from "../types/persona";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throwIfAccessCodeRequired(text, response.status);
    throw new Error(parseApiErrorMessage(text, response.status));
  }
  return response.json() as Promise<T>;
}

export async function fetchPersonas(): Promise<PersonaCatalogResponse> {
  return withAccessCodeRetry(async () => {
    const data = await parseResponse<PersonaCatalogResponse>(
      await fetch(`${API_BASE}/personas?limit=200`),
    );
    return data;
  });
}

export async function fetchPersona(personaId: string): Promise<PersonaDetail> {
  return withAccessCodeRetry(() =>
    fetch(`${API_BASE}/personas/${encodeURIComponent(personaId)}`).then(
      parseResponse<PersonaDetail>,
    ),
  );
}

export async function initPersonaChatSession(input: {
  personaId: string;
  title?: string;
  initialPrompt?: string;
}): Promise<PersonaChatInitResponse> {
  return withAccessCodeRetry(() =>
    fetch(`${API_BASE}/chat/init/persona`, {
      method: "POST",
      headers: jsonPublicHeaders(),
      body: JSON.stringify(input),
    }).then(parseResponse<PersonaChatInitResponse>),
  );
}

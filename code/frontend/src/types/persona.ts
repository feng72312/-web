export interface PersonaLicense {
  name: string;
  attribution: string;
  sourceUrl: string;
}

export interface PersonaUpstream {
  name: string;
  url: string;
  owner: string;
  commit: string;
}

export type PersonaInteractionMode = "historical_simulation" | "public_framework";
export type PersonaAvailability = "ready" | "review_required" | "unavailable";

export interface PersonaCategory {
  id: string;
  label: string;
  order: number;
  count: number;
  readyCount: number;
}

export interface PersonaSummary {
  id: string;
  name: string;
  formalName: string;
  era: string;
  lifespan: string;
  version: string;
  summary: string;
  disclosure: string;
  sealCharacter: string;
  themes: string[];
  suitableFor: string[];
  categoryId: string;
  categoryLabel: string;
  lifeStatus: "historical" | "living" | "unknown";
  interactionMode: PersonaInteractionMode;
  availability: PersonaAvailability;
  availabilityReason: string;
  upstream: PersonaUpstream;
  license: PersonaLicense;
}

export interface PersonaSource {
  id: string;
  title: string;
  kind: "primary" | "research" | "upstream" | "critical";
  note: string;
  citation?: string | null;
  url?: string | null;
}

export interface PersonaStarter {
  label: string;
  prompt: string;
  theme: string;
}

export interface PersonaDetail extends PersonaSummary {
  notSuitableFor: string[];
  sources: PersonaSource[];
  starters: PersonaStarter[];
}

export interface PersonaChatSession {
  agentId: string;
  personaId: string;
  personaName: string;
  title: string;
  disclosure: string;
  interactionMode?: PersonaInteractionMode;
  createdAt: string;
}

export interface PersonaChatInitResponse {
  agentId: string;
  personaId: string;
  title: string;
  disclosure: string;
  interactionMode: PersonaInteractionMode;
}

export interface PersonaCatalogResponse {
  personas: PersonaSummary[];
  categories: PersonaCategory[];
  total: number;
  offset: number;
  limit: number;
  sourceCommit: string;
}

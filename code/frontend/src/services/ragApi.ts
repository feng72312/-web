import { API_BASE } from "./config";

export interface RagStatus {
  provider: string;
  httpUrl: string;
  serviceOk: boolean;
  serviceMessage: string;
  chunks: number;
  filesTotal?: number;
  chunksTotal?: number;
  builtAt?: string | null;
}

export async function fetchRagStatus(): Promise<RagStatus> {
  const response = await fetch(`${API_BASE}/rag/status`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<RagStatus>;
}

export function isStubExcerpt(
  excerpts: Array<{ source?: string; excerpt?: string }>,
): boolean {
  return (
    excerpts.length === 1 &&
    excerpts[0]?.source === "stub"
  );
}

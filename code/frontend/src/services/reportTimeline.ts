import type { UnifiedInterpretation } from "../types/consensus";

export interface TimelineEntry {
  id: string;
  moduleId: string;
  moduleLabel: string;
  question: string;
  summary: string;
  createdAt: string;
  confidenceBand?: string;
  profileId?: string;
}

const STORAGE_KEY = "shushu_report_timeline_v1";

function readAll(): TimelineEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as TimelineEntry[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeAll(entries: TimelineEntry[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

export function listTimelineEntries(profileId?: string): TimelineEntry[] {
  const all = readAll().sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  if (!profileId) {
    return all;
  }
  return all.filter((e) => e.profileId === profileId);
}

export function appendTimelineEntry(input: {
  moduleId: string;
  moduleLabel: string;
  question: string;
  interpretation: UnifiedInterpretation;
  profileId?: string;
}): TimelineEntry {
  const entry: TimelineEntry = {
    id: crypto.randomUUID(),
    moduleId: input.moduleId,
    moduleLabel: input.moduleLabel,
    question: input.question,
    summary:
      input.interpretation.summaryPlain ||
      input.interpretation.summaryProfessional ||
      input.interpretation.summary ||
      "",
    createdAt: new Date().toISOString(),
    confidenceBand: input.interpretation.confidenceBand,
    profileId: input.profileId,
  };
  writeAll([entry, ...readAll()]);
  return entry;
}

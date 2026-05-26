import type { BirthFormState, PaipanRequest, SavedProfile } from "../types/bazi";
import { hourFromSlot } from "../utils/timeSlots";

const STORAGE_KEY = "bazi_birth_profiles_v1";

function readAll(): SavedProfile[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as SavedProfile[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeAll(profiles: SavedProfile[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profiles));
}

export function listProfiles(): SavedProfile[] {
  return readAll().sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

export function saveProfile(form: BirthFormState): SavedProfile {
  const now = new Date().toISOString();
  const profiles = readAll();
  const existing = form.activeProfileId
    ? profiles.find((item) => item.id === form.activeProfileId)
    : undefined;

  const profile: SavedProfile = {
    id: existing?.id || crypto.randomUUID(),
    name: form.name.trim(),
    calendarType: form.calendarType,
    year: form.year,
    month: form.month,
    day: form.day,
    isLeapMonth: form.isLeapMonth,
    hourSlot: form.hourSlot,
    minute: form.minute,
    gender: form.gender,
    createdAt: existing?.createdAt || now,
    updatedAt: now,
  };

  const next = existing
    ? profiles.map((item) => (item.id === profile.id ? profile : item))
    : [profile, ...profiles];

  writeAll(next);
  return profile;
}

export function deleteProfile(profileId: string): void {
  writeAll(readAll().filter((item) => item.id !== profileId));
}

export function profileToFormState(profile: SavedProfile): BirthFormState {
  return {
    activeProfileId: profile.id,
    name: profile.name,
    calendarType: profile.calendarType,
    year: profile.year,
    month: profile.month,
    day: profile.day,
    isLeapMonth: profile.isLeapMonth,
    hourSlot: profile.hourSlot,
    minute: profile.minute,
    gender: profile.gender,
  };
}

export function defaultFormState(): BirthFormState {
  return {
    activeProfileId: null,
    name: "",
    calendarType: "solar",
    year: 1990,
    month: 5,
    day: 15,
    isLeapMonth: false,
    hourSlot: 7,
    minute: 30,
    gender: 1,
  };
}

export function formToPaipanRequest(form: BirthFormState): PaipanRequest {
  return {
    name: form.name.trim(),
    calendarType: form.calendarType,
    year: form.year,
    month: form.month,
    day: form.day,
    isLeapMonth: form.isLeapMonth,
    hour: hourFromSlot(form.hourSlot),
    minute: form.minute,
    gender: form.gender,
  };
}

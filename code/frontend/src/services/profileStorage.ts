import type {
  BirthFormState,
  PaipanRequest,
  SavedProfile,
  ZiweiProfileSettings,
} from "../types/bazi";
import { hourFromSlot, slotFromHour, type ZiHourPhase } from "../utils/timeSlots";

const STORAGE_KEY = "bazi_birth_profiles_v1";

export const DEFAULT_ZIWEI_SETTINGS = {
  useTrueSolarTime: true,
  longitude: 120,
  leapMonthRule: "next_month",
  ziHourRule: "combined",
  mutagenTable: "nan_pai",
  chartSchool: "sanhe",
} satisfies Required<ZiweiProfileSettings>;

export function profileToZiweiSettings(profile: SavedProfile): ZiweiProfileSettings {
  return { ...DEFAULT_ZIWEI_SETTINGS, ...(profile.ziweiSettings ?? {}) };
}

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

function formToProfileFields(form: BirthFormState) {
  return {
    name: form.name.trim(),
    calendarType: form.calendarType,
    year: form.year,
    month: form.month,
    day: form.day,
    isLeapMonth: form.isLeapMonth,
    hourSlot: form.hourSlot,
    ziHourPhase: form.ziHourPhase,
    minute: form.minute,
    gender: form.gender,
  };
}

/** Always append a new profile (multiple saves supported). */
export function saveNewProfile(form: BirthFormState): SavedProfile {
  const now = new Date().toISOString();
  const profile: SavedProfile = {
    id: crypto.randomUUID(),
    ...formToProfileFields(form),
    createdAt: now,
    updatedAt: now,
  };
  writeAll([profile, ...readAll()]);
  return profile;
}

/** Update the currently selected profile in the list. */
export function updateProfile(form: BirthFormState): SavedProfile | null {
  if (!form.activeProfileId) {
    return null;
  }
  const now = new Date().toISOString();
  const profiles = readAll();
  const existing = profiles.find((item) => item.id === form.activeProfileId);
  if (!existing) {
    return null;
  }

  const profile: SavedProfile = {
    id: existing.id,
    ...formToProfileFields(form),
    baziSettings: existing.baziSettings,
    ziweiSettings: existing.ziweiSettings,
    createdAt: existing.createdAt,
    updatedAt: now,
  };

  writeAll(profiles.map((item) => (item.id === profile.id ? profile : item)));
  return profile;
}

/** @deprecated Use saveNewProfile or updateProfile */
export function saveProfile(form: BirthFormState): SavedProfile {
  return updateProfile(form) ?? saveNewProfile(form);
}

export function updateProfileZiweiSettings(
  profileId: string,
  ziweiSettings: ZiweiProfileSettings,
): SavedProfile | null {
  const profiles = readAll();
  const existing = profiles.find((item) => item.id === profileId);
  if (!existing) {
    return null;
  }
  const profile: SavedProfile = {
    ...existing,
    ziweiSettings,
    updatedAt: new Date().toISOString(),
  };
  writeAll(profiles.map((item) => (item.id === profile.id ? profile : item)));
  return profile;
}

export function deleteProfile(profileId: string): void {
  writeAll(readAll().filter((item) => item.id !== profileId));
}

export function profileToFormState(profile: SavedProfile): BirthFormState {
  const hourSlot =
    typeof profile.hourSlot === "number" && profile.hourSlot >= 0 && profile.hourSlot <= 11
      ? profile.hourSlot
      : 7;
  const ziHourPhase: ZiHourPhase =
    profile.ziHourPhase === "early" || profile.ziHourPhase === "late"
      ? profile.ziHourPhase
      : hourSlot === 0
        ? "early"
        : "late";
  return {
    activeProfileId: profile.id,
    name: profile.name ?? "",
    calendarType: profile.calendarType === "lunar" ? "lunar" : "solar",
    year: Number(profile.year) || 1990,
    month: Number(profile.month) || 1,
    day: Number(profile.day) || 1,
    isLeapMonth: Boolean(profile.isLeapMonth),
    hourSlot,
    ziHourPhase,
    minute: Number(profile.minute) || 0,
    gender: profile.gender === 0 ? 0 : 1,
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
    ziHourPhase: "late",
    minute: 30,
    gender: 1,
  };
}

export function paipanRequestToFormState(
  request: PaipanRequest,
  activeProfileId: string | null = null,
): BirthFormState {
  const { slotIndex, ziHourPhase } = slotFromHour(Number(request.hour) || 0);
  return {
    activeProfileId,
    name: request.name ?? "",
    calendarType: request.calendarType === "lunar" ? "lunar" : "solar",
    year: Number(request.year) || 1990,
    month: Number(request.month) || 1,
    day: Number(request.day) || 1,
    isLeapMonth: Boolean(request.isLeapMonth),
    hourSlot: slotIndex,
    ziHourPhase,
    minute: Number(request.minute) || 0,
    gender: request.gender === 0 ? 0 : 1,
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
    hour: hourFromSlot(form.hourSlot, form.ziHourPhase),
    minute: form.minute,
    gender: form.gender,
  };
}

const STORAGE_KEY = "bazi_visitor_id_v1";

function randomId(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `v-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
}

export function getVisitorId(): string {
  try {
    let existing = localStorage.getItem(STORAGE_KEY);
    if (!existing || existing.length < 8) {
      existing = sessionStorage.getItem(STORAGE_KEY);
    }
    if (existing && existing.length >= 8) {
      localStorage.setItem(STORAGE_KEY, existing);
      sessionStorage.setItem(STORAGE_KEY, existing);
      return existing;
    }
    const created = randomId();
    localStorage.setItem(STORAGE_KEY, created);
    sessionStorage.setItem(STORAGE_KEY, created);
    return created;
  } catch {
    return randomId();
  }
}

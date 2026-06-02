import type { QuotaStatus } from "../services/quotaApi";

/** True when anonymous visitor can use AI without logging in. */
export function hasFreeAiQuota(status: QuotaStatus): boolean {
  if (status.freeRemaining > 0) {
    return true;
  }
  return (status.tierQuotas ?? []).some((item) => item.remaining > 0);
}

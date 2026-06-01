export function refreshQuotaBar(): void {
  window.dispatchEvent(new CustomEvent("quota-refresh"));
}

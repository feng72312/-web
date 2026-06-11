export function formatTime(ts: number | null | undefined): string {
  if (!ts) {
    return "-";
  }
  return new Date(ts * 1000).toLocaleString("zh-CN", { hour12: false });
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null) {
    return "-";
  }
  return value.toLocaleString("zh-CN");
}

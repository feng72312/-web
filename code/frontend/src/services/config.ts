export const PRODUCTION_API_BASE =
  "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/api/v1";

/** Local dev routes through Vite proxy to http://127.0.0.1:8002 (see vite.config.ts). */
export const LOCAL_DEV_API_BASE = "/api/v1";

function isLocalDevHost(hostname: string): boolean {
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    return true;
  }
  const parts = hostname.split(".");
  if (parts.length !== 4) {
    return false;
  }
  const octets = parts.map((part) => Number(part));
  if (octets.some((n) => !Number.isInteger(n) || n < 0 || n > 255)) {
    return false;
  }
  const [a, b] = octets;
  if (a === 10) {
    return true;
  }
  if (a === 192 && b === 168) {
    return true;
  }
  if (a === 172 && b >= 16 && b <= 31) {
    return true;
  }
  return false;
}

function resolveApiBase(): string {
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host.endsWith(".tcloudbaseapp.com") || host.endsWith(".tcloudbase.com")) {
      return PRODUCTION_API_BASE;
    }
    if (isLocalDevHost(host)) {
      return LOCAL_DEV_API_BASE;
    }
  }
  const raw = import.meta.env.VITE_API_BASE as string | undefined;
  if (raw && raw.trim()) {
    return raw.replace(/\/$/, "");
  }
  return LOCAL_DEV_API_BASE;
}

export const API_BASE = resolveApiBase();

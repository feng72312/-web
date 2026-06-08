export const PRODUCTION_API_BASE =
  "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/api/v1";

/** Local backend with utils routes (start-backend.bat uses API_PORT=8001). */
export const LOCAL_DEV_API_BASE = "http://127.0.0.1:8001/api/v1";

function isLocalDevHost(hostname: string): boolean {
  return hostname === "localhost" || hostname === "127.0.0.1";
}

function resolveApiBase(): string {
  const raw = import.meta.env.VITE_API_BASE as string | undefined;
  if (raw && raw.trim()) {
    return raw.replace(/\/$/, "");
  }
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (isLocalDevHost(host)) {
      return LOCAL_DEV_API_BASE;
    }
    if (host.endsWith(".tcloudbaseapp.com") || host.endsWith(".tcloudbase.com")) {
      return PRODUCTION_API_BASE;
    }
  }
  return PRODUCTION_API_BASE;
}

export const API_BASE = resolveApiBase();

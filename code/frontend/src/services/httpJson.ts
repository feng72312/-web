const LOCAL_BACKEND_HINT =
  "无法连接本地后端, 请先在 code 目录运行 start-backend.bat (端口 8002).";

export function isLocalDevHost(): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  const host = window.location.hostname;
  return host === "localhost" || host === "127.0.0.1";
}

function wrapFetchError(err: unknown): Error {
  if (err instanceof DOMException && err.name === "AbortError") {
    return new Error(
      isLocalDevHost()
        ? `请求超时 (20秒). ${LOCAL_BACKEND_HINT}`
        : "请求超时, 请稍后重试.",
    );
  }
  if (err instanceof TypeError) {
    return new Error(isLocalDevHost() ? LOCAL_BACKEND_HINT : "网络请求失败, 请检查网络后重试.");
  }
  if (err instanceof Error) {
    return err;
  }
  return new Error("请求失败");
}

export async function fetchWithTimeout(
  input: RequestInfo | URL,
  init?: RequestInit,
  timeoutMs = 20000,
): Promise<Response> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(input, { ...init, signal: controller.signal });
  } catch (err) {
    throw wrapFetchError(err);
  } finally {
    window.clearTimeout(timer);
  }
}

export async function parseResponseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  const trimmed = text.trim();
  if (trimmed.startsWith("<")) {
    throw new Error(
      isLocalDevHost()
        ? `后端返回了网页而非数据. ${LOCAL_BACKEND_HINT}`
        : "后端返回了网页而非数据, 请按 Ctrl+F5 强刷页面后重试",
    );
  }
  try {
    return JSON.parse(text) as T;
  } catch {
    if (!response.ok && isLocalDevHost()) {
      throw new Error(
        response.status === 502 || response.status === 504
          ? LOCAL_BACKEND_HINT
          : trimmed.slice(0, 160) || "响应解析失败",
      );
    }
    throw new Error(trimmed.slice(0, 160) || "响应解析失败");
  }
}

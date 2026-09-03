import { API_BASE } from "./config";
import { withAccessCodeRetry } from "./accessRetry";
import { jsonDeviceHeaders, jsonPublicHeaders, parseApiErrorMessage, parseQuotaError, throwIfAccessCodeRequired } from "./deviceHeaders";
import { fetchWithTimeout, INTERPRET_TIMEOUT_MS, parseResponseJson } from "./httpJson";
import { notifyInterpretQueue, isInterpretQueuedBody } from "../utils/interpretQueue";
import { refreshQuotaBar } from "../utils/quotaEvents";

const QUEUE_RETRY_DELAY_MS = 4000;
const QUEUE_MAX_RETRIES = 30;
const QUEUE_HINT_DELAY_MS = 8000;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

export async function fetchInterpretJson<T>(
  url: string,
  init: RequestInit,
  timeoutMs = INTERPRET_TIMEOUT_MS,
): Promise<T> {
  let finished = false;
  const hintTimer = window.setTimeout(() => {
    if (!finished) {
      notifyInterpretQueue(true, "当前解读人数较多, 排队中, 请稍候...");
    }
  }, QUEUE_HINT_DELAY_MS);

  try {
    for (let attempt = 0; attempt <= QUEUE_MAX_RETRIES; attempt += 1) {
      const response = await fetchWithTimeout(url, init, timeoutMs);
      if (response.status === 503) {
        const text = await response.text();
        if (isInterpretQueuedBody(text)) {
          if (attempt >= QUEUE_MAX_RETRIES) {
            throw new Error("当前解读人数较多, 排队超时, 请稍后重试");
          }
          const detail = parseApiErrorMessage(text, 503);
          notifyInterpretQueue(
            true,
            detail.includes("排队")
              ? `${detail}, 正在自动重试...`
              : "当前解读人数较多, 排队中, 正在自动重试...",
          );
          await sleep(QUEUE_RETRY_DELAY_MS);
          continue;
        }
        throw new Error(parseApiErrorMessage(text, 503));
      }
      if (response.status === 402) {
        refreshQuotaBar();
      }
      if (!response.ok) {
        const text = await response.text();
        throwIfAccessCodeRequired(text, response.status);
        throw new Error(parseQuotaError(text, response.status));
      }
      return parseResponseJson<T>(response);
    }
    throw new Error("当前解读人数较多, 排队超时, 请稍后重试");
  } finally {
    finished = true;
    window.clearTimeout(hintTimer);
    notifyInterpretQueue(false);
  }
}

export async function postInterpretJson<T>(
  path: string,
  body: unknown,
  options?: { modelId?: string; auth?: boolean; timeoutMs?: number },
): Promise<T> {
  const headers =
    options?.auth === false
      ? jsonPublicHeaders()
      : await jsonDeviceHeaders(options?.modelId);
  return withAccessCodeRetry(() =>
    fetchInterpretJson<T>(
      `${API_BASE}${path}`,
      {
        method: "POST",
        headers,
        body: JSON.stringify(body),
      },
      options?.timeoutMs ?? INTERPRET_TIMEOUT_MS,
    ),
  );
}

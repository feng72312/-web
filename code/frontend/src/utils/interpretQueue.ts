const INTERPRET_QUEUE_EVENT = "bazi-interpret-queue";

export type InterpretQueueDetail = {
  waiting: boolean;
  message?: string;
};

export function isInterpretQueuedBody(text: string): boolean {
  try {
    const data = JSON.parse(text) as { detail?: { code?: string } | string };
    if (typeof data.detail === "object" && data.detail?.code === "INTERPRET_QUEUED") {
      return true;
    }
  } catch {
    /* ignore */
  }
  return false;
}

export function notifyInterpretQueue(waiting: boolean, message?: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(
    new CustomEvent<InterpretQueueDetail>(INTERPRET_QUEUE_EVENT, {
      detail: { waiting, message },
    }),
  );
}

export function subscribeInterpretQueue(
  listener: (detail: InterpretQueueDetail) => void,
): () => void {
  if (typeof window === "undefined") {
    return () => undefined;
  }
  const handler = (event: Event) => {
    const custom = event as CustomEvent<InterpretQueueDetail>;
    listener(custom.detail ?? { waiting: false });
  };
  window.addEventListener(INTERPRET_QUEUE_EVENT, handler);
  return () => window.removeEventListener(INTERPRET_QUEUE_EVENT, handler);
}

import { useCallback, useRef, useState } from "react";

export type InterpretRunnerState = "idle" | "loading" | "streaming" | "done" | "error";

interface UseInterpretRunnerOptions<T> {
  run: (onDelta?: (text: string) => void) => Promise<T>;
  onSuccess?: (result: T) => void;
}

export function useInterpretRunner<T>({ run, onSuccess }: UseInterpretRunnerOptions<T>) {
  const [state, setState] = useState<InterpretRunnerState>("idle");
  const [streamText, setStreamText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef(false);

  const execute = useCallback(async () => {
    abortRef.current = false;
    setState("loading");
    setStreamText("");
    setError(null);
    try {
      const result = await run((delta) => {
        if (abortRef.current) {
          return;
        }
        setState("streaming");
        setStreamText((prev) => prev + delta);
      });
      if (!abortRef.current) {
        setState("done");
        onSuccess?.(result);
      }
      return result;
    } catch (err) {
      if (!abortRef.current) {
        setState("error");
        setError(err instanceof Error ? err.message : "解读失败");
      }
      throw err;
    }
  }, [run, onSuccess]);

  const reset = useCallback(() => {
    abortRef.current = true;
    setState("idle");
    setStreamText("");
    setError(null);
  }, []);

  return {
    state,
    streamText,
    error,
    isActive: state === "loading" || state === "streaming",
    execute,
    reset,
  };
}

import { useEffect, useRef, useState } from "react";
import { X } from "lucide-react";

const STORAGE_KEY = "zy_access_code";

type PromptState = {
  invalid: boolean;
  resolve: (value: string | null) => void;
};

let currentPrompt: PromptState | null = null;
let currentPromptPromise: Promise<string | null> | null = null;
const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((listener) => listener());
}

export function promptAccessCode(opts?: { invalid?: boolean }): Promise<string | null> {
  if (currentPrompt && currentPromptPromise) {
    if (opts?.invalid && !currentPrompt.invalid) {
      currentPrompt.invalid = true;
      notify();
    }
    return currentPromptPromise;
  }
  currentPromptPromise = new Promise((resolve) => {
    currentPrompt = { invalid: Boolean(opts?.invalid), resolve };
    notify();
  });
  return currentPromptPromise;
}

export function AccessCodeGate() {
  const [, setTick] = useState(0);
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const listener = () => setTick((n) => n + 1);
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }, []);

  const open = currentPrompt !== null;

  useEffect(() => {
    if (!open) {
      return;
    }
    inputRef.current?.focus();
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        finish(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open]);

  const finish = (next: string | null) => {
    const prompt = currentPrompt;
    currentPrompt = null;
    currentPromptPromise = null;
    setValue("");
    notify();
    prompt?.resolve(next);
  };

  const handleOk = () => {
    const code = value.trim();
    if (!code) {
      return;
    }
    window.localStorage.setItem(STORAGE_KEY, code);
    finish(code);
  };

  if (!open) {
    return null;
  }

  return (
    <div className="auth-modal-overlay access-code-overlay" onClick={() => finish(null)}>
      <div
        className="auth-modal access-code-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="access-code-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="auth-modal-header">
          <div>
            <p className="product-eyebrow">Private Preview</p>
            <h2 id="access-code-title">输入访问口令</h2>
          </div>
          <button
            type="button"
            className="auth-modal-close"
            onClick={() => finish(null)}
            aria-label="取消并关闭"
          >
            <X size={17} strokeWidth={1.8} aria-hidden="true" />
          </button>
        </div>
        <p className="auth-modal-hint">请输入站点访问口令，验证后会在当前设备中保留。</p>
        <div className="auth-form">
          <label>
            访问口令
            <input
              ref={inputRef}
              type="password"
              value={value}
              autoComplete="current-password"
              placeholder="请输入口令"
              aria-invalid={currentPrompt?.invalid || undefined}
              onChange={(event) => setValue(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleOk();
                }
              }}
            />
          </label>
          {currentPrompt?.invalid ? <p className="auth-message">口令不正确，请重试。</p> : null}
          <div className="auth-form-actions access-code-actions">
            <button type="button" className="secondary" onClick={() => finish(null)}>
              取消
            </button>
            <button type="button" className="primary-btn" disabled={!value.trim()} onClick={handleOk}>
              确认进入
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

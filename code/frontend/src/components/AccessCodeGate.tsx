import { useEffect, useState } from "react";
import { Modal } from "antd";

const STORAGE_KEY = "zy_access_code";

type PromptState = {
  invalid: boolean;
  resolve: (value: string | null) => void;
};

let currentPrompt: PromptState | null = null;
const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((listener) => listener());
}

export function promptAccessCode(opts?: { invalid?: boolean }): Promise<string | null> {
  return new Promise((resolve) => {
    currentPrompt = { invalid: Boolean(opts?.invalid), resolve };
    notify();
  });
}

export function AccessCodeGate() {
  const [, setTick] = useState(0);
  const [value, setValue] = useState("");

  useEffect(() => {
    const listener = () => setTick((n) => n + 1);
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }, []);

  const open = currentPrompt !== null;

  const finish = (next: string | null) => {
    const prompt = currentPrompt;
    currentPrompt = null;
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

  return (
    <Modal
      title="输入访问口令"
      open={open}
      okText="确认"
      cancelText="取消"
      onOk={handleOk}
      onCancel={() => finish(null)}
    >
      {currentPrompt?.invalid && <p>口令不正确</p>}
      <input
        className="text-input"
        type="text"
        value={value}
        placeholder="访问口令"
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            handleOk();
          }
        }}
      />
    </Modal>
  );
}

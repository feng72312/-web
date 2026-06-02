import { ModelSelector } from "./ModelSelector";
import type { ChatModelOption } from "../types/bazi";

interface InterpretModelPickerProps {
  models: ChatModelOption[];
  value: string;
  onChange: (modelId: string) => void;
  chatEnabled: boolean;
  disabled?: boolean;
}

export function InterpretModelPicker({
  models,
  value,
  onChange,
  chatEnabled,
  disabled = false,
}: InterpretModelPickerProps) {
  if (!chatEnabled) {
    const onCloud =
      typeof window !== "undefined" &&
      (window.location.hostname.endsWith(".tcloudbaseapp.com") ||
        window.location.hostname.endsWith(".tcloudbase.com"));
    const hint = onCloud
      ? "AI 状态暂不可用, 请强制刷新页面 (Ctrl+F5) 后重试; 若仍无效请联系管理员检查云托管 bazi-api 与 DeepSeek 配置."
      : "AI 未启用, 请在 backend/.env 配置 DeepSeek 或 Cursor API 后重启后端.";
    return <p className="action-hint">{hint}</p>;
  }

  if (models.length === 0) {
    return null;
  }

  return (
    <div className="interpret-model-row">
      <span className="field-label">AI 解读等级</span>
      <ModelSelector
        models={models}
        value={value}
        onChange={onChange}
        disabled={disabled}
      />
    </div>
  );
}

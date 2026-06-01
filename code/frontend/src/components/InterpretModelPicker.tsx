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
    return (
      <p className="action-hint">AI 未启用, 请在 backend/.env 配置 DeepSeek 或 Cursor API 后重启后端.</p>
    );
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

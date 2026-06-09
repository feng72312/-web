import type { TarotDrawMode } from "../../types/tarot";

interface Props {
  value: TarotDrawMode;
  onChange: (mode: TarotDrawMode) => void;
  disabled?: boolean;
}

const OPTIONS: { id: TarotDrawMode; label: string; hint: string }[] = [
  { id: "pick", label: "亲手抽牌", hint: "凭直觉从牌背中选择" },
  { id: "manual", label: "手动摆牌", hint: "录入实体牌结果" },
  { id: "auto", label: "快速随机", hint: "一键洗牌抽牌" },
];

export function DrawModePicker({ value, onChange, disabled }: Props) {
  return (
    <div className="tarot-draw-mode-picker segment-switch">
      {OPTIONS.map((item) => (
        <button
          key={item.id}
          type="button"
          className={value === item.id ? "tab active" : "tab"}
          disabled={disabled}
          onClick={() => onChange(item.id)}
        >
          <span>{item.label}</span>
          <small>{item.hint}</small>
        </button>
      ))}
    </div>
  );
}

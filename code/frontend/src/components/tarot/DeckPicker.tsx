import type { TarotDeckId } from "../../types/tarot";

interface Props {
  value: TarotDeckId;
  onChange: (deck: TarotDeckId) => void;
  disabled?: boolean;
}

const OPTIONS: { id: TarotDeckId; label: string; hint: string }[] = [
  { id: "rws", label: "韦特塔罗", hint: "Rider-Waite-Smith" },
  { id: "marseille", label: "马赛塔罗", hint: "Tarot de Marseille" },
  { id: "thoth", label: "托特塔罗", hint: "文字解读 (无牌面图)" },
];

export function DeckPicker({ value, onChange, disabled }: Props) {
  return (
    <div className="tarot-deck-picker segment-switch">
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

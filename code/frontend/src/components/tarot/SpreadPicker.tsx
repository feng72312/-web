import type { SpreadDef } from "../../types/tarot";

const COMPLEXITY_ZH: Record<string, string> = {
  beginner: "入门",
  intermediate: "进阶",
  advanced: "深度",
};

interface Props {
  spreads: SpreadDef[];
  value: string;
  onChange: (spreadId: string) => void;
  onSuggest: () => void;
  suggestLoading?: boolean;
  suggestReason?: string;
  disabled?: boolean;
}

export function SpreadPicker({
  spreads,
  value,
  onChange,
  onSuggest,
  suggestLoading,
  suggestReason,
  disabled,
}: Props) {
  return (
    <div className="tarot-spread-picker">
      <div className="spread-picker-head">
        <h3 className="cast-form-section-title">牌阵</h3>
        <button
          type="button"
          className="secondary"
          disabled={disabled || suggestLoading}
          onClick={onSuggest}
        >
          {suggestLoading ? "匹配中..." : "AI 推荐牌阵"}
        </button>
      </div>
      {suggestReason && <p className="hint">{suggestReason}</p>}
      <div className="spread-grid">
        {spreads.map((spread) => (
          <button
            key={spread.id}
            type="button"
            className={value === spread.id ? "spread-card active" : "spread-card"}
            disabled={disabled}
            onClick={() => onChange(spread.id)}
          >
            <strong>{spread.nameZh}</strong>
            <span>{spread.cardCount} 张</span>
            <small>{COMPLEXITY_ZH[spread.complexity] ?? spread.complexity}</small>
          </button>
        ))}
      </div>
    </div>
  );
}

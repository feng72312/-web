interface Props {
  count: 1 | 2 | 3;
  values: string[];
  onCountChange: (count: 1 | 2 | 3) => void;
  onChange: (index: number, value: string) => void;
}

export function NumberCastForm({ count, values, onCountChange, onChange }: Props) {
  return (
    <div className="liuyao-number-panel">
      <div className="method-switch">
        {[1, 2, 3].map((num) => (
          <button
            key={num}
            type="button"
            className={count === num ? "tab active" : "tab"}
            onClick={() => onCountChange(num as 1 | 2 | 3)}
          >
            {num} 数起卦
          </button>
        ))}
      </div>
      <div className="number-inputs">
        {Array.from({ length: count }).map((_, idx) => (
          <label key={idx}>
            数字 {idx + 1}
            <input
              type="number"
              min={1}
              value={values[idx] ?? ""}
              onChange={(event) => onChange(idx, event.target.value)}
            />
          </label>
        ))}
      </div>
    </div>
  );
}

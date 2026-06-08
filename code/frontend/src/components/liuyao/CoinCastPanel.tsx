interface Props {
  lines: number[];
  onThrow: () => void;
  onReset: () => void;
  disabled?: boolean;
}

const LINE_LABELS = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"];

function lineLabel(value: number): string {
  if (value === 9) return "老阳 O";
  if (value === 6) return "老阴 X";
  if (value === 7) return "少阳";
  return "少阴";
}

export function rollCoinLine(): number {
  let tails = 0;
  for (let i = 0; i < 3; i += 1) {
    if (Math.random() < 0.5) {
      tails += 1;
    }
  }
  if (tails === 3) return 9;
  if (tails === 0) return 6;
  if (tails === 2) return 8;
  return 7;
}

export function CoinCastPanel({ lines, onThrow, onReset, disabled }: Props) {
  const done = lines.length >= 6;
  return (
    <div className="liuyao-coin-panel cast-form-embedded">
      <p className="hint">三钱摇卦, 自下而上记录, 共六次.</p>
      <div className="coin-actions form-actions-inline">
        <button
          type="button"
          className="primary-btn"
          disabled={disabled || done}
          onClick={onThrow}
        >
          {done ? "已完成六次" : `掷第 ${lines.length + 1} 爻`}
        </button>
        <button
          type="button"
          className="secondary"
          disabled={disabled || lines.length === 0}
          onClick={onReset}
        >
          重新摇卦
        </button>
      </div>
      {lines.length > 0 && (
        <ul className="coin-line-list">
          {lines.map((value, idx) => (
            <li key={idx}>
              <span className="coin-line-label">{LINE_LABELS[idx]}</span>
              <span className="coin-line-value">
                {lineLabel(value)} ({value})
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

interface Props {
  useNow: boolean;
  onUseNowChange: (value: boolean) => void;
  datetime: string;
  onDatetimeChange: (value: string) => void;
}

export function TimeCastForm({
  useNow,
  onUseNowChange,
  datetime,
  onDatetimeChange,
}: Props) {
  return (
    <div className="liuyao-time-panel">
      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={useNow}
          onChange={(event) => onUseNowChange(event.target.checked)}
        />
        使用当前时间 (农历取数, 月建按节气)
      </label>
      {!useNow && (
        <label>
          起卦时间
          <input
            type="datetime-local"
            value={datetime}
            onChange={(event) => onDatetimeChange(event.target.value)}
          />
        </label>
      )}
    </div>
  );
}

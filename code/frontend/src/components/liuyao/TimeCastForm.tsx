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
    <div className="liuyao-time-panel cast-form-embedded">
      <label className="field checkbox-field">
        <input
          type="checkbox"
          checked={useNow}
          onChange={(event) => onUseNowChange(event.target.checked)}
        />
        <span>使用当前时间 (农历取数, 月建按节气)</span>
      </label>
      {!useNow && (
        <label className="field">
          <span>起卦时间</span>
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

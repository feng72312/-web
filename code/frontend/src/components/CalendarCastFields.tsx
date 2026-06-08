import type { CalendarType } from "../types/bazi";

interface CalendarCastFieldsProps {
  calendarType: CalendarType;
  onCalendarTypeChange: (v: CalendarType) => void;
  isLeapMonth: boolean;
  onIsLeapMonthChange: (v: boolean) => void;
  year: number;
  onYearChange: (v: number) => void;
  month: number;
  onMonthChange: (v: number) => void;
  day: number;
  onDayChange: (v: number) => void;
}

export function CalendarCastFields(props: CalendarCastFieldsProps) {
  const label = props.calendarType === "lunar" ? "农历" : "公历";
  return (
    <div className="calendar-cast-fields cast-form-embedded">
      <div className="calendar-tabs">
        <button
          type="button"
          className={props.calendarType === "solar" ? "tab active" : "tab"}
          onClick={() => {
            props.onCalendarTypeChange("solar");
            props.onIsLeapMonthChange(false);
          }}
        >
          公历
        </button>
        <button
          type="button"
          className={props.calendarType === "lunar" ? "tab active" : "tab"}
          onClick={() => props.onCalendarTypeChange("lunar")}
        >
          农历
        </button>
      </div>
      <p className="hint">占时按 {label} 输入年月日, 后端换算四柱</p>
      <div className="field-row">
        <label className="field">
          <span>年</span>
          <input
            type="number"
            min={1900}
            max={2100}
            value={props.year}
            onChange={(e) => props.onYearChange(Number(e.target.value))}
          />
        </label>
        <label className="field">
          <span>月</span>
          <input
            type="number"
            min={1}
            max={12}
            value={props.month}
            onChange={(e) => props.onMonthChange(Number(e.target.value))}
          />
        </label>
        <label className="field">
          <span>日</span>
          <input
            type="number"
            min={1}
            max={31}
            value={props.day}
            onChange={(e) => props.onDayChange(Number(e.target.value))}
          />
        </label>
      </div>
      {props.calendarType === "lunar" && (
        <label className="field checkbox-field">
          <input
            type="checkbox"
            checked={props.isLeapMonth}
            onChange={(e) => props.onIsLeapMonthChange(e.target.checked)}
          />
          <span>闰月</span>
        </label>
      )}
    </div>
  );
}

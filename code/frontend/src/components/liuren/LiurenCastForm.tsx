import type { CalendarType } from "../../types/bazi";
import type { LiurenCastMethod, LiurenCategory } from "../../types/liuren";
import { CalendarCastFields } from "../CalendarCastFields";

const DIZHI = ["", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];

interface LiurenCastFormProps {
  question: string;
  onQuestionChange: (v: string) => void;
  category: LiurenCategory;
  onCategoryChange: (v: LiurenCategory) => void;
  castMethod: LiurenCastMethod;
  onCastMethodChange: (v: LiurenCastMethod) => void;
  jinkouDifen: string;
  onJinkouDifenChange: (v: string) => void;
  guiRenMode: number;
  onGuiRenModeChange: (v: number) => void;
  useTrueSolarTime: boolean;
  onUseTrueSolarTimeChange: (v: boolean) => void;
  longitude: string;
  onLongitudeChange: (v: string) => void;
  useNow: boolean;
  onUseNowChange: (v: boolean) => void;
  datetime: string;
  onDatetimeChange: (v: string) => void;
  calendarType: CalendarType;
  onCalendarTypeChange: (v: CalendarType) => void;
  isLeapMonth: boolean;
  onIsLeapMonthChange: (v: boolean) => void;
  calYear: number;
  onCalYearChange: (v: number) => void;
  calMonth: number;
  onCalMonthChange: (v: number) => void;
  calDay: number;
  onCalDayChange: (v: number) => void;
}

export function LiurenCastForm(props: LiurenCastFormProps) {
  return (
    <div className="liuren-cast-form panel-block">
      <label className="field">
        <span>问事</span>
        <textarea
          rows={2}
          value={props.question}
          onChange={(e) => props.onQuestionChange(e.target.value)}
          placeholder="请输入问事内容"
        />
      </label>
      <div className="field-row">
        <label className="field">
          <span>类别</span>
          <select
            value={props.category}
            onChange={(e) =>
              props.onCategoryChange(e.target.value as LiurenCategory)
            }
          >
            <option value="shizhan">事占</option>
            <option value="xingzhan">行占</option>
          </select>
        </label>
        <label className="field">
          <span>起课</span>
          <select
            value={props.castMethod}
            onChange={(e) =>
              props.onCastMethodChange(e.target.value as LiurenCastMethod)
            }
          >
            <option value="liuren">正六壬</option>
            <option value="jinkou">金口诀</option>
            <option value="both">六壬+金口诀</option>
          </select>
        </label>
      </div>
      {(props.castMethod === "jinkou" || props.castMethod === "both") && (
        <label className="field">
          <span>金口诀地分</span>
          <select
            value={props.jinkouDifen}
            onChange={(e) => props.onJinkouDifenChange(e.target.value)}
          >
            {DIZHI.map((z) => (
              <option key={z || "auto"} value={z}>
                {z === "" ? "默认(占时支)" : z}
              </option>
            ))}
          </select>
        </label>
      )}
      {props.castMethod !== "jinkou" && (
        <label className="field">
          <span>贵人行运</span>
          <select
            value={String(props.guiRenMode)}
            onChange={(e) => props.onGuiRenModeChange(Number(e.target.value))}
          >
            <option value="0">昼贵</option>
            <option value="1">夜贵</option>
          </select>
        </label>
      )}
      <label className="field checkbox-field">
        <input
          type="checkbox"
          checked={props.useTrueSolarTime}
          onChange={(e) => props.onUseTrueSolarTimeChange(e.target.checked)}
        />
        <span>真太阳时</span>
      </label>
      {props.useTrueSolarTime && (
        <label className="field">
          <span>经度</span>
          <input
            type="text"
            value={props.longitude}
            onChange={(e) => props.onLongitudeChange(e.target.value)}
          />
        </label>
      )}
      <CalendarCastFields
        calendarType={props.calendarType}
        onCalendarTypeChange={props.onCalendarTypeChange}
        isLeapMonth={props.isLeapMonth}
        onIsLeapMonthChange={props.onIsLeapMonthChange}
        year={props.calYear}
        onYearChange={props.onCalYearChange}
        month={props.calMonth}
        onMonthChange={props.onCalMonthChange}
        day={props.calDay}
        onDayChange={props.onCalDayChange}
      />
      <label className="field checkbox-field">
        <input
          type="checkbox"
          checked={props.useNow}
          onChange={(e) => props.onUseNowChange(e.target.checked)}
        />
        <span>使用当前时刻(时分)</span>
      </label>
      {!props.useNow && (
        <label className="field">
          <span>占时</span>
          <input
            type="datetime-local"
            value={props.datetime}
            onChange={(e) => props.onDatetimeChange(e.target.value)}
          />
        </label>
      )}
    </div>
  );
}

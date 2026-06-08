import type { CalendarType } from "../../types/bazi";

import type { QimenCategory, QimenMethod } from "../../types/qimen";

import { CalendarCastFields } from "../CalendarCastFields";



const DIRECTIONS = ["", "北", "东北", "东", "东南", "南", "西南", "西", "西北"];



interface QimenCastFormProps {

  question: string;

  onQuestionChange: (v: string) => void;

  category: QimenCategory;

  onCategoryChange: (v: QimenCategory) => void;

  method: QimenMethod;

  onMethodChange: (v: QimenMethod) => void;

  direction: string;

  onDirectionChange: (v: string) => void;

  useTrueSolarTime: boolean;

  onUseTrueSolarTimeChange: (v: boolean) => void;

  longitude: string;

  onLongitudeChange: (v: string) => void;

  juOverride: string;

  onJuOverrideChange: (v: string) => void;

  useNow: boolean;

  onUseNowChange: (v: boolean) => void;

  datetime: string;

  onDatetimeChange: (v: string) => void;

  useBirthProfile: boolean;

  onUseBirthProfileChange: (v: boolean) => void;

  birthProfileHint: string;

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



export function QimenCastForm(props: QimenCastFormProps) {

  return (

    <div className="qimen-cast-form cast-form">

      <section className="cast-form-section">

        <h3 className="cast-form-section-title">问事</h3>

        <label className="field field-grow">

          <span>问事内容</span>

          <textarea

            rows={3}

            value={props.question}

            onChange={(e) => props.onQuestionChange(e.target.value)}

            placeholder="请输入问事内容"

          />

        </label>

      </section>



      <section className="cast-form-section">

        <h3 className="cast-form-section-title">起局设置</h3>

        <div className="field-row field-row-3">

          <label className="field">

            <span>类别</span>

            <select

              value={props.category}

              onChange={(e) =>

                props.onCategoryChange(e.target.value as QimenCategory)

              }

            >

              <option value="shizhan">事占</option>

              <option value="xingzhan">行占</option>

            </select>

          </label>

          <label className="field">

            <span>排盘法</span>

            <select

              value={props.method}

              onChange={(e) =>

                props.onMethodChange(e.target.value as QimenMethod)

              }

            >

              <option value="chaibu">拆补</option>

              <option value="zhirun">置闰</option>

              <option value="maoshan">茅山转盘</option>

            </select>

          </label>

          <label className="field">

            <span>方位</span>

            <select

              value={props.direction}

              onChange={(e) => props.onDirectionChange(e.target.value)}

            >

              {DIRECTIONS.map((d) => (

                <option key={d || "none"} value={d}>

                  {d || "未指定"}

                </option>

              ))}

            </select>

          </label>

        </div>

        <label className="field field-narrow">

          <span>调试局数 (1-9, 留空自动)</span>

          <input

            type="number"

            min={1}

            max={9}

            placeholder="自动"

            value={props.juOverride}

            onChange={(e) => props.onJuOverrideChange(e.target.value)}

          />

        </label>

        <label className="field checkbox-field">

          <input

            type="checkbox"

            checked={props.useBirthProfile}

            onChange={(e) => props.onUseBirthProfileChange(e.target.checked)}

          />

          <span>AI 参考八字命盘 (不影响起局)</span>

        </label>

        {props.useBirthProfile && (

          <p className="hint">{props.birthProfileHint}</p>

        )}

      </section>



      <section className="cast-form-section">

        <h3 className="cast-form-section-title">占时</h3>

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

        <div className="cast-form-options">

          <label className="field checkbox-field">

            <input

              type="checkbox"

              checked={props.useNow}

              onChange={(e) => props.onUseNowChange(e.target.checked)}

            />

            <span>使用当前时刻 (时分)</span>

          </label>

          <label className="field checkbox-field">

            <input

              type="checkbox"

              checked={props.useTrueSolarTime}

              onChange={(e) =>

                props.onUseTrueSolarTimeChange(e.target.checked)

              }

            />

            <span>真太阳时</span>

          </label>

        </div>

        {!props.useNow && (

          <label className="field">

            <span>指定起局时间</span>

            <input

              type="datetime-local"

              value={props.datetime}

              onChange={(e) => props.onDatetimeChange(e.target.value)}

            />

          </label>

        )}

        {props.useTrueSolarTime && (

          <label className="field field-narrow">

            <span>经度</span>

            <input

              type="number"

              step="0.1"

              value={props.longitude}

              onChange={(e) => props.onLongitudeChange(e.target.value)}

            />

          </label>

        )}

      </section>

    </div>

  );

}



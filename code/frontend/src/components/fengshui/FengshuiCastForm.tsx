import type { FengshuiMethod, FengshuiScene } from "../../types/fengshui";
import type { FengshuiMountain } from "../../types/fengshui";
import { SittingMountainPicker } from "./SittingMountainPicker";

interface FengshuiCastFormProps {
  question: string;
  onQuestionChange: (v: string) => void;
  method: FengshuiMethod;
  onMethodChange: (v: FengshuiMethod) => void;
  scene: FengshuiScene;
  onSceneChange: (v: FengshuiScene) => void;
  birthYear: number;
  onBirthYearChange: (v: number) => void;
  gender: 0 | 1;
  onGenderChange: (v: 0 | 1) => void;
  buildYear: number;
  onBuildYearChange: (v: number) => void;
  flowYear: string;
  onFlowYearChange: (v: string) => void;
  sittingMountain: string;
  onSittingMountainChange: (v: string) => void;
  mountains: FengshuiMountain[];
}

export function FengshuiCastForm(props: FengshuiCastFormProps) {
  const isXuankong = props.method === "xuankong";

  return (
    <div className="fengshui-cast-form cast-form">
      <section className="cast-form-section">
        <h3 className="cast-form-section-title">问事</h3>
        <label className="field field-grow">
          <span>问事内容</span>
          <textarea
            rows={3}
            value={props.question}
            onChange={(e) => props.onQuestionChange(e.target.value)}
            placeholder="例如: 这套房子适合长期居住吗? 财位在哪个方位?"
          />
        </label>
      </section>

      <section className="cast-form-section">
        <h3 className="cast-form-section-title">流派与宅向</h3>
        <div className="field-row field-row-2">
          <label className="field">
            <span>流派</span>
            <select
              value={props.method}
              onChange={(e) => props.onMethodChange(e.target.value as FengshuiMethod)}
            >
              <option value="bazhai">八宅</option>
              <option value="xuankong">玄空飞星</option>
            </select>
          </label>
          <label className="field">
            <span>场景</span>
            <select
              value={props.scene}
              onChange={(e) => props.onSceneChange(e.target.value as FengshuiScene)}
            >
              <option value="residence">住宅</option>
              <option value="shop">店铺</option>
              <option value="office">办公室</option>
            </select>
          </label>
        </div>
        <SittingMountainPicker
          value={props.sittingMountain}
          onChange={props.onSittingMountainChange}
          mountains={props.mountains}
        />
        <div className="field-row field-row-2">
          {isXuankong ? (
            <label className="field">
              <span>建成/入伙年</span>
              <input
                type="number"
                min={1864}
                max={2043}
                value={props.buildYear}
                onChange={(e) => props.onBuildYearChange(Number(e.target.value) || 2020)}
              />
            </label>
          ) : (
            <label className="field">
              <span>出生年 (公历)</span>
              <input
                type="number"
                min={1900}
                max={2100}
                value={props.birthYear}
                onChange={(e) => props.onBirthYearChange(Number(e.target.value) || 1990)}
              />
            </label>
          )}
        </div>
        <div className="field-row field-row-2">
          {isXuankong ? (
            <>
              <label className="field">
                <span>流年年份 (可选)</span>
                <input
                  type="number"
                  min={1864}
                  max={2100}
                  placeholder="留空则不排流年"
                  value={props.flowYear}
                  onChange={(e) => props.onFlowYearChange(e.target.value)}
                />
              </label>
              <div className="field" aria-hidden="true" />
            </>
          ) : (
            <>
              <label className="field">
                <span>性别</span>
                <select
                  value={props.gender}
                  onChange={(e) => props.onGenderChange(Number(e.target.value) as 0 | 1)}
                >
                  <option value={1}>男</option>
                  <option value={0}>女</option>
                </select>
              </label>
              <div className="field" aria-hidden="true" />
            </>
          )}
        </div>
      </section>
    </div>
  );
}

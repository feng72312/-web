import { useEffect, useMemo, useState } from "react";
import type { FengshuiMountain } from "../../types/fengshui";
import {
  describeMountainChoice,
  findPresetByFacing,
  findPresetByMountainId,
  FACING_PRESETS,
  groupMountainsByTrigram,
  mountainLabel,
  presetFromFacingDegrees,
  SECTOR_FINE_LABELS,
  type FacingDirection,
} from "../../utils/sittingMountainHelper";

export type SittingPickerMode = "beginner" | "pro";

interface SittingMountainPickerProps {
  value: string;
  onChange: (mountainId: string) => void;
  mountains: FengshuiMountain[];
}

const COMPASS_BUTTONS: Array<{ facing: FacingDirection; position: string }> = [
  { facing: "NW", position: "nw" },
  { facing: "N", position: "n" },
  { facing: "NE", position: "ne" },
  { facing: "W", position: "w" },
  { facing: "E", position: "e" },
  { facing: "SW", position: "sw" },
  { facing: "S", position: "s" },
  { facing: "SE", position: "se" },
];

export function SittingMountainPicker(props: SittingMountainPickerProps) {
  const [mode, setMode] = useState<SittingPickerMode>("beginner");
  const [facing, setFacing] = useState<FacingDirection>("S");
  const [fineIndex, setFineIndex] = useState<0 | 1 | 2>(1);
  const [degreeInput, setDegreeInput] = useState("180");

  const preset = useMemo(() => findPresetByFacing(facing), [facing]);
  const grouped = useMemo(() => groupMountainsByTrigram(props.mountains), [props.mountains]);

  useEffect(() => {
    const fromValue = findPresetByMountainId(props.value);
    if (!fromValue) {
      return;
    }
    setFacing(fromValue.id);
    const idx = fromValue.sectorMountainIds.indexOf(props.value);
    if (idx >= 0) {
      setFineIndex(idx as 0 | 1 | 2);
    }
  }, [props.value]);

  const selectFacing = (dir: FacingDirection, fine: 0 | 1 | 2 = 1) => {
    const nextPreset = findPresetByFacing(dir);
    if (!nextPreset) {
      return;
    }
    setFacing(dir);
    setFineIndex(fine);
    props.onChange(nextPreset.sectorMountainIds[fine]);
  };

  const applyDegrees = () => {
    const degrees = Number(degreeInput);
    if (Number.isNaN(degrees)) {
      return;
    }
    const nextPreset = presetFromFacingDegrees(degrees);
    selectFacing(nextPreset.id, 1);
  };

  const selectedMountain = props.mountains.find((item) => item.id === props.value);
  const fineLabels = preset ? SECTOR_FINE_LABELS[preset.trigram] : null;

  return (
    <div className="sitting-picker">
      <div className="sitting-picker-head">
        <span className="sitting-picker-title">宅坐向</span>
        <div className="sitting-picker-mode" role="tablist" aria-label="选向模式">
          <button
            type="button"
            role="tab"
            className={mode === "beginner" ? "active" : ""}
            aria-selected={mode === "beginner"}
            onClick={() => setMode("beginner")}
          >
            新手
          </button>
          <button
            type="button"
            role="tab"
            className={mode === "pro" ? "active" : ""}
            aria-selected={mode === "pro"}
            onClick={() => setMode("pro")}
          >
            专业
          </button>
        </div>
      </div>

      {mode === "beginner" ? (
        <div className="sitting-picker-beginner">
          <p className="hint sitting-picker-hint">
            先想「大门或阳台主要朝哪」: 与「坐山」相反。例如大门朝南, 就是常见的坐北朝南。
          </p>

          <div className="compass-picker" aria-label="大门朝向选择">
            {COMPASS_BUTTONS.map(({ facing: dir, position }) => {
              const item = FACING_PRESETS.find((row) => row.id === dir);
              if (!item) return null;
              const active = facing === dir;
              return (
                <button
                  key={dir}
                  type="button"
                  className={`compass-btn compass-btn-${position}${active ? " active" : ""}`}
                  onClick={() => selectFacing(dir, 1)}
                  title={item.houseLabel}
                >
                  <span className="compass-btn-dir">{item.doorLabel.replace("大门朝", "")}</span>
                  <span className="compass-btn-sub">{item.houseLabel}</span>
                </button>
              );
            })}
            <div className="compass-center">朝向</div>
          </div>

          {preset && (
            <div className="sitting-picker-result">
              <strong>{preset.houseLabel}</strong>
              <span>
                对应 {mountainLabel(props.mountains, preset.sectorMountainIds[fineIndex])} (
                {preset.trigram}卦)
              </span>
            </div>
          )}

          {preset && fineLabels && (
            <fieldset className="sitting-fine-tune">
              <legend>不确定时选中间; 知道偏一点可微调</legend>
              <div className="sitting-fine-options">
                {preset.sectorMountainIds.map((mid, index) => (
                  <label key={mid} className="sitting-fine-option">
                    <input
                      type="radio"
                      name="fineMountain"
                      checked={fineIndex === index}
                      onChange={() => {
                        setFineIndex(index as 0 | 1 | 2);
                        props.onChange(mid);
                      }}
                    />
                    <span>
                      {fineLabels[index]}: {mountainLabel(props.mountains, mid)}
                    </span>
                  </label>
                ))}
              </div>
            </fieldset>
          )}

          <details className="sitting-degree-tool">
            <summary>有罗盘读数? 输入朝向角度</summary>
            <p className="hint">角度以正北为 0 度, 顺时针增加。手机罗盘读「门朝向」即可。</p>
            <div className="sitting-degree-row">
              <input
                type="number"
                min={0}
                max={359}
                value={degreeInput}
                onChange={(e) => setDegreeInput(e.target.value)}
                placeholder="例如 180 表示朝南"
              />
              <button type="button" className="secondary" onClick={applyDegrees}>
                换算
              </button>
            </div>
          </details>
        </div>
      ) : (
        <div className="sitting-picker-pro">
          <label className="field field-grow">
            <span>二十四山 (坐山)</span>
            <select
              value={props.value}
              onChange={(e) => props.onChange(e.target.value)}
            >
              {grouped.map((group) => (
                <optgroup key={group.trigram} label={`${group.trigram}卦`}>
                  {group.items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.label}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </label>
          <p className="hint">
            专业模式直接选坐山。{selectedMountain ? describeMountainChoice(props.mountains, props.value) : ""}
          </p>
        </div>
      )}
    </div>
  );
}

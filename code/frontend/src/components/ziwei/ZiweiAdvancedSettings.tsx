import type { ZiweiProfileSettings } from "../../types/bazi";

interface Props {
  settings: ZiweiProfileSettings;
  onChange: (patch: Partial<ZiweiProfileSettings>) => void;
}

export function ZiweiAdvancedSettings({ settings, onChange }: Props) {
  return (
    <details className="ziwei-advanced cast-form-inset">
      <summary className="cast-form-inset-summary">高级排盘规则</summary>
      <div className="cast-form-inset-body">
        <label className="field checkbox-field">
          <input
            type="checkbox"
            checked={settings.useTrueSolarTime}
            onChange={(e) => onChange({ useTrueSolarTime: e.target.checked })}
          />
          <span>真太阳时校正 (经度 {settings.longitude})</span>
        </label>
        {!settings.useTrueSolarTime && (
          <p className="hint">关闭后直接使用输入的公历/农历时刻</p>
        )}
        <div className="field-row field-row-2">
          <label className="field field-narrow">
            <span>经度</span>
            <input
              type="number"
              min={70}
              max={140}
              step={0.1}
              value={settings.longitude}
              onChange={(e) =>
                onChange({ longitude: Number(e.target.value) || 120 })
              }
            />
          </label>
          <label className="field">
            <span>闰月</span>
            <select
              value={settings.leapMonthRule}
              onChange={(e) =>
                onChange({
                  leapMonthRule: e.target
                    .value as ZiweiProfileSettings["leapMonthRule"],
                })
              }
            >
              <option value="next_month">归下月 (默认)</option>
              <option value="midmonth_split">半月分界</option>
            </select>
          </label>
        </div>
        <div className="field-row field-row-2">
          <label className="field">
            <span>子时</span>
            <select
              value={settings.ziHourRule}
              onChange={(e) =>
                onChange({
                  ziHourRule: e.target.value as ZiweiProfileSettings["ziHourRule"],
                })
              }
            >
              <option value="combined">不分早晚子时</option>
              <option value="split">分早晚子时</option>
            </select>
          </label>
          <label className="field">
            <span>四化表 (预留)</span>
            <select value={settings.mutagenTable ?? "nan_pai"} disabled>
              <option value="nan_pai">南派三合</option>
            </select>
          </label>
        </div>
      </div>
    </details>
  );
}

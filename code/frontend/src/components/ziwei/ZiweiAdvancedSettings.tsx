import type { ZiweiProfileSettings } from "../../types/bazi";

interface Props {
  settings: ZiweiProfileSettings;
  onChange: (patch: Partial<ZiweiProfileSettings>) => void;
}

export function ZiweiAdvancedSettings({ settings, onChange }: Props) {
  return (
    <details className="ziwei-advanced panel-inset">
      <summary>高级排盘规则</summary>
      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={settings.useTrueSolarTime}
          onChange={(e) => onChange({ useTrueSolarTime: e.target.checked })}
        />
        真太阳时校正 (经度 {settings.longitude})
      </label>
      {!settings.useTrueSolarTime && (
        <p className="hint">关闭后直接使用输入的公历/农历时刻</p>
      )}
      <label>
        经度
        <input
          type="number"
          min={70}
          max={140}
          step={0.1}
          value={settings.longitude}
          onChange={(e) => onChange({ longitude: Number(e.target.value) || 120 })}
        />
      </label>
      <label>
        闰月
        <select
          value={settings.leapMonthRule}
          onChange={(e) =>
            onChange({ leapMonthRule: e.target.value as ZiweiProfileSettings["leapMonthRule"] })
          }
        >
          <option value="next_month">归下月 (默认)</option>
          <option value="midmonth_split">半月分界</option>
        </select>
      </label>
      <label>
        子时
        <select
          value={settings.ziHourRule}
          onChange={(e) =>
            onChange({ ziHourRule: e.target.value as ZiweiProfileSettings["ziHourRule"] })
          }
        >
          <option value="combined">不分早晚子时</option>
          <option value="split">分早晚子时</option>
        </select>
      </label>
      <label>
        四化表 (预留)
        <select value={settings.mutagenTable ?? "nan_pai"} disabled>
          <option value="nan_pai">南派三合</option>
        </select>
      </label>
    </details>
  );
}

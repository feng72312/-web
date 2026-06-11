import type { ZiweiChart, ZiweiRuntimeLayer } from "../../types/ziwei";
import { getActiveLayer } from "./ziweiDisplay";

const RUNTIME_OPTIONS: Array<{ id: ZiweiRuntimeLayer; label: string }> = [
  { id: "native", label: "本命" },
  { id: "decadal", label: "大限" },
  { id: "yearly", label: "流年" },
  { id: "monthly", label: "流月" },
  { id: "daily", label: "流日" },
  { id: "hourly", label: "流时" },
];

interface ZiweiTimeNavigatorProps {
  chart: ZiweiChart;
  targetYear: number;
  runtimeLayer: ZiweiRuntimeLayer;
  selectedDecadalIndex: number | null;
  onRuntimeLayerChange: (layer: ZiweiRuntimeLayer) => void;
  onTargetYearChange?: (year: number) => void;
  onSelectDecadal: (index: number) => void;
}

export function ZiweiTimeNavigator({
  chart,
  targetYear,
  runtimeLayer,
  selectedDecadalIndex,
  onRuntimeLayerChange,
  onTargetYearChange,
  onSelectDecadal,
}: ZiweiTimeNavigatorProps) {
  return (
    <div className="ziwei-time-navigator">
      <div className="ziwei-time-runtime">
        {RUNTIME_OPTIONS.map((option) => {
          const layer = getActiveLayer(chart, option.id);
          const disabled = option.id !== "native" && layer && !layer.available;
          return (
            <button
              key={option.id}
              type="button"
              className={runtimeLayer === option.id ? "ziwei-time-btn active" : "ziwei-time-btn"}
              disabled={disabled}
              title={disabled ? layer?.reason : undefined}
              onClick={() => onRuntimeLayerChange(option.id)}
            >
              {option.label}
            </button>
          );
        })}
      </div>
      <div className="ziwei-time-controls">
        <label className="ziwei-time-year">
          流年参照年
          <input
            type="number"
            min={1900}
            max={2100}
            value={targetYear}
            onChange={(e) => onTargetYearChange?.(Number(e.target.value) || targetYear)}
          />
        </label>
        <div className="ziwei-decadal-pills">
          {chart.limits.decadal.map((item) => (
            <button
              key={item.index}
              type="button"
              className={
                selectedDecadalIndex === item.index
                  ? "ziwei-decadal-pill active"
                  : "ziwei-decadal-pill"
              }
              onClick={() => onSelectDecadal(item.index)}
            >
              {item.ageRange} {item.palace}
            </button>
          ))}
        </div>
      </div>
      {runtimeLayer !== "native" ? (
        <p className="ziwei-time-active">
          当前层: {runtimeLayer}{" "}
          {getActiveLayer(chart, runtimeLayer)?.stemBranch
            ? `(${getActiveLayer(chart, runtimeLayer)?.stemBranch})`
            : ""}
        </p>
      ) : null}
    </div>
  );
}

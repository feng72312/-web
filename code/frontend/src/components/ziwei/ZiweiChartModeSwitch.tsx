import type { ZiweiDisplayMode } from "../../types/ziwei";

interface ZiweiChartModeSwitchProps {
  mode: ZiweiDisplayMode;
  loading?: boolean;
  onChange: (mode: ZiweiDisplayMode) => void;
}

export function ZiweiChartModeSwitch({ mode, loading = false, onChange }: ZiweiChartModeSwitchProps) {
  return (
    <div className="ziwei-chart-mode-switch" role="group" aria-label="排盘显示模式">
      <button
        type="button"
        className={mode === "simple" ? "active" : ""}
        disabled={loading}
        onClick={() => onChange("simple")}
      >
        简易排盘
      </button>
      <button
        type="button"
        className={mode === "pro" ? "active" : ""}
        disabled={loading}
        onClick={() => onChange("pro")}
      >
        专业排盘
      </button>
      <p className="ziwei-chart-mode-hint">
        {mode === "simple"
          ? "快速展示本命十二宫与四化, 适合先看盘面结构."
          : "含流年/流月/流日/流时与层级高亮, 计算更完整但耗时更长."}
      </p>
    </div>
  );
}

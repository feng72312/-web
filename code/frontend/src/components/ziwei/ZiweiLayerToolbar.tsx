import type { ZiweiDisplayLayer, ZiweiHighlightMode } from "../../types/ziwei";

const LAYER_OPTIONS: Array<{ id: ZiweiDisplayLayer; label: string }> = [
  { id: "native", label: "本命" },
  { id: "mutagen", label: "四化" },
  { id: "malefic", label: "煞曜" },
  { id: "triad", label: "三方四正" },
  { id: "decadal", label: "大限" },
  { id: "yearly", label: "流年" },
  { id: "all", label: "全部" },
];

interface ZiweiLayerToolbarProps {
  activeLayers: Set<ZiweiDisplayLayer>;
  highlightMode: ZiweiHighlightMode;
  onToggleLayer: (layer: ZiweiDisplayLayer) => void;
  onHighlightModeChange: (mode: ZiweiHighlightMode) => void;
}

export function ZiweiLayerToolbar({
  activeLayers,
  highlightMode,
  onToggleLayer,
  onHighlightModeChange,
}: ZiweiLayerToolbarProps) {
  return (
    <div className="ziwei-layer-toolbar">
      <div className="ziwei-layer-group">
        {LAYER_OPTIONS.map((option) => (
          <button
            key={option.id}
            type="button"
            className={
              activeLayers.has(option.id) || (option.id === "all" && activeLayers.has("all"))
                ? "ziwei-layer-btn active"
                : "ziwei-layer-btn"
            }
            onClick={() => onToggleLayer(option.id)}
          >
            {option.label}
          </button>
        ))}
      </div>
      <div className="ziwei-layer-group">
        <button
          type="button"
          className={highlightMode === "mutagen" ? "ziwei-layer-btn active" : "ziwei-layer-btn"}
          onClick={() =>
            onHighlightModeChange(highlightMode === "mutagen" ? "none" : "mutagen")
          }
        >
          高亮四化
        </button>
        <button
          type="button"
          className={highlightMode === "malefic" ? "ziwei-layer-btn active" : "ziwei-layer-btn"}
          onClick={() =>
            onHighlightModeChange(highlightMode === "malefic" ? "none" : "malefic")
          }
        >
          高亮煞曜
        </button>
      </div>
    </div>
  );
}

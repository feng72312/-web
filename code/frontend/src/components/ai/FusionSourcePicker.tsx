import { useMemo, useState } from "react";
import type { FusionChartSource } from "./fusionTypes";

interface FusionSourcePickerProps {
  sources: FusionChartSource[];
  selectedIds: string[];
  disabled?: boolean;
  onToggle: (sourceId: string) => void;
  onRemove: (sourceId: string) => void;
  onCreateFusion: () => void;
}

export function FusionSourcePicker({
  sources,
  selectedIds,
  disabled = false,
  onToggle,
  onRemove,
  onCreateFusion,
}: FusionSourcePickerProps) {
  const [moduleFilter, setModuleFilter] = useState("all");

  const moduleOptions = useMemo(() => {
    const labels = new Map<string, string>();
    for (const item of sources) {
      labels.set(item.moduleId, item.moduleLabel);
    }
    return Array.from(labels.entries()).map(([id, label]) => ({ id, label }));
  }, [sources]);

  const filteredSources = useMemo(() => {
    if (moduleFilter === "all") {
      return sources;
    }
    return sources.filter((item) => item.moduleId === moduleFilter);
  }, [moduleFilter, sources]);

  const selectedCount = selectedIds.length;
  const canCreate = selectedCount >= 2 && !disabled;

  return (
    <section className="ai-chat-fusion-panel">
      <div className="ai-chat-fusion-head">
        <h3>融合分析</h3>
        <span className="ai-chat-fusion-count">
          素材库 {sources.length} 条 / 已选 {selectedCount}
        </span>
      </div>
      <p className="ai-chat-fusion-desc">
        从历史排盘中勾选两个及以上盘面, 创建独立融合会话后继续追问同向点与冲突点.
      </p>

      {moduleOptions.length > 1 ? (
        <div className="ai-chat-fusion-filters">
          <button
            type="button"
            className={moduleFilter === "all" ? "ai-chat-fusion-filter active" : "ai-chat-fusion-filter"}
            disabled={disabled}
            onClick={() => setModuleFilter("all")}
          >
            全部
          </button>
          {moduleOptions.map((item) => (
            <button
              key={item.id}
              type="button"
              className={
                moduleFilter === item.id ? "ai-chat-fusion-filter active" : "ai-chat-fusion-filter"
              }
              disabled={disabled}
              onClick={() => setModuleFilter(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
      ) : null}

      {filteredSources.length === 0 ? (
        <p className="ai-chat-fusion-empty">
          素材库暂无盘面. 可在左侧「历史记录 - 排盘档案」加载八字或紫微盘, 也可在预测模块排盘后自动入库.
        </p>
      ) : (
        <div className="ai-chat-fusion-list">
          {filteredSources.map((item) => {
            const checked = selectedIds.includes(item.sourceId);
            const hasSummary = Boolean(item.summaryPlain || item.summaryProfessional);
            return (
              <div
                key={item.sourceId}
                className={checked ? "ai-chat-fusion-card selected" : "ai-chat-fusion-card"}
              >
                <label className="ai-chat-fusion-card-main">
                  <input
                    type="checkbox"
                    checked={checked}
                    disabled={disabled}
                    onChange={() => onToggle(item.sourceId)}
                  />
                  <span className="ai-chat-fusion-card-body">
                    <span className="ai-chat-fusion-card-title">{item.title}</span>
                    <span className="ai-chat-fusion-card-tags">
                      <span className="ai-chat-fusion-tag">{item.moduleLabel}</span>
                      {hasSummary ? (
                        <span className="ai-chat-fusion-tag muted">含解读摘要</span>
                      ) : (
                        <span className="ai-chat-fusion-tag muted">仅盘面</span>
                      )}
                    </span>
                    {item.question ? (
                      <span className="ai-chat-fusion-card-question">{item.question}</span>
                    ) : null}
                    {item.subtitle ? (
                      <span className="ai-chat-fusion-card-subtitle">{item.subtitle}</span>
                    ) : null}
                  </span>
                </label>
                <button
                  type="button"
                  className="ai-chat-fusion-remove"
                  disabled={disabled}
                  title="删除素材"
                  aria-label="删除素材"
                  onClick={() => onRemove(item.sourceId)}
                >
                  删除
                </button>
              </div>
            );
          })}
        </div>
      )}

      <button
        type="button"
        className="product-gold-button ai-chat-fusion-create"
        disabled={!canCreate}
        onClick={onCreateFusion}
      >
        创建融合分析
      </button>
      {selectedCount > 0 && selectedCount < 2 ? (
        <p className="ai-chat-fusion-hint">请至少选择 2 个盘面素材.</p>
      ) : null}
    </section>
  );
}

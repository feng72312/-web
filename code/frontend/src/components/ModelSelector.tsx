import { useEffect, useRef, useState } from "react";
import { fetchQuotaStatus, type TierQuota } from "../services/quotaApi";
import { resolveModelTier, sortModelsByTier, tierClassName } from "../utils/modelTier";

export interface ModelOption {
  id: string;
  label: string;
  tag: string;
  provider: string;
  tier?: string;
  tierRank?: number;
}

interface ModelSelectorProps {
  models: ModelOption[];
  value: string;
  disabled?: boolean;
  onChange: (modelId: string) => void;
}

export function ModelSelector({
  models,
  value,
  disabled = false,
  onChange,
}: ModelSelectorProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [tierQuotas, setTierQuotas] = useState<TierQuota[]>([]);
  const rootRef = useRef<HTMLDivElement | null>(null);

  const sortedModels = sortModelsByTier(models);
  const selected = sortedModels.find((item) => item.id === value) ?? sortedModels[0];
  const selectedTier = selected ? resolveModelTier(selected) : null;
  const filtered = sortedModels.filter((item) => {
    const tier = resolveModelTier(item).tier;
    return tier.includes(query.trim());
  });

  useEffect(() => {
    if (!open) {
      return;
    }
    fetchQuotaStatus()
      .then((status) => setTierQuotas(status.tierQuotas ?? []))
      .catch(() => setTierQuotas([]));
  }, [open]);

  const tierRemaining = (tierName: string): number | null => {
    const row = tierQuotas.find((item) => item.tier === tierName);
    return row ? row.remaining : null;
  };

  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  if (!selected || models.length === 0) {
    return null;
  }

  return (
    <div className="model-selector" ref={rootRef}>
      <button
        type="button"
        className="model-selector-trigger"
        disabled={disabled}
        onClick={() => setOpen((prev) => !prev)}
        aria-label={`当前解读等级: ${selectedTier?.tier ?? ""}`}
      >
        {selectedTier && (
          <span className={`model-selector-tier tier-${tierClassName(selectedTier.tier)}`}>
            {selectedTier.tier}
          </span>
        )}
        <span className="model-selector-chevron">{open ? "^" : "v"}</span>
      </button>

      {open && (
        <div className="model-selector-menu">
          <input
            className="model-selector-search"
            type="text"
            placeholder="搜索等级"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <div className="model-selector-list">
            {filtered.map((item) => {
              const tier = resolveModelTier(item);
              const remaining = tierRemaining(tier.tier);
              return (
                <button
                  key={item.id}
                  type="button"
                  className={
                    item.id === value
                      ? "model-selector-item active"
                      : "model-selector-item"
                  }
                  onClick={() => {
                    onChange(item.id);
                    setOpen(false);
                    setQuery("");
                  }}
                >
                  <span className={`model-selector-tier tier-${tierClassName(tier.tier)}`}>
                    {tier.tier}
                  </span>
                  {remaining != null && (
                    <span className="model-selector-item-tag">今日剩 {remaining} 次</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

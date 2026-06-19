import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
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

const MENU_WIDTH = 320;
const MENU_MAX_HEIGHT = 320;

function computeMenuRect(trigger: HTMLElement, itemCount: number) {
  const rect = trigger.getBoundingClientRect();
  const width = Math.min(MENU_WIDTH, window.innerWidth - 16);
  let left = rect.left;
  if (left + width > window.innerWidth - 8) {
    left = Math.max(8, window.innerWidth - width - 8);
  }

  const estimatedHeight = Math.min(MENU_MAX_HEIGHT, itemCount * 52 + 56);
  const gap = 6;
  let top = rect.bottom + gap;
  if (top + estimatedHeight > window.innerHeight - 8) {
    top = Math.max(8, rect.top - gap - estimatedHeight);
  }

  return { top, left, width };
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
  const [menuRect, setMenuRect] = useState<{ top: number; left: number; width: number } | null>(
    null,
  );
  const rootRef = useRef<HTMLDivElement | null>(null);
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);

  const sortedModels = sortModelsByTier(models);
  const selected = sortedModels.find((item) => item.id === value) ?? sortedModels[0];
  const selectedTier = selected ? resolveModelTier(selected) : null;
  const filtered = sortedModels.filter((item) => {
    const tier = resolveModelTier(item).tier;
    return tier.includes(query.trim());
  });

  const updateMenuRect = useCallback(() => {
    if (!triggerRef.current) {
      return;
    }
    setMenuRect(computeMenuRect(triggerRef.current, filtered.length));
  }, [filtered.length]);

  useEffect(() => {
    if (!open) {
      setMenuRect(null);
      return;
    }
    updateMenuRect();
    window.addEventListener("resize", updateMenuRect);
    window.addEventListener("scroll", updateMenuRect, true);
    return () => {
      window.removeEventListener("resize", updateMenuRect);
      window.removeEventListener("scroll", updateMenuRect, true);
    };
  }, [open, updateMenuRect]);

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
    if (!open) {
      return;
    }
    const handleClick = (event: MouseEvent) => {
      const target = event.target as Node;
      if (rootRef.current?.contains(target) || menuRef.current?.contains(target)) {
        return;
      }
      setOpen(false);
    };
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("mousedown", handleClick);
      document.removeEventListener("keydown", handleKey);
    };
  }, [open]);

  if (!selected || models.length === 0) {
    return null;
  }

  const menu = open && menuRect
    ? createPortal(
        <div
          ref={menuRef}
          className="model-selector-menu model-selector-menu-portal"
          style={{
            top: menuRect.top,
            left: menuRect.left,
            width: menuRect.width,
          }}
          role="listbox"
          aria-label="AI 解读等级"
        >
          <input
            className="model-selector-search"
            type="text"
            placeholder="搜索等级"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <div className="model-selector-list">
            {filtered.length === 0 && (
              <p className="model-selector-empty">没有匹配的等级</p>
            )}
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
        </div>,
        document.body,
      )
    : null;

  return (
    <div className="model-selector" ref={rootRef}>
      <button
        ref={triggerRef}
        type="button"
        className="model-selector-trigger"
        disabled={disabled}
        aria-expanded={open}
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
      {menu}
    </div>
  );
}

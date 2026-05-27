import { useEffect, useRef, useState } from "react";

export interface ModelOption {
  id: string;
  label: string;
  tag: string;
  provider: string;
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
  const rootRef = useRef<HTMLDivElement | null>(null);

  const selected = models.find((item) => item.id === value) ?? models[0];
  const filtered = models.filter((item) => {
    const haystack = `${item.label} ${item.tag} ${item.id}`.toLowerCase();
    return haystack.includes(query.trim().toLowerCase());
  });

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
      >
        <span className="model-selector-name">{selected.label}</span>
        <span className="model-selector-tag">{selected.tag}</span>
        <span className="model-selector-chevron">{open ? "^" : "v"}</span>
      </button>

      {open && (
        <div className="model-selector-menu">
          <input
            className="model-selector-search"
            type="text"
            placeholder="Search models"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <div className="model-selector-list">
            {filtered.map((item) => (
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
                <span className="model-selector-item-label">{item.label}</span>
                <span className="model-selector-item-tag">{item.tag}</span>
                {item.id === value && (
                  <span className="model-selector-check">OK</span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

import type { UtilityId } from "./registry";
import { UTILITY_ITEMS } from "./registry";

interface Props {
  activeId: UtilityId;
  onSelect: (id: UtilityId) => void;
}

export function UtilityNav({ activeId, onSelect }: Props) {
  return (
    <nav className="utility-nav" aria-label="实用工具">
      {UTILITY_ITEMS.map((item) => (
        <button
          key={item.id}
          type="button"
          className={activeId === item.id ? "utility-nav-btn active" : "utility-nav-btn"}
          onClick={() => onSelect(item.id)}
        >
          {item.label}
          {!item.enabled && <span className="view-nav-tag">待开发</span>}
        </button>
      ))}
    </nav>
  );
}

import type { UtilityItem } from "./registry";

interface Props {
  item: UtilityItem;
}

export function UtilityPlaceholder({ item }: Props) {
  return (
    <section className="panel placeholder-panel utility-placeholder">
      <h2>{item.label}</h2>
      <p className="hint">{item.description}</p>
      <p className="hint">该工具开发中, 敬请期待.</p>
    </section>
  );
}

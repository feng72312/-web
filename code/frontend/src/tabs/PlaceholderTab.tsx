interface Props {
  title: string;
}

export function PlaceholderTab({ title }: Props) {
  return (
    <section className="panel placeholder-panel">
      <h2>{title}</h2>
      <p className="hint">该术数模块开发中, 敬请期待.</p>
    </section>
  );
}

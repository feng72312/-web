interface Props {
  shenSha: Record<string, string>;
}

export function ShenShaPanel({ shenSha }: Props) {
  const entries = Object.entries(shenSha);
  if (!entries.length) return null;
  return (
    <div className="liuren-shensha panel-block">
      <h3>神煞</h3>
      <ul className="shensha-list">
        {entries.map(([k, v]) => (
          <li key={k}>
            <span className="sha-name">{k}</span>
            <span>{v}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

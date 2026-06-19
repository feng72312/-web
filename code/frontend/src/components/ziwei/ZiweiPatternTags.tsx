interface ZiweiPatternTagsProps {
  labels: string[];
}

export function ZiweiPatternTags({ labels }: ZiweiPatternTagsProps) {
  if (!labels.length) {
    return null;
  }
  return (
    <div className="ziwei-pattern-tags">
      <span className="ziwei-pattern-tags-label">格局</span>
      {labels.map((label) => (
        <span key={label} className="ziwei-pattern-tag">
          {label}
        </span>
      ))}
    </div>
  );
}

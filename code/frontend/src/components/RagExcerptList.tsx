interface RagExcerptItem {
  source?: string;
  excerpt?: string;
}

interface RagExcerptListProps {
  excerpts?: RagExcerptItem[] | null;
}

export function RagExcerptList({ excerpts }: RagExcerptListProps) {
  const list = excerpts ?? [];
  if (!list.length) {
    return null;
  }

  return (
    <>
      {list.map((item, idx) => (
        <blockquote key={idx} className="excerpt">
          <cite>{idx + 1}</cite>
          {item.excerpt && <p>{item.excerpt}</p>}
        </blockquote>
      ))}
    </>
  );
}

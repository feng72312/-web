interface RagExcerptItem {
  source?: string;
  excerpt?: string;
}

interface RagExcerptListProps {
  excerpts: RagExcerptItem[];
}

export function RagExcerptList({ excerpts }: RagExcerptListProps) {
  if (!excerpts.length) {
    return null;
  }

  return (
    <>
      {excerpts.map((item, idx) => (
        <blockquote key={idx} className="excerpt">
          <cite>{idx + 1}</cite>
          {item.excerpt && <p>{item.excerpt}</p>}
        </blockquote>
      ))}
    </>
  );
}

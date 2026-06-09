interface RagExcerptItem {
  source?: string;
  excerpt?: string;
  classic?: string;
  chapter?: string;
  score?: number;
  rerankScore?: number;
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
      {list.map((item, idx) => {
        const cite =
          item.classic && item.chapter
            ? `《${item.classic}》${item.chapter}`
            : item.classic
              ? `《${item.classic}》`
              : item.source?.trim() || `${idx + 1}`;
        const score =
          item.rerankScore ?? item.score;
        return (
          <blockquote key={idx} className="excerpt">
            <cite>
              {cite}
              {typeof score === "number" ? ` (${score})` : ""}
            </cite>
            {item.excerpt && <p>{item.excerpt}</p>}
          </blockquote>
        );
      })}
    </>
  );
}

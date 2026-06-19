import { RagExcerptList } from "./RagExcerptList";

interface ClassicIndexItem {
  source?: string;
  excerpt?: string;
  classic?: string;
  chapter?: string;
  score?: number;
  rerankScore?: number;
}

interface ClassicIndexPanelProps {
  query?: string | null;
  excerpts?: ClassicIndexItem[] | null;
  defaultOpen?: boolean;
}

export function ClassicIndexPanel({
  query,
  excerpts,
  defaultOpen = false,
}: ClassicIndexPanelProps) {
  const list = (excerpts ?? []).filter(
    (item) => item.excerpt?.trim() || item.source?.trim() || item.classic?.trim(),
  );
  const trimmedQuery = query?.trim();
  if (!trimmedQuery && !list.length) {
    return null;
  }

  const summaryLabel =
    list.length > 0 ? `古籍索引 (${list.length}条)` : "古籍索引";

  return (
    <details className="classic-index-panel" open={defaultOpen}>
      <summary>{summaryLabel}</summary>
      <div className="classic-index-body">
        {trimmedQuery && (
          <p className="classic-index-query">
            <span className="classic-index-query-label">检索词: </span>
            <span className="mono">{trimmedQuery}</span>
          </p>
        )}
        <RagExcerptList excerpts={list} />
      </div>
    </details>
  );
}

import type { KnowledgeEvidenceItem } from "../types/bazi";
import { RagExcerptList } from "./RagExcerptList";

interface ChannelRagEvidenceProps {
  query?: string;
  excerpts?: Array<{ source?: string; excerpt?: string }> | null;
  knowledgeEvidence?: KnowledgeEvidenceItem[] | null;
  label?: string;
  defaultOpen?: boolean;
  showQuery?: boolean;
}

const AGREEMENT_LABELS: Record<string, string> = {
  unanimous: "一致",
  majority: "多数",
  disputed: "存疑",
  single_source: "单源",
};

function agreementLabel(level: string): string {
  return AGREEMENT_LABELS[level] || level;
}

export function ChannelRagEvidence({
  query,
  excerpts,
  knowledgeEvidence,
  label,
  defaultOpen = false,
  showQuery = true,
}: ChannelRagEvidenceProps) {
  const list = (excerpts ?? []).filter((item) => item.source !== "stub" && item.excerpt);
  const knowledge = (knowledgeEvidence ?? []).filter(
    (item) => item.summary || (item.claims && item.claims.length > 0),
  );
  const suffix = label ? ` (${label})` : "";
  const hasEvidence = knowledge.length > 0 || list.length > 0;
  const trimmedQuery = query?.trim();
  const totalCount = knowledge.length + list.length;
  const summaryLabel =
    totalCount > 0 ? `古籍索引${suffix} (${totalCount}条)` : `古籍索引${suffix}`;

  if (!hasEvidence && !trimmedQuery) {
    return null;
  }

  if (!hasEvidence) {
    return (
      <details className="classic-index-panel channel-rag-evidence" open={defaultOpen}>
        <summary>{summaryLabel}</summary>
        <div className="classic-index-body">
          {showQuery && trimmedQuery && (
            <p className="classic-index-query">
              <span className="classic-index-query-label">检索词: </span>
              <span className="mono">{trimmedQuery}</span>
            </p>
          )}
          <p className="channel-rag-empty">暂无典籍依据{suffix}</p>
        </div>
      </details>
    );
  }

  return (
    <details className="classic-index-panel channel-rag-evidence" open={defaultOpen}>
      <summary>{summaryLabel}</summary>
      <div className="classic-index-body">
        {showQuery && trimmedQuery && (
          <p className="classic-index-query">
            <span className="classic-index-query-label">检索词: </span>
            <span className="mono">{trimmedQuery}</span>
          </p>
        )}

        {knowledge.length > 0 && (
          <div className="channel-knowledge-evidence">
            <h5 className="channel-rag-title">典籍结论{suffix}</h5>
            {knowledge.map((item) => (
              <div key={item.id} className="knowledge-evidence-item">
                <div className="knowledge-evidence-head">
                  <span className="knowledge-evidence-topic">{item.topic}</span>
                  <span
                    className={`knowledge-evidence-agreement agreement-${item.agreementLevel}`}
                  >
                    {agreementLabel(item.agreementLevel)}
                  </span>
                  <span className="knowledge-evidence-tier">{item.sourceTier}</span>
                </div>
                {item.summary && <p className="knowledge-evidence-summary">{item.summary}</p>}
                {item.claims?.map((claim, idx) => (
                  <blockquote key={`${item.id}-${idx}`} className="excerpt knowledge-claim">
                    <cite>
                      {claim.classic}
                      {claim.chapter ? ` / ${claim.chapter}` : ""}
                    </cite>
                    {claim.quote && <p>{claim.quote}</p>}
                    {claim.conclusion && (
                      <p className="knowledge-claim-conclusion">{claim.conclusion}</p>
                    )}
                  </blockquote>
                ))}
              </div>
            ))}
          </div>
        )}

        {list.length > 0 && (
          <div className="channel-rag-excerpts">
            {knowledge.length > 0 && (
              <h5 className="channel-rag-title">原文摘录{suffix}</h5>
            )}
            <RagExcerptList excerpts={list} />
          </div>
        )}
      </div>
    </details>
  );
}

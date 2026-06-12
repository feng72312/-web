import { RagExcerptList } from "../RagExcerptList";
import type { RagStatus } from "../../services/ragApi";
import type { Interpretation } from "../../types/bazi";

interface BaziClassicReferenceProps {
  ragStatus: RagStatus | null;
  interpretation: Interpretation | null;
}

export function BaziClassicReference({ ragStatus, interpretation }: BaziClassicReferenceProps) {
  const ragExcerpts =
    interpretation?.excerpts?.filter((item) => item.source !== "stub") ?? [];
  const hasExcerpts = ragExcerpts.length > 0;

  return (
    <section className="bazi-report-card bazi-classic-reference">
      <div className="bazi-report-section-head">
        <span className="bazi-card-eyebrow">典籍</span>
        <h3>智能古籍参考</h3>
      </div>

      {ragStatus && !ragStatus.serviceOk && (
        <p className="bazi-rag-hint">典籍库未就绪: {ragStatus.serviceMessage}</p>
      )}
      {ragStatus?.serviceOk && (
        <p className="bazi-rag-hint ok">典籍库已连接, 索引约 {ragStatus.chunks} 条</p>
      )}

      {interpretation?.query && (
        <details className="bazi-classic-query" open={hasExcerpts}>
          <summary>检索问句</summary>
          <p className="mono">{interpretation.query}</p>
        </details>
      )}

      {hasExcerpts ? (
        <RagExcerptList excerpts={ragExcerpts} />
      ) : (
        <p className="bazi-classic-empty">
          完成 AI 解读后, 此处会展示与命盘相关的典籍摘录与索引结果。
        </p>
      )}
    </section>
  );
}

import { ChannelRagEvidence } from "../ChannelRagEvidence";
import { ClassicIndexPanel } from "../ClassicIndexPanel";
import { RagExcerptList } from "../RagExcerptList";
import type { RagStatus } from "../../services/ragApi";
import type { Interpretation } from "../../types/bazi";

interface BaziClassicReferenceProps {
  ragStatus: RagStatus | null;
  interpretation: Interpretation | null;
}

function asExcerptList(rows?: Array<Record<string, unknown>>) {
  if (!rows?.length) return [];
  return rows.map((row) => ({
    source: String(row.source ?? row.classic ?? "未知来源"),
    excerpt: String(row.excerpt ?? ""),
    authorityTier: row.authorityTier ? String(row.authorityTier) : undefined,
    evidenceRole: row.evidenceRole ? String(row.evidenceRole) : undefined,
  }));
}

export function BaziClassicReference({ ragStatus, interpretation }: BaziClassicReferenceProps) {
  const tiered = interpretation?.tieredEvidence ?? interpretation?.judgement?.tieredEvidence;
  const primary = asExcerptList(tiered?.primaryEvidence);
  const secondary = asExcerptList(tiered?.secondaryEvidence);
  const caseRef = asExcerptList(tiered?.caseReference);
  const excluded = asExcerptList(tiered?.excludedOrLowTrust);
  const fallbackExcerpts =
    interpretation?.excerpts?.filter((item) => item.source !== "stub") ?? [];
  const hasTiered = primary.length + secondary.length + caseRef.length + excluded.length > 0;
  const hasKnowledge = (interpretation?.knowledgeEvidence?.length ?? 0) > 0;

  return (
    <section className="bazi-report-card bazi-classic-reference">
      <div className="bazi-report-section-head">
        <span className="bazi-card-eyebrow">典籍</span>
        <h3>古籍参考</h3>
      </div>

      {ragStatus && !ragStatus.serviceOk && (
        <p className="bazi-rag-hint">典籍库未就绪: {ragStatus.serviceMessage}</p>
      )}
      {ragStatus?.serviceOk && (
        <p className="bazi-rag-hint ok">典籍库已连接, 索引约 {ragStatus.chunks} 条</p>
      )}

      {hasKnowledge && (
        <ChannelRagEvidence
          query={interpretation?.query}
          knowledgeEvidence={interpretation?.knowledgeEvidence}
          label="结构化典籍"
          showQuery={Boolean(interpretation?.query && !hasTiered && !fallbackExcerpts.length)}
        />
      )}

      {hasTiered ? (
        <details className="classic-index-panel bazi-tiered-evidence">
          <summary>
            古籍索引 (
            {primary.length + secondary.length + caseRef.length + excluded.length}条)
          </summary>
          <div className="classic-index-body">
            {interpretation?.query && (
              <p className="classic-index-query">
                <span className="classic-index-query-label">检索词: </span>
                <span className="mono">{interpretation.query}</span>
              </p>
            )}
            {primary.length > 0 && (
              <details>
                <summary>主裁典籍 ({primary.length}条)</summary>
                <RagExcerptList excerpts={primary} />
              </details>
            )}
            {secondary.length > 0 && (
              <details>
                <summary>辅助古籍 ({secondary.length}条)</summary>
                <RagExcerptList excerpts={secondary} />
              </details>
            )}
            {caseRef.length > 0 && (
              <details>
                <summary>案例参考 ({caseRef.length}条)</summary>
                <RagExcerptList excerpts={caseRef} />
              </details>
            )}
            {excluded.length > 0 && (
              <details>
                <summary>不参与裁判资料 ({excluded.length}条)</summary>
                <RagExcerptList excerpts={excluded} />
              </details>
            )}
          </div>
        </details>
      ) : fallbackExcerpts.length > 0 ? (
        <ClassicIndexPanel
          query={interpretation?.query}
          excerpts={fallbackExcerpts}
        />
      ) : !hasKnowledge ? (
        <p className="bazi-classic-empty">
          完成 AI 解读后, 此处会展示主裁典籍、辅助古籍、案例参考与证据链。
        </p>
      ) : null}
    </section>
  );
}

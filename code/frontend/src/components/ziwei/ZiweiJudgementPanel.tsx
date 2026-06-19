import type {
  ZiweiJudgementReport,
  ZiweiTieredEvidence,
} from "../../types/ziwei";
import { ZIWEI_JUDGE_ROLE_LABELS, ZIWEI_TIERED_BUCKET_LABELS } from "../../types/ziwei";
import {
  JudgementFoldShell,
  JudgementSubFold,
  formatConfidenceBand,
} from "../JudgementFoldShell";
import { localizeJudgementText, translateJudgeRole } from "../../utils/judgementDisplay";

interface ZiweiJudgementPanelProps {
  judgement?: ZiweiJudgementReport | null;
  loading?: boolean;
}

function renderTieredBucket(
  bucket: keyof ZiweiTieredEvidence,
  rows: Array<{ source: string; excerpt: string; authorityTier?: string }>,
) {
  if (!rows.length) {
    return null;
  }
  return (
    <div className="ziwei-tiered-bucket">
      <h5>{ZIWEI_TIERED_BUCKET_LABELS[bucket] ?? bucket}</h5>
      <ul>
        {rows.slice(0, 5).map((row, index) => (
          <li key={`${bucket}-${row.source}-${index}`}>
            <strong>{row.source}</strong>
            <p>{row.excerpt}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

function buildFoldHint(judgement: ZiweiJudgementReport): string {
  const parts: string[] = [];
  if (judgement.topic?.topicLabel) {
    parts.push(judgement.topic.topicLabel);
  }
  const band = judgement.arbitration?.confidenceBand;
  if (band) {
    const score =
      judgement.arbitration?.confidenceScore != null
        ? ` ${Math.round(judgement.arbitration.confidenceScore * 100)}%`
        : "";
    parts.push(`置信${formatConfidenceBand(band)}${score}`);
  }
  if (judgement.arbitration?.summary) {
    parts.push(localizeJudgementText(judgement.arbitration.summary));
  }
  return parts.join(" / ");
}

function countTieredRows(tiered: ZiweiTieredEvidence): number {
  return (
    (tiered.primaryEvidence?.length ?? 0)
    + (tiered.secondaryEvidence?.length ?? 0)
    + (tiered.schoolCommentary?.length ?? 0)
    + (tiered.caseReference?.length ?? 0)
    + (tiered.excludedOrUnreadable?.length ?? 0)
  );
}

export function ZiweiJudgementPanel({ judgement, loading }: ZiweiJudgementPanelProps) {
  if (loading) {
    return (
      <section className="bazi-report-card bazi-judgement-panel ziwei-judgement-panel">
        <p className="bazi-judgement-overview-line">判盘链计算中...</p>
      </section>
    );
  }

  if (!judgement) {
    return null;
  }

  const steps = judgement.steps ?? [];
  const judges = judgement.judges ?? [];
  const arbitration = judgement.arbitration;
  const tiered = judgement.tieredEvidence ?? {};
  const tieredCount = countTieredRows(tiered);
  const hasNotes =
    (arbitration?.conflicts?.length ?? 0) > 0 || (arbitration?.finalBoundaries?.length ?? 0) > 0;

  return (
    <JudgementFoldShell
      title="紫微判盘链"
      hint={buildFoldHint(judgement)}
      className="bazi-report-card bazi-judgement-panel ziwei-judgement-panel"
    >
      {judges.length > 0 && (
        <div className="ziwei-judge-opinions">
          <h4>裁判结论</h4>
          <ul>
            {judges.map((judge) => (
              <li key={`${judge.role}-${judge.summary.slice(0, 24)}`}>
                <strong>{translateJudgeRole(judge.role, ZIWEI_JUDGE_ROLE_LABELS)}</strong>
                <p>{localizeJudgementText(judge.summary)}</p>
                {judge.boundary ? (
                  <p className="bazi-judge-boundary">{localizeJudgementText(judge.boundary)}</p>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      )}

      {hasNotes && (
        <JudgementSubFold
          title={`需留意 (${(arbitration?.conflicts?.length ?? 0) + (arbitration?.finalBoundaries?.length ?? 0)})`}
        >
          {(arbitration?.conflicts?.length ?? 0) > 0 && (
            <div className="bazi-judgement-conflicts">
              <h5>观点冲突</h5>
              <ul>
                {arbitration!.conflicts!.map((item) => (
                  <li key={item}>{localizeJudgementText(item)}</li>
                ))}
              </ul>
            </div>
          )}
          {(arbitration?.finalBoundaries?.length ?? 0) > 0 && (
            <div className="bazi-judgement-boundaries">
              <h5>结论边界</h5>
              <ul>
                {arbitration!.finalBoundaries!.map((item) => (
                  <li key={item}>{localizeJudgementText(item)}</li>
                ))}
              </ul>
            </div>
          )}
        </JudgementSubFold>
      )}

      {tieredCount > 0 && (
        <JudgementSubFold title={`典籍依据 (${tieredCount}条)`}>
          <div className="ziwei-tiered-evidence">
            {renderTieredBucket("primaryEvidence", tiered.primaryEvidence ?? [])}
            {renderTieredBucket("secondaryEvidence", tiered.secondaryEvidence ?? [])}
            {renderTieredBucket("schoolCommentary", tiered.schoolCommentary ?? [])}
            {renderTieredBucket("caseReference", tiered.caseReference ?? [])}
            {renderTieredBucket("excludedOrUnreadable", tiered.excludedOrUnreadable ?? [])}
          </div>
        </JudgementSubFold>
      )}

      {steps.length > 0 && (
        <JudgementSubFold title={`分析过程 (${steps.length}步)`}>
          <div className="bazi-judgement-steps">
            <ul>
              {steps.map((step) => (
                <li key={step.id}>
                  <strong>{step.label}</strong>
                  <p>{localizeJudgementText(step.summary)}</p>
                </li>
              ))}
            </ul>
          </div>
        </JudgementSubFold>
      )}
    </JudgementFoldShell>
  );
}

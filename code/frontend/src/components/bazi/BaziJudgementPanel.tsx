import { useEffect, useRef } from "react";
import type { BaziJudgementReport } from "../../types/bazi";
import {
  JudgementFoldShell,
  JudgementSubFold,
  formatConfidenceBand,
} from "../JudgementFoldShell";
import {
  BAZI_JUDGE_ROLE_LABELS,
  localizeJudgementText,
  translateJudgeRole,
} from "../../utils/judgementDisplay";

interface BaziJudgementPanelProps {
  judgement?: BaziJudgementReport | null;
  panelRef?: React.MutableRefObject<HTMLElement | null>;
  highlightRuleId?: string | null;
}

const GEJU_EVIDENCE_GROUP_ORDER = ["月令格局", "成败救应", "杂格外格", "其他"] as const;
const SUIYUN_EVIDENCE_GROUP_ORDER = ["大运干支", "岁运总则", "流年规则", "流年事件", "三命流年", "其他"] as const;

function ruleIdMatches(raw: string | undefined, target: string): boolean {
  if (!raw || !target) {
    return false;
  }
  return raw.split(",").map((part) => part.trim()).includes(target);
}

function evidenceItemRuleId(item: NonNullable<BaziJudgementReport["evidenceChain"]>[number]): string {
  return String(item.ruleId || "").split(",")[0]?.trim() || "";
}

function parseGejuEvidenceGroup(conclusion: string): string | null {
  const idx = conclusion.indexOf(":");
  if (idx <= 0) {
    return null;
  }
  const label = conclusion.slice(0, idx).trim();
  return GEJU_EVIDENCE_GROUP_ORDER.includes(label as (typeof GEJU_EVIDENCE_GROUP_ORDER)[number])
    ? label
    : null;
}

function parseSuiyunEvidenceGroup(conclusion: string): string | null {
  const idx = conclusion.indexOf(":");
  if (idx <= 0) {
    return null;
  }
  const label = conclusion.slice(0, idx).trim();
  return SUIYUN_EVIDENCE_GROUP_ORDER.includes(label as (typeof SUIYUN_EVIDENCE_GROUP_ORDER)[number])
    ? label
    : null;
}

function parseTiaohouEvidenceGroup(conclusion: string): boolean {
  return conclusion.startsWith("调候:");
}

function isInteractionsEvidence(
  item: NonNullable<BaziJudgementReport["evidenceChain"]>[number],
): boolean {
  return (
    item.conclusion.startsWith("合冲刑害:")
    || Boolean(item.ruleId?.startsWith("interactions:"))
    || item.primaryClassic === "神峰通考"
  );
}

function partitionEvidenceChain(evidenceChain: NonNullable<BaziJudgementReport["evidenceChain"]>) {
  const gejuGroups = new Map<string, typeof evidenceChain>();
  const suiyunGroups = new Map<string, typeof evidenceChain>();
  const tiaohouItems: typeof evidenceChain = [];
  const interactionItems: typeof evidenceChain = [];
  const otherItems: typeof evidenceChain = [];

  for (const item of evidenceChain) {
    const gejuGroup = parseGejuEvidenceGroup(item.conclusion);
    if (gejuGroup && item.primaryClassic === "子平真诠") {
      const rows = gejuGroups.get(gejuGroup) ?? [];
      rows.push(item);
      gejuGroups.set(gejuGroup, rows);
      continue;
    }
    if (parseTiaohouEvidenceGroup(item.conclusion) || item.primaryClassic === "穷通宝鉴") {
      tiaohouItems.push(item);
      continue;
    }
    const suiyunGroup = parseSuiyunEvidenceGroup(item.conclusion);
    if (
      suiyunGroup
      || item.ruleId?.startsWith("liunian:")
      || item.ruleId?.startsWith("suiyun:")
      || item.primaryClassic === "三命通会"
      || item.primaryClassic === "命理探源"
    ) {
      const label = suiyunGroup || "其他";
      const rows = suiyunGroups.get(label) ?? [];
      rows.push(item);
      suiyunGroups.set(label, rows);
      continue;
    }
    if (isInteractionsEvidence(item)) {
      interactionItems.push(item);
      continue;
    }
    otherItems.push(item);
  }

  return { gejuGroups, suiyunGroups, tiaohouItems, interactionItems, otherItems };
}

function renderEvidenceItem(
  item: NonNullable<BaziJudgementReport["evidenceChain"]>[number],
  key: string,
  highlightRuleId?: string | null,
) {
  const gejuGroup = parseGejuEvidenceGroup(item.conclusion);
  const suiyunGroup = parseSuiyunEvidenceGroup(item.conclusion);
  const tiaohouGroup = parseTiaohouEvidenceGroup(item.conclusion);
  const headline = gejuGroup || suiyunGroup || (tiaohouGroup ? "调候" : item.primaryClassic || "依据");
  const body = gejuGroup || suiyunGroup || tiaohouGroup
    ? item.conclusion.slice(item.conclusion.indexOf(":") + 1).trim()
    : item.conclusion;
  const ruleId = evidenceItemRuleId(item);
  const highlighted = ruleIdMatches(item.ruleId, highlightRuleId || "");

  return (
    <li
      key={key}
      data-rule-id={ruleId || undefined}
      className={highlighted ? "bazi-evidence-highlight" : undefined}
    >
      <strong>{headline}</strong>
      <p>{body}</p>
      {item.quote && <blockquote className="bazi-evidence-quote">{item.quote}</blockquote>}
      {item.boundary && <p className="bazi-judge-boundary">{item.boundary}</p>}
    </li>
  );
}

function buildFoldHint(judgement: BaziJudgementReport): string {
  const parts: string[] = [];
  const band = judgement.arbitration?.confidenceBand;
  if (band) {
    const score =
      judgement.arbitration?.confidenceScore != null
        ? ` ${Math.round(judgement.arbitration.confidenceScore * 100)}%`
        : "";
    parts.push(`置信${formatConfidenceBand(band)}${score}`);
  }
  const steps = judgement.steps ?? [];
  if (steps.length > 0) {
    parts.push(steps.map((step) => step.label).join(" -> "));
  }
  return parts.join(" / ");
}

function renderEvidenceSections(
  evidenceChain: NonNullable<BaziJudgementReport["evidenceChain"]>,
  highlightRuleId?: string | null,
) {
  const { gejuGroups, suiyunGroups, tiaohouItems, interactionItems, otherItems } =
    partitionEvidenceChain(evidenceChain);

  return (
    <>
      {tiaohouItems.length > 0 && (
        <div className="bazi-evidence-tiaohou-groups">
          <h5>调候 (穷通宝鉴)</h5>
          <ul>
            {tiaohouItems.map((item) =>
              renderEvidenceItem(
                item,
                `tiaohou-${item.ruleId}-${item.conclusion.slice(0, 24)}`,
                highlightRuleId,
              ),
            )}
          </ul>
        </div>
      )}
      {suiyunGroups.size > 0 && (
        <div className="bazi-evidence-suiyun-groups">
          <h5>岁运 (三命通会/命理探源)</h5>
          {SUIYUN_EVIDENCE_GROUP_ORDER.map((label) => {
            const items = suiyunGroups.get(label);
            if (!items || items.length === 0) {
              return null;
            }
            return (
              <div key={label} className="bazi-evidence-geju-group">
                <h6>{label}</h6>
                <ul>
                  {items.map((item) =>
                    renderEvidenceItem(
                      item,
                      `${label}-${item.ruleId}-${item.conclusion.slice(0, 24)}`,
                      highlightRuleId,
                    ),
                  )}
                </ul>
              </div>
            );
          })}
        </div>
      )}
      {gejuGroups.size > 0 && (
        <div className="bazi-evidence-geju-groups">
          <h5>格局 (子平真诠)</h5>
          {GEJU_EVIDENCE_GROUP_ORDER.map((label) => {
            const items = gejuGroups.get(label);
            if (!items || items.length === 0) {
              return null;
            }
            return (
              <div key={label} className="bazi-evidence-geju-group">
                <h6>{label}</h6>
                <ul>
                  {items.map((item) =>
                    renderEvidenceItem(
                      item,
                      `${label}-${item.ruleId}-${item.conclusion.slice(0, 24)}`,
                      highlightRuleId,
                    ),
                  )}
                </ul>
              </div>
            );
          })}
        </div>
      )}
      {interactionItems.length > 0 && (
        <div className="bazi-evidence-interactions-groups">
          <h5>合冲刑害与神煞</h5>
          <ul>
            {interactionItems.map((item) =>
              renderEvidenceItem(
                item,
                `interaction-${item.ruleId}-${item.conclusion.slice(0, 24)}`,
                highlightRuleId,
              ),
            )}
          </ul>
        </div>
      )}
      {otherItems.length > 0 && (
        <ul>
          {otherItems.map((item) =>
            renderEvidenceItem(
              item,
              `${item.ruleId}-${item.conclusion.slice(0, 24)}`,
              highlightRuleId,
            ),
          )}
        </ul>
      )}
    </>
  );
}

export function BaziJudgementPanel({
  judgement,
  panelRef,
  highlightRuleId,
}: BaziJudgementPanelProps) {
  const localRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!highlightRuleId || !localRef.current) {
      return;
    }
    const target = localRef.current.querySelector(
      `[data-rule-id="${CSS.escape(highlightRuleId)}"]`,
    );
    if (target instanceof HTMLElement) {
      target.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [highlightRuleId]);

  if (!judgement) {
    return null;
  }

  const steps = judgement.steps ?? [];
  const opinions = judgement.arbitration?.judgeOpinions ?? [];
  const primaryOpinions = opinions.filter((item) => item.role !== "case");
  const conflicts = judgement.arbitration?.conflicts ?? [];
  const boundaries = judgement.arbitration?.finalBoundaries ?? [];
  const evidenceChain = judgement.evidenceChain ?? [];
  const hasNotes = conflicts.length > 0 || boundaries.length > 0;

  const setSectionRef = (node: HTMLElement | null) => {
    localRef.current = node;
    if (panelRef) {
      panelRef.current = node;
    }
  };

  return (
    <JudgementFoldShell
      id="bazi-judgement-panel"
      title="判盘链总览"
      hint={buildFoldHint(judgement)}
      forceOpen={Boolean(highlightRuleId)}
      sectionRef={setSectionRef}
    >
      {primaryOpinions.length > 0 && (
        <div className="bazi-judge-opinions">
          <h4>裁判结论</h4>
          <ul>
            {primaryOpinions.map((opinion) => (
              <li key={`${opinion.role}-${opinion.classic}`}>
                <strong>
                  {translateJudgeRole(opinion.role, BAZI_JUDGE_ROLE_LABELS)}
                  {opinion.classic ? ` / ${opinion.classic}` : ""}
                </strong>
                <p>{localizeJudgementText(opinion.summary)}</p>
                {opinion.boundary && (
                  <p className="bazi-judge-boundary">{localizeJudgementText(opinion.boundary)}</p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {hasNotes && (
        <JudgementSubFold title={`需留意 (${conflicts.length + boundaries.length})`}>
          {conflicts.length > 0 && (
            <div className="bazi-judgement-conflicts">
              <h5>观点冲突</h5>
              <ul>
                {conflicts.map((item) => (
                  <li key={item}>{localizeJudgementText(item)}</li>
                ))}
              </ul>
            </div>
          )}
          {boundaries.length > 0 && (
            <div className="bazi-judgement-boundaries">
              <h5>结论边界</h5>
              <ul>
                {boundaries.map((item) => (
                  <li key={item}>{localizeJudgementText(item)}</li>
                ))}
              </ul>
            </div>
          )}
        </JudgementSubFold>
      )}

      {evidenceChain.length > 0 && (
        <JudgementSubFold
          title={`典籍依据 (${evidenceChain.length}条)`}
          defaultOpen={Boolean(highlightRuleId)}
        >
          <div className="bazi-evidence-chain">
            {renderEvidenceSections(evidenceChain, highlightRuleId)}
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

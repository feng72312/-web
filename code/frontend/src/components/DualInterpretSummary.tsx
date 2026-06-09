import type { DualInterpretSummaries } from "../utils/interpretStyle";
import type { ConsensusPayload } from "../types/consensus";
import { sanitizeInterpretText } from "../utils/sanitizeInterpret";
import { ConsensusPanel } from "./ConsensusPanel";
import { CopyTextButton } from "./CopyTextButton";
import { InterpretBlock } from "./InterpretBlock";
import { InterpretMarkdown } from "./InterpretMarkdown";
import { ConfidenceGauge } from "./viz/ConfidenceGauge";

interface DualInterpretSummaryProps {
  title: string;
  interpretation: DualInterpretSummaries & {
    consensus?: ConsensusPayload;
    questionConsensus?: ConsensusPayload;
    confidenceBand?: ConsensusPayload["confidenceBand"];
    confidenceScore?: number;
  };
  children?: React.ReactNode;
}

export function DualInterpretSummary({
  title,
  interpretation,
  children,
}: DualInterpretSummaryProps) {
  const hasPro = Boolean(interpretation.summaryProfessional);
  const hasPlain = Boolean(interpretation.summaryPlain);
  const hasLegacy = Boolean(interpretation.summary) && !hasPro && !hasPlain;

  if (!hasPro && !hasPlain && !hasLegacy && !children) {
    return null;
  }

  return (
    <section className="panel interpret-panel">
      <h2>{title}</h2>
      {hasPro && (
        <InterpretBlock
          title="命理师专用解读"
          copyText={sanitizeInterpretText(interpretation.summaryProfessional ?? "")}
        >
          <InterpretMarkdown text={interpretation.summaryProfessional ?? ""} />
        </InterpretBlock>
      )}
      {hasPlain && (
        <InterpretBlock
          title="AI深度解读"
          copyText={sanitizeInterpretText(interpretation.summaryPlain ?? "")}
        >
          <InterpretMarkdown text={interpretation.summaryPlain ?? ""} />
        </InterpretBlock>
      )}
      {!hasPro && !hasPlain && interpretation.summary && (
        <div className="interpret-block">
          <div className="interpret-block-head">
            <h3 className="interpret-block-title">解读</h3>
            <CopyTextButton text={sanitizeInterpretText(interpretation.summary)} />
          </div>
          <InterpretMarkdown text={interpretation.summary} />
        </div>
      )}
      {(interpretation.confidenceBand || interpretation.consensus) && (
        <div className="interpret-confidence-row">
          {interpretation.confidenceBand && (
            <ConfidenceGauge
              band={interpretation.confidenceBand}
              score={interpretation.confidenceScore}
            />
          )}
          <ConsensusPanel
            consensus={interpretation.consensus}
            questionConsensus={interpretation.questionConsensus}
          />
        </div>
      )}
      {children}
    </section>
  );
}

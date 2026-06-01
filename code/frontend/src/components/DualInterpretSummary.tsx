import type { DualInterpretSummaries } from "../utils/interpretStyle";
import { CopyTextButton } from "./CopyTextButton";
import { InterpretBlock } from "./InterpretBlock";

interface DualInterpretSummaryProps {
  title: string;
  interpretation: DualInterpretSummaries;
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
        <InterpretBlock title="命理师专用解读" copyText={interpretation.summaryProfessional ?? ""}>
          <p className="interpret-summary">{interpretation.summaryProfessional}</p>
        </InterpretBlock>
      )}
      {hasPlain && (
        <InterpretBlock title="AI深度解读" copyText={interpretation.summaryPlain ?? ""}>
          <p className="interpret-summary">{interpretation.summaryPlain}</p>
        </InterpretBlock>
      )}
      {!hasPro && !hasPlain && interpretation.summary && (
        <div className="interpret-block">
          <div className="interpret-block-head">
            <h3 className="interpret-block-title">解读</h3>
            <CopyTextButton text={interpretation.summary} />
          </div>
          <p className="interpret-summary">{interpretation.summary}</p>
        </div>
      )}
      {children}
    </section>
  );
}

import type { InterpretSegment } from "../../types/bazi";

interface BaziInterpretSegmentsProps {
  segments: InterpretSegment[];
  onRuleIdSelect?: (ruleId: string) => void;
}

export function BaziInterpretSegments({
  segments,
  onRuleIdSelect,
}: BaziInterpretSegmentsProps) {
  if (!segments.length) {
    return null;
  }

  return (
    <div className="bazi-interpret-segments">
      {segments.map((segment, index) => {
        const refs = segment.ruleIdRefs ?? [];
        const isInference = segment.kind === "inference";
        return (
          <article
            key={`segment-${index}`}
            className={`bazi-interpret-segment ${isInference ? "bazi-interpret-segment-inference" : "bazi-interpret-segment-anchored"}`}
          >
            <div className="bazi-interpret-segment-head">
              <span className={`bazi-interpret-segment-kind ${isInference ? "is-inference" : "is-anchored"}`}>
                {isInference ? "推断" : "有锚"}
              </span>
              {refs.length > 0 && (
                <div className="bazi-interpret-segment-refs">
                  {refs.map((ref) => (
                    <button
                      key={`${index}-${ref.ruleId}`}
                      type="button"
                      className={`bazi-rule-id-chip ${ref.verified === false ? "is-unverified" : ""}`}
                      title={ref.conclusion || ref.classic || ref.ruleId}
                      onClick={() => onRuleIdSelect?.(ref.ruleId)}
                    >
                      {ref.ruleId}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <p className="bazi-interpret-segment-text">{segment.text}</p>
          </article>
        );
      })}
    </div>
  );
}

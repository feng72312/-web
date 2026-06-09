import type { ConsensusPayload } from "../types/consensus";
import { ResultCard } from "./ui/ResultCard";

const BAND_LABEL: Record<string, string> = {
  strong: "高",
  medium: "中",
  weak: "低",
};

interface ConsensusPanelProps {
  consensus?: ConsensusPayload | null;
  questionConsensus?: ConsensusPayload | null;
}

export function ConsensusPanel({ consensus, questionConsensus }: ConsensusPanelProps) {
  if (!consensus && !questionConsensus) {
    return null;
  }

  return (
    <div className="consensus-stack">
      {consensus && <ConsensusBlock title="命盘级联判" data={consensus} />}
      {questionConsensus && (
        <ConsensusBlock title="问事级对照" data={questionConsensus} />
      )}
    </div>
  );
}

function ConsensusBlock({ title, data }: { title: string; data: ConsensusPayload }) {
  const band = data.confidenceBand ? BAND_LABEL[data.confidenceBand] ?? data.confidenceBand : "";
  return (
    <ResultCard title={title}>
      <div className="consensus-meta">
        <span>主通道: {data.leadDiscipline || "-"}</span>
        {band && <span>置信度: {band}</span>}
      </div>
      {data.consensusPoints && data.consensusPoints.length > 0 && (
        <div className="consensus-section">
          <h4>共识点</h4>
          <ul>
            {data.consensusPoints.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}
      {data.conflictPoints && data.conflictPoints.length > 0 && (
        <div className="consensus-section conflict">
          <h4>冲突点</h4>
          <ul>
            {data.conflictPoints.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
          {data.conflictExplanation && <p>{data.conflictExplanation}</p>}
        </div>
      )}
    </ResultCard>
  );
}

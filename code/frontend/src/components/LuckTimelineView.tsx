import type { LuckTimeline } from "../types/bazi";
import { LuckTimelinePanel } from "./bazi/LuckTimelinePanel";

interface Props {
  timeline: LuckTimeline;
  onBack: () => void;
}

export function LuckTimelineView({ timeline, onBack }: Props) {
  return (
    <section className="chart-detail panel luck-panel">
      <div className="chart-detail-header">
        <button type="button" className="secondary back-btn" onClick={onBack}>
          返回
        </button>
        <h2>大运流年</h2>
      </div>
      <LuckTimelinePanel timeline={timeline} />
    </section>
  );
}

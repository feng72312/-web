import { useMemo } from "react";
import { listTimelineEntries } from "../services/reportTimeline";
import { EmptyState } from "./ui/EmptyState";
import { ResultCard } from "./ui/ResultCard";

interface ReportTimelinePanelProps {
  profileId?: string;
}

export function ReportTimelinePanel({ profileId }: ReportTimelinePanelProps) {
  const entries = useMemo(() => listTimelineEntries(profileId), [profileId]);

  if (entries.length === 0) {
    return (
      <EmptyState
        title="暂无报告记录"
        description="完成解读后将自动加入时间线, 便于跨模块复盘."
      />
    );
  }

  return (
    <ResultCard title="报告时间线">
      <ul className="report-timeline">
        {entries.map((entry) => (
          <li key={entry.id} className="report-timeline-item">
            <div className="report-timeline-head">
              <span className="report-timeline-module">{entry.moduleLabel}</span>
              <time dateTime={entry.createdAt}>
                {new Date(entry.createdAt).toLocaleString()}
              </time>
            </div>
            {entry.question && <p className="report-timeline-q">问: {entry.question}</p>}
            {entry.summary && (
              <p className="report-timeline-summary">{entry.summary.slice(0, 160)}</p>
            )}
          </li>
        ))}
      </ul>
    </ResultCard>
  );
}

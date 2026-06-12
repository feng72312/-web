import type { LuckTimeline } from "../../types/bazi";
import { LuckTimelinePanel } from "./LuckTimelinePanel";

interface BaziLuckReportProps {
  luckLoading: boolean;
  luckTimeline: LuckTimeline | null;
  onOpenLuck: () => void;
}

export function BaziLuckReport({ luckLoading, luckTimeline, onOpenLuck }: BaziLuckReportProps) {
  return (
    <section className="bazi-report-card bazi-luck-report">
      <div className="bazi-report-section-head">
        <span className="bazi-card-eyebrow">运限</span>
        <h3>大运流年流月</h3>
      </div>

      {!luckTimeline ? (
        <div className="bazi-luck-empty">
          <p>大运流年数据尚未加载, 点击下方按钮获取完整运限。</p>
          <button
            type="button"
            className="bazi-gold-button"
            disabled={luckLoading}
            onClick={onOpenLuck}
          >
            {luckLoading ? "加载中..." : "加载大运流年"}
          </button>
        </div>
      ) : (
        <LuckTimelinePanel timeline={luckTimeline} />
      )}
    </section>
  );
}

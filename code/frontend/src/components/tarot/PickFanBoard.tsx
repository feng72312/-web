import { useEffect, useState } from "react";
import type { TarotDeckId } from "../../types/tarot";

interface Props {
  deckSize: number;
  cardCount: number;
  deck: TarotDeckId;
  spreadName?: string;
  question?: string;
  loading?: boolean;
  onBack?: () => void;
  onReveal: (picks: number[]) => void;
  onReshuffle: () => void;
}

export function PickFanBoard({
  deckSize,
  cardCount,
  deck,
  spreadName,
  question,
  loading,
  onBack,
  onReveal,
  onReshuffle,
}: Props) {
  const [picks, setPicks] = useState<number[]>([]);

  useEffect(() => {
    setPicks([]);
  }, [deckSize, cardCount, deck]);

  const togglePick = (index: number) => {
    if (loading) return;
    setPicks((prev) => {
      if (prev.includes(index)) {
        return prev.filter((item) => item !== index);
      }
      if (prev.length >= cardCount) {
        return prev;
      }
      return [...prev, index];
    });
  };

  return (
    <div className="tarot-pick-board">
      <div className="tarot-pick-toolbar">
        {onBack && (
          <button type="button" className="secondary" disabled={loading} onClick={onBack}>
            返回设置
          </button>
        )}
        <div className="tarot-pick-meta">
          {spreadName && <span>{spreadName}</span>}
          <span>{cardCount} 张牌</span>
        </div>
      </div>

      <div className="tarot-pick-head">
        <div>
          <h3>亲手抽牌</h3>
          <p className="hint">凝神想着你的问题, 从下方牌背中凭直觉选择 {cardCount} 张.</p>
          {question && <p className="tarot-pick-question">{question}</p>}
        </div>
        <strong className="tarot-pick-counter">
          已选 {picks.length} / {cardCount}
        </strong>
      </div>

      <div className="tarot-pick-stage">
        <div className="tarot-fan" aria-label="塔罗牌背选择区">
          {Array.from({ length: deckSize }, (_, index) => {
            const selectedIndex = picks.indexOf(index);
            const selected = selectedIndex >= 0;
            return (
              <button
                key={`${deck}-${index}`}
                type="button"
                className={selected ? "tarot-fan-card selected" : "tarot-fan-card"}
                disabled={loading || (!selected && picks.length >= cardCount)}
                onClick={() => togglePick(index)}
              >
                <span className="tarot-card-back">塔罗</span>
                {selected && <em>{selectedIndex + 1}</em>}
              </button>
            );
          })}
        </div>
      </div>

      <div className="form-actions form-actions-end tarot-pick-actions">
        <button type="button" className="secondary" disabled={loading} onClick={onReshuffle}>
          重新洗牌
        </button>
        <button
          type="button"
          className="primary-btn"
          disabled={loading || picks.length !== cardCount}
          onClick={() => onReveal(picks)}
        >
          {loading ? "揭牌中..." : "确认并翻牌"}
        </button>
      </div>
    </div>
  );
}

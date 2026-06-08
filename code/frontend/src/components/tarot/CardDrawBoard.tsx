import { useEffect, useState } from "react";
import type { DrawnCard, TarotDeckId, TarotReading } from "../../types/tarot";
import { TarotCard } from "./TarotCard";

interface Props {
  reading: TarotReading | null;
  deck: TarotDeckId;
  loading?: boolean;
  onDraw: () => void;
  onReset?: () => void;
  onRevealComplete?: (complete: boolean) => void;
}

export function CardDrawBoard({
  reading,
  deck,
  loading,
  onDraw,
  onReset,
  onRevealComplete,
}: Props) {
  const [revealedCount, setRevealedCount] = useState(0);

  useEffect(() => {
    setRevealedCount(0);
  }, [reading]);

  const cards = reading?.cards ?? [];
  const allRevealed = cards.length > 0 && revealedCount >= cards.length;

  useEffect(() => {
    onRevealComplete?.(allRevealed);
  }, [allRevealed, onRevealComplete]);

  return (
    <div className="tarot-draw-board">
      {!reading && (
        <div className="tarot-draw-empty">
          <p className="hint">确认牌系与牌阵后, 点击下方按钮洗牌抽牌.</p>
        </div>
      )}
      {reading && (
        <div className="tarot-draw-grid">
          {cards.map((card: DrawnCard, index: number) => (
            <TarotCard
              key={`${card.cardId}-${card.position}-${reading.spreadId}`}
              card={card}
              deck={deck}
              revealed={index < revealedCount}
              onReveal={() => setRevealedCount((prev) => Math.max(prev, index + 1))}
            />
          ))}
        </div>
      )}
      <div className="form-actions form-actions-end tarot-draw-actions">
        {!reading && (
          <button type="button" className="primary-btn" disabled={loading} onClick={onDraw}>
            {loading ? "抽牌中..." : "开始抽牌"}
          </button>
        )}
        {reading && !allRevealed && (
          <>
            <button
              type="button"
              className="secondary"
              onClick={() => setRevealedCount(cards.length)}
            >
              全部翻开
            </button>
            <button type="button" className="secondary" disabled={loading} onClick={onDraw}>
              {loading ? "抽牌中..." : "重新抽牌"}
            </button>
            {onReset && (
              <button type="button" className="secondary" disabled={loading} onClick={onReset}>
                清空重来
              </button>
            )}
          </>
        )}
        {reading && allRevealed && (
          <>
            <p className="hint tarot-draw-hint">牌已全部翻开, 可进行 AI 解读.</p>
            <div className="action-row tarot-redraw-row">
              <button type="button" className="secondary" onClick={() => setRevealedCount(0)}>
                重新翻牌
              </button>
              <button type="button" className="secondary" disabled={loading} onClick={onDraw}>
                {loading ? "抽牌中..." : "重新抽牌"}
              </button>
              {onReset && (
                <button type="button" className="secondary" disabled={loading} onClick={onReset}>
                  清空重来
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

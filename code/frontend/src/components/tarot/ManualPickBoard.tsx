import { useMemo, useState } from "react";
import type {
  ManualCardSelection,
  SpreadPosition,
  TarotCardInfo,
  TarotDeckId,
  TarotOrientation,
} from "../../types/tarot";

interface Props {
  positions: SpreadPosition[];
  deck: TarotDeckId;
  deckCards: TarotCardInfo[];
  value: ManualCardSelection[];
  onChange: (value: ManualCardSelection[]) => void;
  onSubmit: () => void;
  loading?: boolean;
}

interface PickerProps {
  deckCards: TarotCardInfo[];
  selectedCardIds: Set<string>;
  currentCardId?: string;
  onSelect: (card: TarotCardInfo) => void;
  onClose: () => void;
}

function ManualCardPickerModal({
  deckCards,
  selectedCardIds,
  currentCardId,
  onSelect,
  onClose,
}: PickerProps) {
  const [keyword, setKeyword] = useState("");
  const filtered = useMemo(() => {
    const q = keyword.trim().toLowerCase();
    if (!q) return deckCards;
    return deckCards.filter((card) => {
      const text = `${card.nameZh} ${card.nameEn} ${(card.keywordsZh ?? []).join(" ")}`.toLowerCase();
      return text.includes(q);
    });
  }, [deckCards, keyword]);

  return (
    <div className="tarot-manual-modal" role="dialog" aria-modal="true">
      <div className="tarot-manual-modal-panel">
        <div className="tarot-manual-modal-head">
          <h3>选择塔罗牌</h3>
          <button type="button" className="secondary" onClick={onClose}>
            关闭
          </button>
        </div>
        <input
          className="tarot-card-search"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          placeholder="搜索牌名或关键词"
        />
        <div className="tarot-card-option-grid">
          {filtered.map((card) => {
            const used = selectedCardIds.has(card.cardId) && card.cardId !== currentCardId;
            return (
              <button
                key={card.cardId}
                type="button"
                className={card.cardId === currentCardId ? "spread-card active" : "spread-card"}
                disabled={used}
                onClick={() => onSelect(card)}
              >
                <strong>{card.nameZh}</strong>
                <span>{card.nameEn}</span>
                {used ? <small>已用于其他位置</small> : null}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function nextOrientation(orientation: TarotOrientation): TarotOrientation {
  return orientation === "upright" ? "reversed" : "upright";
}

export function ManualPickBoard({
  positions,
  deck,
  deckCards,
  value,
  onChange,
  onSubmit,
  loading,
}: Props) {
  const [activePosition, setActivePosition] = useState<number | null>(null);
  const selectedCardIds = useMemo(() => new Set(value.map((item) => item.cardId)), [value]);
  const cardById = useMemo(
    () => new Map(deckCards.map((card) => [card.cardId, card])),
    [deckCards],
  );

  const updateSelection = (position: number, patch: Partial<ManualCardSelection>) => {
    const existing = value.find((item) => item.position === position);
    const nextItem: ManualCardSelection = {
      position,
      cardId: patch.cardId ?? existing?.cardId ?? "",
      orientation: patch.orientation ?? existing?.orientation ?? "upright",
    };
    const next = value.filter((item) => item.position !== position);
    onChange([...next, nextItem].sort((a, b) => a.position - b.position));
  };

  const complete = positions.every((position) =>
    value.some((item) => item.position === position.index && item.cardId),
  );
  const activeSelection = value.find((item) => item.position === activePosition);

  return (
    <div className="tarot-manual-board">
      <div className="tarot-pick-head">
        <div>
          <h3>手动摆牌</h3>
          <p className="hint">把实体牌的结果录入到每个牌阵位置, 再交给 AI 解读.</p>
        </div>
        <strong className="tarot-pick-counter">
          已填 {value.filter((item) => item.cardId).length} / {positions.length}
        </strong>
      </div>

      <div className="tarot-manual-grid">
        {positions.map((position) => {
          const selected = value.find((item) => item.position === position.index);
          const card = selected ? cardById.get(selected.cardId) : undefined;
          return (
            <div key={`${deck}-${position.index}`} className="tarot-manual-slot">
              <div className="reading-position-label">
                <strong>{position.labelZh}</strong>
                <span>{position.meaningZh}</span>
              </div>
              <button
                type="button"
                className={card ? "tarot-manual-card chosen" : "tarot-manual-card"}
                disabled={loading}
                onClick={() => setActivePosition(position.index)}
              >
                <strong>{card?.nameZh ?? "选择牌面"}</strong>
                <span>{card?.nameEn ?? "点击从 78 张牌中选择"}</span>
              </button>
              {selected?.cardId ? (
                <button
                  type="button"
                  className="secondary tarot-orient-toggle"
                  disabled={loading}
                  onClick={() =>
                    updateSelection(position.index, {
                      orientation: nextOrientation(selected.orientation),
                    })
                  }
                >
                  {selected.orientation === "reversed" ? "逆位" : "正位"}
                </button>
              ) : null}
            </div>
          );
        })}
      </div>

      <div className="form-actions form-actions-end tarot-pick-actions">
        <button type="button" className="primary-btn" disabled={loading || !complete} onClick={onSubmit}>
          {loading ? "生成中..." : "生成牌阵"}
        </button>
      </div>

      {activePosition !== null && (
        <ManualCardPickerModal
          deckCards={deckCards}
          selectedCardIds={selectedCardIds}
          currentCardId={activeSelection?.cardId}
          onClose={() => setActivePosition(null)}
          onSelect={(card) => {
            updateSelection(activePosition, { cardId: card.cardId });
            setActivePosition(null);
          }}
        />
      )}
    </div>
  );
}

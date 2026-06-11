interface MysticDeckGridProps {
  deckSize: number;
  cardCount: number;
  picks: number[];
  loading?: boolean;
  onPick: (index: number) => void;
}

export function MysticDeckGrid({
  deckSize,
  cardCount,
  picks,
  loading = false,
  onPick,
}: MysticDeckGridProps) {
  if (deckSize <= 0) {
    return (
      <div className="mystic-deck-empty">
        <span>等待洗牌</span>
        <p>输入问事并点击「洗牌入局」后, 这里会展开真实牌背桌面。</p>
      </div>
    );
  }

  return (
    <div className="mystic-deck-grid" aria-label="塔罗牌背选择区">
      {Array.from({ length: deckSize }, (_, index) => {
        const selectedIndex = picks.indexOf(index);
        const selected = selectedIndex >= 0;
        const disabled = loading || (!selected && picks.length >= cardCount);
        return (
          <button
            key={index}
            type="button"
            className={selected ? "mystic-card-back selected" : "mystic-card-back"}
            disabled={disabled}
            onClick={() => onPick(index)}
            aria-label={selected ? `已选择第 ${selectedIndex + 1} 张` : `选择第 ${index + 1} 张牌`}
          >
            <span className="mystic-card-sigil">*</span>
            <span className="mystic-card-title">TAROT</span>
            {selected && <em>{selectedIndex + 1}</em>}
          </button>
        );
      })}
    </div>
  );
}

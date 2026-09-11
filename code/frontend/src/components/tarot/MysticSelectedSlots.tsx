import type { DrawnCard, SpreadPosition, TarotDeckId } from "../../types/tarot";

interface MysticSelectedSlotsProps {
  positions: SpreadPosition[];
  picks: number[];
  cards?: DrawnCard[];
  deck: TarotDeckId;
}

export function MysticSelectedSlots({ positions, picks, cards, deck }: MysticSelectedSlotsProps) {
  return (
    <div className="mystic-selected-slots" aria-label="已选牌位">
      {positions.map((position, index) => {
        const picked = picks[index] !== undefined;
        const card = cards?.[index];
        const imageSrc = card?.image ? `/tarot/${card.image}` : null;
        const showImage = Boolean(imageSrc && deck !== "thoth");
        const reversed = card?.orientation === "reversed";

        return (
          <div
            key={position.index}
            className={`mystic-slot${picked ? " filled" : ""}${card ? " revealed" : ""}`}
          >
            <div className={`mystic-slot-card${card ? " revealed" : ""}`}>
              {card ? (
                <>
                  <span className="mystic-slot-card-fallback">{card.nameZh}</span>
                  {showImage && (
                    <img
                      className={reversed ? "reversed" : undefined}
                      src={imageSrc!}
                      alt={`${card.nameZh}，${reversed ? "逆位" : "正位"}`}
                      loading="lazy"
                      onError={(event) => {
                        event.currentTarget.hidden = true;
                      }}
                    />
                  )}
                </>
              ) : (
                <span>{picked ? index + 1 : "空"}</span>
              )}
            </div>
            <div className="mystic-slot-text">
              <strong>{position.labelZh}</strong>
              {card && (
                <span className="mystic-slot-reading">
                  {card.nameZh} · {reversed ? "逆位" : "正位"}
                </span>
              )}
              <small>{position.meaningZh}</small>
              {deck === "thoth" && card && (
                <small className="mystic-slot-copyright">托特牌面仅提供文字解读</small>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

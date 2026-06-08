import { useEffect, useState } from "react";
import type { DrawnCard, TarotDeckId } from "../../types/tarot";

interface Props {
  card: DrawnCard;
  deck: TarotDeckId;
  revealed: boolean;
  onReveal?: () => void;
}

export function TarotCard({ card, deck, revealed, onReveal }: Props) {
  const reversed = card.orientation === "reversed";
  const imageSrc = card.image ? `/tarot/${card.image}` : null;
  const [imageFailed, setImageFailed] = useState(false);

  useEffect(() => {
    setImageFailed(false);
  }, [card.cardId, imageSrc]);

  const showPlaceholder = !imageSrc || deck === "thoth" || imageFailed;

  return (
    <button
      type="button"
      className={
        revealed
          ? `tarot-card revealed ${reversed ? "reversed" : "upright"}`
          : "tarot-card face-down"
      }
      onClick={onReveal}
      disabled={revealed}
    >
      {!revealed && <span className="tarot-card-back">塔罗</span>}
      {revealed && (
        <>
          {showPlaceholder ? (
            <div className="tarot-card-placeholder">
              <span className="tarot-card-name">{card.nameZh}</span>
              {deck !== "thoth" && card.nameEn !== card.nameZh && (
                <span className="tarot-card-en">{card.nameEn}</span>
              )}
              {deck === "thoth" && (
                <small className="tarot-copyright-note">
                  托特牌面受版权保护, 本平台仅文字解读
                </small>
              )}
            </div>
          ) : (
            <img
              src={imageSrc!}
              alt={card.nameZh}
              loading="lazy"
              onError={() => setImageFailed(true)}
            />
          )}
          <div className="tarot-card-meta">
            <span>{reversed ? "逆位" : "正位"}</span>
          </div>
        </>
      )}
    </button>
  );
}

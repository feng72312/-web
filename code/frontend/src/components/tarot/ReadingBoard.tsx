import type { TarotReading } from "../../types/tarot";
import { TarotCard } from "./TarotCard";

interface Props {
  reading: TarotReading;
}

export function ReadingBoard({ reading }: Props) {
  return (
    <div className="tarot-reading-board">
      <div className="reading-board-head">
        <h3>{reading.spreadName}</h3>
        <p className="hint">{reading.deckName}</p>
      </div>
      <div className="reading-positions">
        {reading.cards.map((card) => (
          <div key={`${card.position}-${card.cardId}`} className="reading-position">
            <div className="reading-position-label">
              <strong>{card.positionLabel}</strong>
              <span>{card.positionMeaning}</span>
            </div>
            <TarotCard card={card} deck={reading.deck} revealed />
            <p className="reading-card-meaning">
              {card.orientation === "reversed" ? "逆位" : "正位"}: {card.meaningZh || card.meaningEn}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

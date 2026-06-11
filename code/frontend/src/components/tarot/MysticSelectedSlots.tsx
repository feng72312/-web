import type { SpreadPosition } from "../../types/tarot";

interface MysticSelectedSlotsProps {
  positions: SpreadPosition[];
  picks: number[];
}

export function MysticSelectedSlots({ positions, picks }: MysticSelectedSlotsProps) {
  return (
    <div className="mystic-selected-slots" aria-label="已选牌位">
      {positions.map((position, index) => {
        const picked = picks[index] !== undefined;
        return (
          <div
            key={position.index}
            className={picked ? "mystic-slot filled" : "mystic-slot"}
          >
            <div className="mystic-slot-card">
              {picked ? <span>{index + 1}</span> : <span>空</span>}
            </div>
            <div className="mystic-slot-text">
              <strong>{position.labelZh}</strong>
              <small>{position.meaningZh}</small>
            </div>
          </div>
        );
      })}
    </div>
  );
}

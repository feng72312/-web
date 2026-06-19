import { BirthForm } from "../../components/BirthForm";
import type { PaipanRequest, SavedProfile } from "../../types/bazi";
import { formatHourSlotLabel, slotFromHour } from "../../utils/timeSlots";

function formatPersonSummary(person: PaipanRequest): string {
  const calendar = person.calendarType === "lunar" ? "农历" : "公历";
  const leap = person.isLeapMonth ? " 闰月" : "";
  const gender = person.gender === 1 ? "男" : "女";
  const { slotIndex, ziHourPhase } = slotFromHour(person.hour);
  const hourLabel = formatHourSlotLabel(slotIndex, ziHourPhase);
  return `${person.name || "未命名"} / ${calendar} ${person.year}-${person.month}-${person.day}${leap} ${hourLabel} ${gender}`;
}

interface HepanPersonSlotProps {
  label: string;
  person: PaipanRequest | null;
  expanded: boolean;
  active?: boolean;
  onExpandedChange: (expanded: boolean) => void;
  onSubmit: (data: PaipanRequest) => void;
  onProfileLoad?: (profile: SavedProfile) => void;
  onProfilesChange?: () => void;
}

export function HepanPersonSlot({
  label,
  person,
  expanded,
  active = true,
  onExpandedChange,
  onSubmit,
  onProfileLoad,
  onProfilesChange,
}: HepanPersonSlotProps) {
  const showForm = expanded || !person;

  return (
    <div className={active ? "hepan-person-col hepan-person-col-active" : "hepan-person-col"}>
      <div className="hepan-person-col-head">
        <h3>{label}</h3>
        {person && !expanded ? (
          <button
            type="button"
            className="hepan-person-edit-btn"
            onClick={() => onExpandedChange(true)}
          >
            编辑
          </button>
        ) : null}
      </div>

      {person && !expanded ? (
        <div className="hepan-person-summary">
          <span className="hepan-person-summary-text">{formatPersonSummary(person)}</span>
        </div>
      ) : null}

      {showForm ? (
        <BirthForm
          key={person ? `${label}-${person.name}-${person.year}` : `${label}-new`}
          embedded
          compact
          hideSavedList
          loading={false}
          submitLabel="确认录入"
          initialRequest={person}
          onSubmit={(data) => {
            onSubmit(data);
            onExpandedChange(false);
          }}
          onProfileLoad={onProfileLoad}
          onProfilesChange={onProfilesChange}
        />
      ) : null}
    </div>
  );
}

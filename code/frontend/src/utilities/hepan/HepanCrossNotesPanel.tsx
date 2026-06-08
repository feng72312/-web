import type { HepanCrossNote, HepanPersonCharts } from "../../types/hepan";

interface Props {
  notes: HepanCrossNote[];
}

export function HepanCrossNotesPanel({ notes }: Props) {
  if (!notes.length) {
    return (
      <section className="panel hepan-notes-panel">
        <h3>合盘要点</h3>
        <p className="hint">暂无结构化要点.</p>
      </section>
    );
  }

  return (
    <section className="panel hepan-notes-panel">
      <h3>合盘要点</h3>
      <ul className="hepan-notes-list">
        {notes.map((note) => (
          <li key={note.id} className={`hepan-note hepan-note-${note.level}`}>
            <div className="hepan-note-head">
              <strong>{note.title}</strong>
              <span className="hepan-note-tag">{note.source === "bazi" ? "八字" : "紫微"}</span>
            </div>
            <p>{note.detail}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}

interface SummaryProps {
  person: HepanPersonCharts;
  label: string;
  discipline: "bazi" | "ziwei";
}

export function HepanPersonSummary({ person, label, discipline }: SummaryProps) {
  const bazi = person.baziChart as {
    dayMaster?: string;
    pillars?: Record<string, { ganzhi?: string; nayin?: string }>;
  } | null | undefined;
  const ziwei = person.ziweiChart as {
    meta?: { bureau?: string; soul?: string };
    palaces?: Array<{ name?: string; stemBranch?: string; majorStars?: Array<{ name: string }> }>;
  } | null | undefined;

  const day = bazi?.pillars?.day;
  const soulPalace = ziwei?.palaces?.[0];

  return (
    <div className="hepan-person-summary">
      <h4>
        {label} {person.name || ""}
      </h4>
      {bazi && (
        <p className="hint">
          日主 {bazi.dayMaster ?? ""} / 日柱 {day?.ganzhi ?? ""} {day?.nayin ?? ""}
        </p>
      )}
      {discipline === "ziwei" && ziwei && (
        <p className="hint">
          {ziwei.meta?.bureau ?? ""} / 命宫 {soulPalace?.stemBranch ?? ""}{" "}
          {(soulPalace?.majorStars ?? []).map((s) => s.name).join("、") || "无主星"}
        </p>
      )}
    </div>
  );
}

interface BaziInteractionNotesProps {
  stemNotes?: string;
  branchNotes?: string;
}

export function BaziInteractionNotes({ stemNotes, branchNotes }: BaziInteractionNotesProps) {
  const stem = stemNotes?.trim() || "暂无";
  const branch = branchNotes?.trim() || "暂无";

  return (
    <section className="bazi-report-card bazi-report-notes">
      <div className="bazi-report-section-head">
        <span className="bazi-card-eyebrow">留意</span>
        <h3>天干地支留意</h3>
      </div>
      <div className="bazi-report-notes-grid">
        <div className="bazi-report-note-item">
          <span className="bazi-report-note-label">天干留意</span>
          <p>{stem}</p>
        </div>
        <div className="bazi-report-note-item">
          <span className="bazi-report-note-label">地支留意</span>
          <p>{branch}</p>
        </div>
      </div>
    </section>
  );
}

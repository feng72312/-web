import type { SectionModuleProps } from "../types/bazi";

export function DayunSection({ section }: SectionModuleProps) {
  const data = section.data as {
    forward: boolean;
    start: Record<string, number>;
    rows: Array<{
      ganzhi: string;
      startAge: number;
      endAge: number;
      startYear: number;
    }>;
  };

  return (
    <section className="panel">
      <h3>{section.name}</h3>
      <p className="hint">
        起运: {data.start.year}年{data.start.month}月{data.start.day}天 (
        {data.forward ? "顺" : "逆"})
      </p>
      <div className="dayun-list">
        {data.rows.map((row) => (
          <div key={`${row.ganzhi}-${row.startAge}`} className="dayun-item">
            <div className="dayun-age">
              {row.startAge}-{row.endAge}岁
            </div>
            <div className="dayun-ganzhi">{row.ganzhi}</div>
            <div className="dayun-year">{row.startYear}年起</div>
          </div>
        ))}
      </div>
    </section>
  );
}

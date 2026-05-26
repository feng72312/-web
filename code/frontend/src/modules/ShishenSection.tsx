import type { SectionModuleProps } from "../types/bazi";

export function ShishenSection({ section }: SectionModuleProps) {
  const data = section.data as {
    rows: Array<{
      pillar: string;
      ganzhi: string;
      shishenGan: string;
      shishenZhi: string[];
    }>;
  };

  return (
    <section className="panel">
      <h3>{section.name}</h3>
      <table className="data-table">
        <thead>
          <tr>
            <th>柱</th>
            <th>干支</th>
            <th>天干十神</th>
            <th>地支十神</th>
          </tr>
        </thead>
        <tbody>
          {data.rows.map((row) => (
            <tr key={row.pillar}>
              <td>{row.pillar}</td>
              <td>{row.ganzhi}</td>
              <td>{row.shishenGan}</td>
              <td>{row.shishenZhi.join("、")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

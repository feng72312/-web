import type { MeihuaChart } from "../../types/meihua";

interface Props {
  chart: MeihuaChart;
  highlightPosition?: number;
}

const POSITION_LABELS = ["初", "二", "三", "四", "五", "上"];

export function MeihuaBoard({ chart, highlightPosition }: Props) {
  const ordered = [...chart.lines].sort((a, b) => b.position - a.position);
  return (
    <div className="hexagram-board meihua-board">
      <div className="hexagram-head">
        <p>
          本卦: {chart.benGua.name} (下{chart.benGua.lower} 上{chart.benGua.upper})
        </p>
        {chart.bianGua && <p>变卦: {chart.bianGua.name}</p>}
        {chart.huGua && (
          <p>
            互卦: {chart.huGua.name} (下{chart.huGua.lower} 上{chart.huGua.upper})
          </p>
        )}
        <p>
          动爻 {chart.movingLines.length ? chart.movingLines.join("、") : "无"}
          {chart.isStatic ? " (静卦: 下体上用)" : ""}
        </p>
      </div>
      <table className="data-table hexagram-table">
        <thead>
          <tr>
            <th>爻位</th>
            <th>爻象</th>
            <th>所属</th>
            <th>标记</th>
          </tr>
        </thead>
        <tbody>
          {ordered.map((line) => (
            <tr
              key={line.position}
              className={highlightPosition === line.position ? "row-highlight" : ""}
            >
              <td>{POSITION_LABELS[line.position - 1]}爻</td>
              <td>
                {line.isYang ? "—" : "- -"} {line.isMoving ? "动" : ""}
              </td>
              <td>{line.inLower ? "下卦" : "上卦"}</td>
              <td>
                {chart.tiGua.name === (line.inLower ? chart.benGua.lower : chart.benGua.upper)
                  ? "体 "
                  : ""}
                {chart.yongGua.name === (line.inLower ? chart.benGua.lower : chart.benGua.upper)
                  ? "用 "
                  : ""}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

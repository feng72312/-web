import type { LiuyaoChart } from "../../types/liuyao";

interface Props {
  chart: LiuyaoChart;
  highlightPosition?: number;
}

const POSITION_LABELS = ["初", "二", "三", "四", "五", "上"];

export function HexagramBoard({ chart, highlightPosition }: Props) {
  const ordered = [...chart.lines].sort((a, b) => b.position - a.position);
  return (
    <div className="hexagram-board">
      <div className="hexagram-head">
        <p>
          本卦: {chart.benGua.name} (下{chart.benGua.lower} 上{chart.benGua.upper})
        </p>
        <p>卦宫: {chart.benGua.palace}({chart.benGua.palaceElement})</p>
        {chart.bianGua && <p>变卦: {chart.bianGua.name}</p>}
        <p>
          月建 {chart.monthJian} / 日辰 {chart.dayChen} / 动爻{" "}
          {chart.movingLines.length ? chart.movingLines.join("、") : "无"}
        </p>
        <p>
          世应: 世{chart.shiYing.shi} 应{chart.shiYing.ying}
        </p>
      </div>
      <table className="data-table hexagram-table">
        <thead>
          <tr>
            <th>爻位</th>
            <th>爻象</th>
            <th>干支</th>
            <th>六亲</th>
            <th>六神</th>
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
              <td>{line.isYang ? "—" : "- -"} {line.isMoving ? "动" : ""}</td>
              <td>
                {line.stem}
                {line.branch}
              </td>
              <td>{line.liuqin}</td>
              <td>{line.liushen}</td>
              <td>
                {line.isShi ? "世 " : ""}
                {line.isYing ? "应 " : ""}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

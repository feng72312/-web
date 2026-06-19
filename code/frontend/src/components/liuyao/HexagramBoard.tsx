import type { LiuyaoChart } from "../../types/liuyao";

interface Props {
  chart: LiuyaoChart;
  highlightPosition?: number;
}

const POSITION_LABELS = ["初", "二", "三", "四", "五", "上"];

function lineRowClass(line: LiuyaoChart["lines"][number], highlightPosition?: number): string {
  const classes: string[] = [];
  if (highlightPosition === line.position) {
    classes.push("row-highlight");
  }
  if (line.isShi) {
    classes.push("row-shi");
  }
  if (line.isYing) {
    classes.push("row-ying");
  }
  if (line.isMoving) {
    classes.push("row-moving");
  }
  if (line.kongPoState?.xunKong) {
    classes.push("row-xun-kong");
  }
  if (line.kongPoState?.yuePo) {
    classes.push("row-yue-po");
  }
  return classes.join(" ");
}

function lineMarks(line: LiuyaoChart["lines"][number]): string {
  const marks: string[] = [];
  if (line.isShi) marks.push("世");
  if (line.isYing) marks.push("应");
  if (line.isMoving) marks.push("动");
  if (line.kongPoState?.xunKong) marks.push("空");
  if (line.kongPoState?.yuePo) marks.push("破");
  return marks.join(" ");
}

export function HexagramBoard({ chart, highlightPosition }: Props) {
  const ordered = [...chart.lines].sort((a, b) => b.position - a.position);
  const liuChong = chart.riskFlags?.benLiuChong || chart.riskFlags?.bianLiuChong;
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
          {liuChong ? " / 六冲" : ""}
        </p>
        {chart.meta?.rules ? <p>装卦: {chart.meta.rules as string}</p> : null}
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
            <tr key={line.position} className={lineRowClass(line, highlightPosition)}>
              <td>{POSITION_LABELS[line.position - 1]}爻</td>
              <td>
                {line.isYang ? "—" : "- -"} {line.isMoving ? "动" : ""}
              </td>
              <td>
                {line.stem}
                {line.branch}
              </td>
              <td>{line.liuqin}</td>
              <td>{line.liushen}</td>
              <td className="hexagram-marks">{lineMarks(line)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

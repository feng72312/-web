import type { JinkouPan } from "../../types/liuren";

interface Props {
  jinkou: JinkouPan;
}

export function JinkouPanel({ jinkou }: Props) {
  return (
    <div className="liuren-jinkou-panel panel-block">
      <h3>金口诀</h3>
      <p>
        人元: {jinkou.renYuan} | 地分: {jinkou.difen}
      </p>
      <p>
        贵神: {jinkou.guiShen.join(" / ")} | 将神: {jinkou.jiangShen.join(" / ")}
      </p>
      <p className="meta-line">
        四柱: {jinkou.fourPillars.year} {jinkou.fourPillars.month}{" "}
        {jinkou.fourPillars.day} {jinkou.fourPillars.hour}
      </p>
    </div>
  );
}

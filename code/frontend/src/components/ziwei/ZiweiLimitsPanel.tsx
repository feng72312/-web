import type { ZiweiChart } from "../../types/ziwei";

interface Props {
  chart: ZiweiChart;
  targetYear: number;
  onTargetYearChange: (year: number) => void;
}

export function ZiweiLimitsPanel({ chart, targetYear, onTargetYearChange }: Props) {
  const { limits } = chart;
  const yearly = limits.yearly as Record<string, string>;
  const currentMinor = (limits.current?.minor ?? {}) as Record<string, string>;

  return (
    <div className="ziwei-limits panel-inset">
      <h3>运限</h3>
      <label>
        流年参照年
        <input
          type="number"
          min={1900}
          max={2100}
          value={targetYear}
          onChange={(e) => onTargetYearChange(Number(e.target.value) || targetYear)}
        />
      </label>
      <section>
        <h4>流年</h4>
        <p>
          {yearly.stemBranch || `${yearly.heavenlyStem || ""}${yearly.earthlyBranch || ""}`} (
          {yearly.name})
        </p>
        {Array.isArray(yearly.palaceNames) && (
          <p className="hint">流宫: {(yearly.palaceNames as string[]).join(" ")}</p>
        )}
      </section>
      <section>
        <h4>小限 (当前)</h4>
        <p>
          {currentMinor.stemBranch ||
            `${currentMinor.heavenlyStem || ""}${currentMinor.earthlyBranch || ""}`}{" "}
          ({currentMinor.name})
        </p>
      </section>
      <section>
        <h4>大限</h4>
        <ul className="ziwei-decadal-list">
          {limits.decadal.map((row) => (
            <li key={row.index}>
              {row.ageRange}岁 {row.palace} {row.stemBranch}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h4>小限表 (节选)</h4>
        <ul className="ziwei-minor-list">
          {limits.minor.slice(0, 24).map((row) => (
            <li key={row.age}>
              {row.age}岁 {row.palace}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

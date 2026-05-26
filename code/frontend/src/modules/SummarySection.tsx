import type { SectionModuleProps } from "../types/bazi";

export function SummarySection({ section, chart }: SectionModuleProps) {
  const data = section.data as {
    fourPillars: string;
    name: string;
    calendarType: string;
    inputLabel: string;
    dayMaster: string;
    dayMasterWuxing: string;
    lunar: string;
    solar: string;
    dayunForward: boolean;
  };

  return (
    <section className="panel">
      <h3>{section.name}</h3>
      <dl className="kv-list">
        {data.name && (
          <div>
            <dt>姓名</dt>
            <dd>{data.name}</dd>
          </div>
        )}
        <div>
          <dt>四柱</dt>
          <dd>{data.fourPillars}</dd>
        </div>
        <div>
          <dt>输入</dt>
          <dd>{data.inputLabel || (data.calendarType === "lunar" ? "农历" : "公历")}</dd>
        </div>
        <div>
          <dt>日主</dt>
          <dd>
            {data.dayMaster} ({data.dayMasterWuxing})
          </dd>
        </div>
        <div>
          <dt>公历</dt>
          <dd>{data.solar}</dd>
        </div>
        <div>
          <dt>农历</dt>
          <dd>{data.lunar}</dd>
        </div>
        <div>
          <dt>大运</dt>
          <dd>{data.dayunForward ? "顺排" : "逆排"}</dd>
        </div>
      </dl>
      <p className="hint">规则: {chart.meta.rules.note as string}</p>
    </section>
  );
}

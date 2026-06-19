import type { ZiweiChart, ZiweiRules } from "../../types/ziwei";

const RULE_LABELS: Record<string, Record<string, string>> = {
  leapMonthRule: { next_month: "闰月归下月", midmonth_split: "闰月半月分界" },
  ziHourRule: { combined: "不分早晚子时", split: "分早晚子时" },
  mutagenTable: {
    nan_pai: "南派三合四化",
    geng_beipai: "北派庚干四化",
    wu_pai: "王亭之戊干",
    ren_pai: "壬干四化",
  },
  chartSchool: { sanhe: "三合派", feixing: "飞星派" },
};

function label(group: string, value: string | undefined): string {
  if (!value) {
    return "-";
  }
  return RULE_LABELS[group]?.[value] ?? value;
}

interface ZiweiRulesMetaBarProps {
  chart: ZiweiChart;
}

export function ZiweiRulesMetaBar({ chart }: ZiweiRulesMetaBarProps) {
  const meta = chart.rulesMeta as ZiweiRules & { warnings?: string[] };
  return (
    <div className="ziwei-rules-meta-bar">
      <span>闰月: {label("leapMonthRule", meta.leapMonthRule)}</span>
      <span>子时: {label("ziHourRule", meta.ziHourRule)}</span>
      <span>四化: {label("mutagenTable", meta.mutagenTable)}</span>
      <span>法派: {label("chartSchool", meta.chartSchool)}</span>
      <span>{chart.trueSolarTime ? `真太阳时 ${chart.trueSolarTime}` : ""}</span>
      {meta.warnings?.length ? (
        <span className="ziwei-rules-warning">规则提示: {meta.warnings.join("; ")}</span>
      ) : null}
    </div>
  );
}

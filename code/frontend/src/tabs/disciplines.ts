export type DisciplineLayer = "chart" | "divination" | "environment";

export interface DisciplineTab {
  id: string;
  label: string;
  enabled: boolean;
  layer: DisciplineLayer;
}

export interface DisciplineGroup {
  id: DisciplineLayer;
  label: string;
  tabs: DisciplineTab[];
}

export const DISCIPLINE_TABS: DisciplineTab[] = [
  { id: "01", label: "八字命理", enabled: true, layer: "chart" },
  { id: "11", label: "紫微斗数", enabled: true, layer: "chart" },
  { id: "09", label: "星命占验", enabled: true, layer: "chart" },
  { id: "02", label: "六爻卜筮", enabled: true, layer: "divination" },
  { id: "03", label: "梅花易数", enabled: true, layer: "divination" },
  { id: "04", label: "奇门遁甲", enabled: true, layer: "divination" },
  { id: "05", label: "大六壬", enabled: true, layer: "divination" },
  { id: "13", label: "塔罗占卜", enabled: true, layer: "divination" },
  { id: "06", label: "风水堪舆", enabled: true, layer: "environment" },
  { id: "12", label: "实用专区", enabled: true, layer: "environment" },
];

export const DISCIPLINE_GROUPS: DisciplineGroup[] = [
  { id: "chart", label: "命盘", tabs: DISCIPLINE_TABS.filter((t) => t.layer === "chart") },
  {
    id: "divination",
    label: "卜筮",
    tabs: DISCIPLINE_TABS.filter((t) => t.layer === "divination"),
  },
  {
    id: "environment",
    label: "环境关系",
    tabs: DISCIPLINE_TABS.filter((t) => t.layer === "environment"),
  },
];

export const DEFAULT_TAB = "01";

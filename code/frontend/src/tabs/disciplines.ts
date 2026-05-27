export interface DisciplineTab {
  id: string;
  label: string;
  enabled: boolean;
}

export const DISCIPLINE_TABS: DisciplineTab[] = [
  { id: "01", label: "八字命理", enabled: true },
  { id: "02", label: "六爻卜筮", enabled: true },
  { id: "03", label: "梅花易学", enabled: false },
  { id: "04", label: "奇门遁甲", enabled: false },
  { id: "05", label: "大六壬", enabled: false },
  { id: "06", label: "风水堪舆", enabled: false },
  { id: "07", label: "相术神相", enabled: false },
  { id: "08", label: "择日历算", enabled: false },
  { id: "09", label: "星命占验", enabled: false },
  { id: "10", label: "杂占方术", enabled: false },
];

export const DEFAULT_TAB = "01";

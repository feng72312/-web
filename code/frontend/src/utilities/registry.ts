export type UtilityId =
  | "hepan"
  | "zhuge"
  | "jiemeng"
  | "cewen"
  | "naming"
  | "name-analysis"
  | "phone";

export interface UtilityItem {
  id: UtilityId;
  label: string;
  description: string;
  enabled: boolean;
}

export const UTILITY_ITEMS: UtilityItem[] = [
  {
    id: "hepan",
    label: "合盘工具",
    description: "双人八字/紫微合盘, 婚恋与合作",
    enabled: true,
  },
  {
    id: "zhuge",
    label: "诸葛神数",
    description: "三字报卦, 384签查签",
    enabled: true,
  },
  {
    id: "jiemeng",
    label: "周公解梦",
    description: "梦境象意条目检索",
    enabled: true,
  },
  {
    id: "cewen",
    label: "测字",
    description: "汉字拆形取象, 一事一测",
    enabled: true,
  },
  {
    id: "naming",
    label: "起名",
    description: "说文字义, 五格数理, 八字喜忌与典籍 RAG",
    enabled: true,
  },
  {
    id: "name-analysis",
    label: "姓名分析",
    description: "姓名笔画五行与命盘配合",
    enabled: false,
  },
  {
    id: "phone",
    label: "手机号分析",
    description: "号码数理与五行倾向",
    enabled: false,
  },
];

export const DEFAULT_UTILITY: UtilityId = "hepan";

export function getUtilityItem(id: UtilityId): UtilityItem | undefined {
  return UTILITY_ITEMS.find((item) => item.id === id);
}

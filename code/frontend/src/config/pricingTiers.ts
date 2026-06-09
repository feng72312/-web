export interface PricingTier {
  id: string;
  label: string;
  features: string[];
}

export const PRICING_TIERS: PricingTier[] = [
  {
    id: "free",
    label: "免费层",
    features: ["基础排盘", "有限解读次数", "单牌/三牌塔罗"],
  },
  {
    id: "pro",
    label: "进阶层",
    features: ["深度报告", "跨术数联判", "扩展追问额度", "流式解读"],
  },
  {
    id: "expert",
    label: "专业层",
    features: ["批量档案", "专业视图", "导出与复盘", "案例资产库"],
  },
];

import type { DisciplineLayer } from "../tabs/disciplines";
import { DISCIPLINE_GROUPS } from "../tabs/disciplines";
import { getDisciplineIntro } from "./disciplineIntros";
import { UTILITY_ITEMS } from "../utilities/registry";

export type ProductPageId = "home" | "modules" | "chat";

export type VisualThemeId = "chart" | "divination" | "environment" | "utility";

export interface ModuleShowcaseMeta {
  id: string;
  label: string;
  layer: DisciplineLayer | "utility";
  theme: VisualThemeId;
  tagline: string;
  enabled: boolean;
  hasVisualDemo?: boolean;
}

const TAGLINES: Record<string, string> = {
  "01": "四柱格局与一生大势",
  "11": "十二宫星曜与四化飞星",
  "09": "七政四余与天象变局",
  "02": "铜钱摇卦一事一占",
  "03": "灵机起卦体用生克",
  "04": "九宫八门时空决策",
  "05": "四课三传人事推演",
  "13": "牌阵象征与情境梳理",
  "06": "宅墓方位气场布局",
  "12": "合盘测字解梦轻量工具",
};

const UTILS_MODULE_META: ModuleShowcaseMeta = {
  id: "12",
  label: "实用专区",
  layer: "utility",
  theme: "utility",
  tagline: TAGLINES["12"],
  enabled: true,
};

export function buildModuleShowcaseList(): ModuleShowcaseMeta[] {
  const tabs = DISCIPLINE_GROUPS.flatMap((group) =>
    group.tabs.map((tab) => {
      const visualLayer = tab.id === "12" ? "utility" : tab.layer;
      return {
        id: tab.id,
        label: tab.label,
        layer: visualLayer,
        theme: visualLayer as VisualThemeId,
        tagline: TAGLINES[tab.id] ?? getDisciplineIntro(tab.id)?.category ?? tab.label,
        enabled: tab.enabled,
      };
    }),
  );
  return tabs.filter((tab) => tab.id !== "12");
}

export function getUtilityShowcaseList() {
  return UTILITY_ITEMS.map((item) => ({
    id: item.id,
    label: item.label,
    tagline: item.description,
    theme: "utility" as VisualThemeId,
    enabled: item.enabled,
  }));
}

export function getModuleMeta(moduleId: string): ModuleShowcaseMeta | undefined {
  if (moduleId === "12") {
    return UTILS_MODULE_META;
  }
  return buildModuleShowcaseList().find((item) => item.id === moduleId);
}

export const LAYER_LABELS: Record<VisualThemeId, string> = {
  chart: "命盘",
  divination: "卜筮",
  environment: "环境关系",
  utility: "实用专区",
};

export const LAYER_DESCRIPTIONS: Record<VisualThemeId, string> = {
  chart: "论一生格局、阶段运势与命盘细节, 适合宏观把握人生层次与转折.",
  divination: "针对具体问事快速决疑, 擅长事件成败、时机选择与情境判断.",
  environment: "从空间、方位与气场入手, 适合宅居布局与长期环境规划.",
  utility: "轻量快捷工具, 合盘、测字、解梦、起名等辅助问事.",
};

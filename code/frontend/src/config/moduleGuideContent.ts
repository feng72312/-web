import { getDisciplineIntro } from "./disciplineIntros";
import { getModuleHomeImage, type HomeImageMeta } from "./homeModuleImages";
import {
  buildModuleShowcaseList,
  getUtilityShowcaseList,
  LAYER_DESCRIPTIONS,
  LAYER_LABELS,
  type VisualThemeId,
} from "./productModules";
import { getWorkflowGuide, type WorkflowGuideConfig } from "./workflowSteps";

export type AdvisorTagId =
  | "life-pattern"
  | "specific-outcome"
  | "strategy"
  | "relationship"
  | "space"
  | "psychology"
  | "quick-tool";

export interface AdvisorTag {
  id: AdvisorTagId;
  label: string;
  hint: string;
}

export const ADVISOR_TAGS: AdvisorTag[] = [
  { id: "life-pattern", label: "看一生格局", hint: "论格局、阶段运势与人生层次" },
  { id: "specific-outcome", label: "问具体成败", hint: "一事一占, 成败与应期" },
  { id: "strategy", label: "要行动策略", hint: "时机、方位与进退取舍" },
  { id: "relationship", label: "看关系人事", hint: "人际互动、来龙去脉" },
  { id: "space", label: "住宅店铺", hint: "宅向、气场与布局" },
  { id: "psychology", label: "心理关系梳理", hint: "情境象征与关系走向" },
  { id: "quick-tool", label: "轻量工具", hint: "合盘、测字、解梦、起名等" },
];

const MODULE_ADVISOR_MAP: Record<string, AdvisorTagId[]> = {
  "01": ["life-pattern"],
  "11": ["life-pattern", "relationship", "psychology"],
  "09": ["life-pattern"],
  "02": ["specific-outcome"],
  "03": ["specific-outcome"],
  "04": ["strategy"],
  "05": ["relationship"],
  "06": ["space"],
  "13": ["psychology", "specific-outcome"],
  "12": ["quick-tool", "relationship"],
};

export interface ModuleGuideItem {
  id: string;
  label: string;
  layer: VisualThemeId | "utility";
  theme: VisualThemeId;
  image?: HomeImageMeta;
  tagline: string;
  category: string;
  coreMethod: string;
  characteristics: string;
  advantages: string[];
  recommendedFor: string[];
  typicalQuestions: string[];
  workflow: WorkflowGuideConfig;
  advisorTags: AdvisorTagId[];
  enabled: boolean;
}

export interface UtilityGuideItem {
  id: string;
  label: string;
  description: string;
  theme: VisualThemeId;
  image?: HomeImageMeta;
  enabled: boolean;
  advisorTags: AdvisorTagId[];
  workflow?: WorkflowGuideConfig;
}

export function getModuleGuideItems(): ModuleGuideItem[] {
  return buildModuleShowcaseList().map((meta) => {
    const intro = getDisciplineIntro(meta.id);
    const workflow = getWorkflowGuide(meta.id);
    return {
      id: meta.id,
      label: meta.label,
      layer: meta.layer,
      theme: meta.theme,
      image: getModuleHomeImage(meta.id),
      tagline: meta.tagline,
      category: intro?.category ?? meta.tagline,
      coreMethod: intro?.coreMethod ?? "",
      characteristics: intro?.characteristics ?? "",
      advantages: intro?.advantages ?? [],
      recommendedFor: intro?.recommendedFor ?? [],
      typicalQuestions: intro?.typicalQuestions ?? [],
      workflow,
      advisorTags: MODULE_ADVISOR_MAP[meta.id] ?? [],
      enabled: meta.enabled,
    };
  });
}

export function getUtilityGuideItems(): UtilityGuideItem[] {
  return getUtilityShowcaseList().map((item) => ({
    id: item.id,
    label: item.label,
    description: item.tagline,
    theme: item.theme,
    image: getModuleHomeImage(item.id),
    enabled: item.enabled,
    advisorTags: ["quick-tool"] as AdvisorTagId[],
    workflow: getWorkflowGuide("12", item.id),
  }));
}

export function getModulesForAdvisorTag(tag: AdvisorTagId): ModuleGuideItem[] {
  const items = getModuleGuideItems();
  if (tag === "quick-tool") {
    return items.filter((item) => item.advisorTags.includes("quick-tool"));
  }
  return items.filter((item) => item.advisorTags.includes(tag));
}

export function getLayerOverview() {
  const layers: VisualThemeId[] = ["chart", "divination", "environment", "utility"];
  return layers.map((id) => ({
    id,
    label: LAYER_LABELS[id],
    description: LAYER_DESCRIPTIONS[id],
    modules: getModuleGuideItems().filter((m) => m.layer === id),
  }));
}

export const HOME_CAPABILITY_ITEMS = [
  {
    title: "一门看透人生起伏",
    detail: "八字、紫微、六爻、梅花、奇门、六壬、风水、星命、塔罗等主流术数齐聚, 大事小情都有对应法门.",
  },
  {
    title: "千年典籍为你撑腰",
    detail: "博采经典命理文献, 解读有据、言之有物, 让你听得明白也信得过.",
  },
  {
    title: "名师级 AI 顾问",
    detail: "多年功底凝练成易懂语言, 专业版与白话版随心切换, 像身边有位懂行的老师傅.",
  },
  {
    title: "问到满意为止",
    detail: "看完结果还能接着聊, 事业、感情、时机、取舍, 想到哪问到哪.",
  },
  {
    title: "命盘卜筮一站齐备",
    detail: "看格局、问成败、择时机、理关系、调环境, 不用东奔西跑换平台.",
  },
  {
    title: "沉浸式测算体验",
    detail: "庄重而不失温度的界面, 让每一次问事都像一场值得铭记的仪式.",
  },
] as const;

export const HOME_WORKFLOW_STEPS = [
  { title: "说出你的疑惑", detail: "人生方向、眼前抉择、关系困扰或环境顾虑, 如实写下即可." },
  { title: "为你精密推演", detail: "依你所选术数, 呈现专属命盘、卦象或牌阵, 一目了然." },
  { title: "引经据典佐证", detail: "结合传世典籍精华, 让解读更有分量、更经得起琢磨." },
  { title: "专家级解读送达", detail: "专业术语或大白话, 按你的阅读习惯娓娓道来." },
  { title: "继续深聊解惑", detail: "还有追问? 接着聊, 直到心里踏实为止." },
] as const;

export const HOME_SELECTION_TIPS: string[] = [
  "想看清人生大方向? 命盘类术数最适合入门.",
  "眼前有事要尽快决断? 卜筮类应答神速、一针见血.",
  "犹豫不决需要策略? 奇门能帮你理清进退与时机.",
  "人际关系理不清? 六壬专解纠缠来龙去脉.",
  "还没想好选哪门? 先进预测模块, 向导会替你匹配.",
];

import type { AiScenarioConfig } from "./types";

export const AI_CHAT_SCENARIOS: AiScenarioConfig[] = [
  {
    id: "general",
    label: "通用术数顾问",
    title: "通用术数顾问",
    description: "不限定术数, 先聊背景再给出建议.",
    quickPrompts: [
      "我想了解今年事业走势, 该从哪个方向入手?",
      "命理和心理学有什么区别, 我该怎么看待测算结果?",
      "第一次接触术数, 请给我一个入门学习路径.",
    ],
  },
  {
    id: "choose_method",
    label: "选择术数",
    title: "选择术数",
    description: "根据问事帮你判断更适合八字, 六爻还是塔罗等.",
    quickPrompts: [
      "我想问感情走向, 该用八字还是六爻?",
      "短期决策和长期趋势, 分别适合什么术数?",
      "我有一个具体时间点的问题, 该怎么选方法?",
    ],
  },
  {
    id: "prepare_question",
    label: "整理问事",
    title: "整理问事",
    description: "把模糊问题整理成适合排盘或起卦的表述.",
    quickPrompts: [
      "我想问工作变动, 但问题很乱, 请帮我整理.",
      "我准备问感情, 需要补充哪些关键信息?",
      "如何把「最近不顺」变成可测算的具体问题?",
    ],
  },
  {
    id: "explain_terms",
    label: "解释术语",
    title: "解释术语",
    description: "通俗解释格局, 用神, 宫位等命理术语.",
    quickPrompts: [
      "请解释什么是用神, 喜忌?",
      "紫微斗数里的命宫和身宫有什么区别?",
      "六爻里的世应和动爻怎么理解?",
    ],
  },
  {
    id: "review_result",
    label: "解读已有结果",
    title: "解读已有结果",
    description: "粘贴或描述已有测算结果, 获取解读思路.",
    quickPrompts: [
      "我有一份八字解读, 想请你帮我梳理重点.",
      "我起了一卦但看不懂, 稍后粘贴结果请你解释.",
      "请告诉我粘贴测算结果时应该包含哪些信息.",
    ],
  },
];

export function getScenarioConfig(
  scenario: string,
): AiScenarioConfig | undefined {
  return AI_CHAT_SCENARIOS.find((item) => item.id === scenario);
}

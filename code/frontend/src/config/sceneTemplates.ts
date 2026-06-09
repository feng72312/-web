export interface SceneTemplate {
  id: string;
  label: string;
  moduleIds: string[];
  prompt: string;
}

export const SCENE_TEMPLATES: SceneTemplate[] = [
  {
    id: "career",
    label: "事业财运",
    moduleIds: ["01", "11"],
    prompt: "请论此命主事业方向、财运起伏与近一年关键转折.",
  },
  {
    id: "marriage",
    label: "婚恋感情",
    moduleIds: ["11", "13"],
    prompt: "请论感情模式、伴侣缘分与当下关系走向.",
  },
  {
    id: "decision",
    label: "当下抉择",
    moduleIds: ["13", "02"],
    prompt: "此事应推进还是等待? 请给明确倾向与时机建议.",
  },
  {
    id: "timing",
    label: "择时策略",
    moduleIds: ["04", "05"],
    prompt: "此事最佳启动时机与需回避时段.",
  },
];

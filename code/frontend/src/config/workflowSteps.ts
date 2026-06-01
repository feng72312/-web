export interface WorkflowStep {
  title: string;
  detail: string;
  tip?: string;
}

export interface WorkflowGuideConfig {
  title: string;
  intro: string;
  steps: WorkflowStep[];
}

export const WORKFLOW_GUIDES: Record<string, WorkflowGuideConfig> = {
  "01": {
    title: "八字预测流程",
    intro: "按顺序填写出生信息并排盘, 再向 AI 提问即可得到命理解读.",
    steps: [
      {
        title: "填写出生信息",
        detail: "输入姓名、公历或农历生日、出生时辰与性别.",
        tip: "时辰不确定可先选最接近的时辰, 后续可改档案重排.",
      },
      {
        title: "点击开始排盘",
        detail: "系统计算四柱、大运与流年等命盘信息.",
      },
      {
        title: "查看命盘结果",
        detail: "在命盘区浏览四柱、大运流年与分析面板.",
      },
      {
        title: "填写问事",
        detail: "在「典籍与 AI」区用一句话写清楚你想问的事, 如事业、感情、健康.",
      },
      {
        title: "选择 AI 模型",
        detail: "推荐选大师级及以上.",
      },
      {
        title: "获取解读",
        detail: "先点「检索知识库」, 再点「AI深度解读」或「命理师专用解读」.",
        tip: "AI深度解读更易懂, 命理师专用解读术语更多; 各扣 1 次 AI 配额.",
      },
      {
        title: "继续追问(可选)",
        detail: "点「打开 AI 对话」可针对命盘多轮追问.",
      },
    ],
  },
  "02": {
    title: "六爻预测流程",
    intro: "先明确问事, 再起卦排盘, 确认用神后请 AI 断卦.",
    steps: [
      {
        title: "写清楚问事",
        detail: "在问事框用一句话描述要占的事, 宜具体, 如「这次面试能否通过」.",
      },
      {
        title: "选择起卦方式",
        detail: "摇卦、数字或时间三种方式任选其一.",
        tip: "新手推荐「数字起卦」: 心里默想三个数即可.",
      },
      {
        title: "完成起卦并排盘",
        detail: "按所选方式操作后, 点「完成起卦并排盘」.",
      },
      {
        title: "确认用神",
        detail: "点「AI 推断用神」或手动选择用神并确认.",
        tip: "用神代表问事的核心对象, 不确认则无法 AI 解读.",
      },
      {
        title: "检索典籍",
        detail: "在「典籍与 AI」区点「检索典籍」加载参考资料.",
      },
      {
        title: "获取解读",
        detail: "点「AI深度解读」或「命理师专用解读」查看占断结果.",
      },
      {
        title: "继续追问(可选)",
        detail: "点「打开 AI 对话」可追问细节.",
      },
    ],
  },
  "03": {
    title: "梅花易数预测流程",
    intro: "写问事、起卦、看体用, 再请 AI 给出梅花易数解读.",
    steps: [
      {
        title: "写清楚问事",
        detail: "描述要占的具体问题.",
      },
      {
        title: "选择起卦方式",
        detail: "数字起卦或时间起卦, 新手可用数字起卦.",
      },
      {
        title: "完成起卦",
        detail: "填好数字或时间后, 点「完成起卦」.",
      },
      {
        title: "查看卦象与体用",
        detail: "看本卦、变卦及体用关系.",
        tip: "静卦可点「动1-6爻」切换动爻位置.",
      },
      {
        title: "检索知识库",
        detail: "点「检索知识库」加载相关典籍摘录.",
      },
      {
        title: "获取解读",
        detail: "点「AI深度解读」或「命理师专用解读」.",
      },
    ],
  },
  "04": {
    title: "奇门预测流程",
    intro: "填问事与起局时间, 排九宫盘后用 AI 断事.",
    steps: [
      {
        title: "写清楚问事",
        detail: "说明要占的事, 并选择事占或行占.",
      },
      {
        title: "设置起局参数",
        detail: "选排盘法(默认拆补法)、方位; 时间一般用当前时刻即可.",
        tip: "非专业人士保持默认拆补法与当前时间.",
      },
      {
        title: "完成起局",
        detail: "点「完成起局」, 等待九宫盘生成.",
      },
      {
        title: "查看九宫盘",
        detail: "浏览局名、值符值使与九宫门星神.",
      },
      {
        title: "检索知识库",
        detail: "点「检索知识库」.",
      },
      {
        title: "获取解读",
        detail: "选「大师」「宗师」或「道长」级模型, 点「AI深度解读」或「命理师专用解读」.",
        tip: "AI深度解读更适合初次使用.",
      },
    ],
  },
  "05": {
    title: "六壬预测流程",
    intro: "写问事、选占时, 起课后由 AI 给出六壬断语.",
    steps: [
      {
        title: "写清楚问事",
        detail: "描述要占的问题并选择类别.",
      },
      {
        title: "设置起课参数",
        detail: "选正六壬或金口诀, 占时一般用当前时刻.",
      },
      {
        title: "完成起课",
        detail: "点「完成起课」生成课盘.",
      },
      {
        title: "查看课盘",
        detail: "看四课三传、天地盘与神煞.",
      },
      {
        title: "检索知识库",
        detail: "点「检索知识库」.",
      },
      {
        title: "获取解读",
        detail: "点「AI深度解读」或「命理师专用解读」.",
      },
    ],
  },
};

export const DEFAULT_WORKFLOW: WorkflowGuideConfig = {
  title: "预测流程",
  intro: "该术数模块尚在开发中, 请先使用已开放的八字、六爻、梅花易数、奇门或大六壬.",
  steps: [
    {
      title: "切换已开放 Tab",
      detail: "点击顶部 Tab 选择八字命理、六爻卜筮等已启用模块.",
    },
  ],
};

export function getWorkflowGuide(tabId: string): WorkflowGuideConfig {
  return WORKFLOW_GUIDES[tabId] ?? DEFAULT_WORKFLOW;
}

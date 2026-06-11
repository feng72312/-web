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
        detail: "点「AI深度解读」或「命理师专用解读」.",
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
        title: "获取解读",
        detail: "选「小师傅」「大师」或「资深道长」级模型, 点「AI深度解读」或「命理师专用解读」.",
        tip: "AI深度解读更适合初次使用.",
      },
    ],
  },
  "11": {
    title: "紫微斗数流程",
    intro: "填写出生并排盘, 查看十二宫与运限后用 AI 解读.",
    steps: [
      {
        title: "填写出生信息",
        detail: "与八字共用档案; 可选高级规则(真太阳时、闰月、子时).",
        tip: "默认开启真太阳时, 经度 120 (北京时间).",
      },
      {
        title: "点击排盘",
        detail: "系统安星排十二宫, 并计算大限、小限与流年.",
      },
      {
        title: "查看命盘",
        detail: "浏览命宫主星、局数、四化与各宫运限.",
      },
      {
        title: "填写问事",
        detail: "说明想论的事业、感情、健康等主题.",
      },
      {
        title: "获取解读",
        detail: "点 AI 深度解读或命理师专用解读.",
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
        title: "获取解读",
        detail: "点「AI深度解读」或「命理师专用解读」.",
      },
    ],
  },
  "06": {
    title: "风水堪舆预测流程",
    intro: "写问事、选流派与宅向, 排八宅或玄空盘后请 AI 给出布局建议.",
    steps: [
      {
        title: "写清楚问事",
        detail: "说明要论的事, 如这套房是否宜住、财位在哪、如何调整布局.",
      },
      {
        title: "选择流派与场景",
        detail: "八宅看命卦与宅卦相配; 玄空飞星看元运与运山向飞星. 场景可选住宅、店铺或办公室.",
        tip: "入门可先试八宅; 论长期宅运与流年叠加可选玄空.",
      },
      {
        title: "填写宅向参数",
        detail: "选择宅坐山. 八宅还需填出生年与性别; 玄空需填建成/入伙年, 可选填流年年份.",
      },
      {
        title: "完成排盘",
        detail: "点「完成排盘」, 等待八宅方位盘或玄空飞星盘生成.",
      },
      {
        title: "查看风水盘",
        detail: "八宅看四大吉方/四凶方与人宅是否相配; 玄空看运盘、山盘、向盘及流年叠加.",
      },
      {
        title: "选择 AI 模型",
        detail: "在「典籍与 AI」区选择模型, 推荐大师级及以上.",
      },
      {
        title: "获取解读",
        detail: "点「AI深度解读」或「命理师专用解读」, 结合古籍摘录看趋吉避凶思路.",
        tip: "各扣 1 次 AI 配额.",
      },
      {
        title: "继续追问(可选)",
        detail: "点「打开 AI 对话」可针对当前宅盘多轮追问.",
      },
    ],
  },
  "09": {
    title: "星命占验预测流程",
    intro: "填写出生与问事, 排七政四余十二宫, 可对照八字/紫微后用 AI 断验.",
    steps: [
      {
        title: "填写出生信息",
        detail: "输入姓名、公历或农历生日、出生时辰与性别, 与八字排盘表单相同.",
        tip: "默认真太阳时, 经度 120 (北京时间).",
      },
      {
        title: "填写问事与流年",
        detail: "在问事框写清楚想论的主题; 流年参照年用于太岁与阶段运势.",
      },
      {
        title: "对照其他命盘(可选)",
        detail: "勾选「对照八字盘」或「对照紫微盘」, 需先在对应 Tab 完成排盘并存入 session.",
        tip: "三术对照有助于 AI 综合星命、子平与紫微视角.",
      },
      {
        title: "星命排盘",
        detail: "点「星命排盘」, 系统计算七政四余、十二宫与太岁落宫.",
      },
      {
        title: "查看星命盘",
        detail: "浏览星体落宿、十二宫星曜分布、流年太岁与昼夜生.",
      },
      {
        title: "选择 AI 模型",
        detail: "推荐选大师级及以上.",
      },
      {
        title: "获取解读",
        detail: "点「AI深度解读」或「命理师专用解读」, 可查看占验课例与古籍摘录.",
      },
      {
        title: "继续对话(可选)",
        detail: "点「继续对话」针对星命盘多轮追问.",
      },
    ],
  },
  "13": {
    title: "塔罗占卜流程",
    intro: "明确问事, 选牌系与牌阵, 抽牌后 AI 中文解读, 可继续追问.",
    steps: [
      {
        title: "写清楚问事",
        detail: "用一句话描述要问的事, 宜具体, 如「这次面试能否通过」.",
      },
      {
        title: "选择牌系",
        detail: "韦特 (主流) / 马赛 (传统) / 托特 (文字解读).",
      },
      {
        title: "选择牌阵",
        detail: "可手动选牌阵, 或点「AI 推荐牌阵」自动匹配.",
      },
      {
        title: "洗牌抽牌",
        detail: "点「开始抽牌」, 逐张翻开或一键全部翻开.",
      },
      {
        title: "查看牌阵",
        detail: "按位置查看每张牌的正逆位与牌义.",
      },
      {
        title: "AI 解读",
        detail: "点「AI深度解读」或「命理师专用解读」, 结合典籍 RAG 生成中文摘要.",
      },
      {
        title: "继续追问(可选)",
        detail: "点「打开 AI 对话」针对牌阵多轮追问.",
      },
    ],
  },
  "12": {
    title: "实用专区流程",
    intro: "选择小工具, 填写对应信息, 查看结果后可 AI 解读.",
    steps: [
      {
        title: "选择工具",
        detail: "在合盘、诸葛神数、解梦、测字、起名等子导航中选择一项.",
      },
      {
        title: "填写信息",
        detail: "按工具要求输入, 合盘需录入甲乙双方.",
      },
      {
        title: "查看结果",
        detail: "合盘会展示结构化要点与双方摘要.",
      },
      {
        title: "AI 解读(可选)",
        detail: "消耗 AI 配额获取叙述与建议.",
      },
    ],
  },
  "12-zhuge": {
    title: "诸葛神数流程",
    intro: "三字报卦, 计笔画查签, 可 AI 释签.",
    steps: [
      { title: "输入三字", detail: "恰好三个汉字, 可选手填每字笔画." },
      { title: "报字查签", detail: "系统按百十个位归约后对 384 签取签文." },
      { title: "AI 释签", detail: "结合问事与典籍摘录生成白话或专业解读." },
    ],
  },
  "12-jiemeng": {
    title: "周公解梦流程",
    intro: "描述梦境, 检索条目, 可 AI 解读.",
    steps: [
      { title: "描述梦境", detail: "输入梦中景象或关键词, 至少两字." },
      { title: "检索条目", detail: "从《周公解梦》匹配象意断语." },
      { title: "AI 解读", detail: "串联条目与 RAG 摘录作答." },
    ],
  },
  "12-cewen": {
    title: "测字流程",
    intro: "一字一测, 依《测字秘牒》体例解读.",
    steps: [
      { title: "输入字与问事", detail: "填写所测汉字与要问的事." },
      { title: "AI 测字", detail: "检索秘牒摘录并生成解读." },
    ],
  },
  "12-naming": {
    title: "起名流程",
    intro: "说文字义, 五格数理, 可选八字喜忌, 典籍 RAG 与 AI 取名建议.",
    steps: [
      { title: "填写姓名", detail: "输入姓氏与名字, 可勾选出生信息以合八字." },
      { title: "结构化分析", detail: "查看五格、部首五行与《说文》字义." },
      { title: "AI 取名建议", detail: "结合起名典籍摘录生成专业或白话解读." },
    ],
  },
  "12-hepan": {
    title: "合盘工具流程",
    intro: "双人合盘: 选场景, 录入两人, 排盘后可解读.",
    steps: [
      {
        title: "选择场景",
        detail: "恋爱/婚姻默认紫微, 合作默认八字, 也可手动指定术数.",
      },
      {
        title: "录入甲方与乙方",
        detail: "分别填写出生信息或从档案载入.",
      },
      {
        title: "合盘排盘",
        detail: "系统计算交叉要点与标签.",
      },
      {
        title: "AI 解读",
        detail: "基于要点生成契合/注意/建议.",
      },
    ],
  },
};

export const DEFAULT_WORKFLOW: WorkflowGuideConfig = {
  title: "预测流程",
  intro: "请使用顶部已开放模块: 八字、六爻、梅花、奇门、六壬、风水、星命、紫微或实用专区.",
  steps: [
    {
      title: "切换已开放 Tab",
      detail: "点击顶部 Tab 选择八字命理、六爻卜筮等已启用模块.",
    },
  ],
};

export function getWorkflowGuide(tabId: string, utilityId?: string): WorkflowGuideConfig {
  if (tabId === "12" && utilityId) {
    const key = `12-${utilityId}` as keyof typeof WORKFLOW_GUIDES;
    if (WORKFLOW_GUIDES[key]) {
      return WORKFLOW_GUIDES[key];
    }
  }
  return WORKFLOW_GUIDES[tabId] ?? DEFAULT_WORKFLOW;
}

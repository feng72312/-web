export interface DisciplineIntro {
  subtitle?: string;
  category: string;
  coreMethod: string;
  characteristics: string;
  advantages: string[];
  recommendedFor: string[];
  typicalQuestions: string[];
}

export const DISCIPLINE_SELECTION_TIPS: string[] = [
  "想了解一生运程: 八字 + 紫微 (两者互补, 八字看格局, 紫微看细节).",
  "有具体问题, 要快问快答: 六爻 (最稳) 或梅花 (最快).",
  "需要决策建议 (换工作、投资、出行): 奇门遁甲 (给策略).",
  "想探究人际关系、事情来龙去脉: 大六壬.",
  "手边没有工具, 随手起卦: 梅花易数 (数字、时间皆可).",
];

export const DISCIPLINE_INTROS: Record<string, DisciplineIntro> = {
  "01": {
    subtitle: "子平命理",
    category: "一生整体运势 (财富、事业、婚姻、健康、六亲)、大运流年吉凶.",
    coreMethod: "四柱干支、十神、五行生克制化、用神喜忌.",
    characteristics:
      "最普及, 理论成熟, 擅长宏观判断人生层次和趋势, 但具体细节不如紫微.",
    advantages: [
      "适合论一生大势与十年阶段",
      "格局用神体系成熟, 可反复推敲",
      "可与大运流年配合, 看何时起运、何时转折",
    ],
    recommendedFor: [
      "性格天赋与职业方向",
      "婚姻感情大势",
      "财运起伏与理财时机",
      "健康倾向与养生重点",
      "某段大运或流年吉凶",
    ],
    typicalQuestions: ["我这辈子能发财吗?", "哪年结婚?"],
  },
  "02": {
    subtitle: "纳甲筮法",
    category: "具体事务的成败、过程、应期 (时效短, 通常数日内到一两年).",
    coreMethod: "三枚铜钱摇卦, 排六亲、六神、世应, 看动爻、用神、日月建.",
    characteristics:
      "最正统的「一事一占」, 对具体问题的回答非常直接 (能、不能、何时), 准确率高.",
    advantages: [
      "问事明确, 结论相对直接",
      "擅长占断具体事件能否成功",
      "应期、过程细节可进一步追问",
    ],
    recommendedFor: [
      "面试录取、考试结果",
      "交易合作能否谈成",
      "失物能否找回",
      "官司诉讼输赢",
      "出行安危、项目能否落地",
    ],
    typicalQuestions: ["明天面试能过吗?", "丢的东西能找到吗?"],
  },
  "03": {
    category: "与六爻相似, 但更强调「灵机」和「象意」, 可测任何事物.",
    coreMethod: "数字、时间、方位、颜色、声音等任意起卦, 体用生克, 卦象直读.",
    characteristics:
      "起卦最灵活, 入门快, 但对解卦者的悟性和联想力要求极高, 适合快速决疑.",
    advantages: [
      "起卦快, 不占场地, 随时可占",
      "善抓当下形势与动静之机",
      "体用关系直观, 入门相对容易",
    ],
    recommendedFor: [
      "当下要不要做某个决定",
      "短期走势与吉凶",
      "寻人寻物、小事成败",
      "临场即兴问事",
      "对方心意与事态走向",
    ],
    typicalQuestions: ["这次出行是否顺利?", "这个人心思如何?"],
  },
  "04": {
    category: "策略决策、时机选择、地理方位、竞争胜负 (常用于商业、军事、官司).",
    coreMethod: "时家转盘为主, 九宫、八门、九星、八神、天盘地盘人盘, 看用神落宫和格局.",
    characteristics:
      "被称为「帝王之术」, 最强项是提供「怎么做」的建议 (如往哪个方向走、何时行动), 时空建模精细.",
    advantages: [
      "时空信息完整, 利于谋事布局",
      "可论方位得失与进退时机",
      "竞争、谈判、出行类问题表现突出",
    ],
    recommendedFor: [
      "开业、签约、谈判择时",
      "出行方向与行程安危",
      "竞争策略与避凶趋吉",
      "寻人、索债、躲灾",
      "重要行动是否宜动",
    ],
    typicalQuestions: ["这场谈判怎么赢?", "店铺开在哪个方向好?"],
  },
  "05": {
    category: "人事吉凶、社会关系、事情发展过程 (与奇门并称「三式」之一).",
    coreMethod: "月将加时起天地盘、四课三传、十二天将, 看课体、三传生克.",
    characteristics:
      "专攻「人事」, 对人与人之间的互动、事情的前因后果描述非常详尽, 被称为「人事之王」.",
    advantages: [
      "课传层次清楚, 细节占断深入",
      "神将系统完备, 人事关系可辨",
      "兼能金口诀, 适合快速问事",
    ],
    recommendedFor: [
      "官司诉讼、口舌是非",
      "贵人小人、合作纠纷",
      "疾病灾咎、安危祸福",
      "婚嫁、动土、出行",
      "失脱疑难、来意虚实",
    ],
    typicalQuestions: ["上司对我什么看法?", "朋友借钱会还吗?"],
  },
  "06": {
    category: "宅墓气场、环境布局与方位趋吉.",
    coreMethod: "形法理气, 龙穴砂水, 罗盘定向.",
    characteristics: "从环境入手, 适合选址与长期布局规划.",
    advantages: [
      "从环境入手, 适合选址与布局",
      "可配合居住、办公长期规划",
      "形法理气体系传承完整",
    ],
    recommendedFor: [
      "住宅、店铺选址",
      "办公室布局调整",
      "阴宅择地 (需专业指导)",
      "化煞补局思路参考",
    ],
    typicalQuestions: ["这房子适合住吗?", "店铺朝向如何调整?"],
  },
  "09": {
    category: "人生阶段运势与天象变局.",
    coreMethod: "七政四余等星体推运.",
    characteristics: "从天象角度补充命理, 适合论阶段转折.",
    advantages: [
      "从天象角度补充命理视角",
      "适合论阶段运势与变局",
      "可与子平、紫微对照",
    ],
    recommendedFor: [
      "人生阶段转折",
      "重大决策前的天象参考",
      "流年重点与避凶",
    ],
    typicalQuestions: ["今年天象对我有何影响?"],
  },
  "11": {
    category: "人生细节和心理状态 (性格、职业倾向、人际关系、具体事件轨迹).",
    coreMethod: "十二宫、百余颗星曜、四化飞星、庙旺利陷.",
    characteristics:
      "像「人生模拟沙盘」, 信息密度高, 擅长描绘生活画面和心理活动, 对具体年份的推断比八字更细腻.",
    advantages: [
      "十二宫分工细, 人事刻画具体",
      "四化飞星便于看变化",
      "大限、流年体系完整",
    ],
    recommendedFor: [
      "职业适性与才华方向",
      "感情模式与配偶缘",
      "财帛管理与投资倾向",
      "人际格局与贵人位置",
      "流年重点宫位与注意事项",
    ],
    typicalQuestions: ["我适合做哪一行?", "今年换工作会遇到什么情况?"],
  },
  "12": {
    subtitle: "轻量工具",
    category: "合盘、测字、解梦、诸葛神数等快捷工具 (相术、择日、杂占典籍仍保留在库中, 暂不单独开 Tab).",
    coreMethod: "规则引擎 + 典籍 RAG + AI 解读.",
    characteristics:
      "与主排盘 Tab 互补: 合盘看双人, 测字/解梦/诸葛神数看文字与梦境等轻量问事, 按工具逐步开放.",
    advantages: [
      "入口集中, 不干扰八字/六爻等主流程",
      "合盘支持场景分流(婚恋/合作)",
      "测字、解梦、诸葛神数将迁入本专区典籍库",
    ],
    recommendedFor: [
      "双人婚恋或合作合盘",
      "测字问事、梦境象意",
      "诸葛神数三字报卦",
    ],
    typicalQuestions: [
      "我们适合结婚吗?",
      "这个字怎么解?",
      "此梦何意?",
    ],
  },
  "13": {
    category: "具体问事的象征解读 (感情、事业、抉择、年运等).",
    coreMethod: "78 张塔罗牌、牌阵位置语义、正逆位、公版典籍 RAG + AI 中文解读.",
    characteristics:
      "西方象征体系, 擅长心理投射与情境梳理; 支持韦特、马赛、托特三套牌与多种牌阵.",
    advantages: [
      "牌阵灵活, 从单牌到凯尔特十字",
      "正逆位丰富解读层次",
      "AI 可自动推荐牌阵并多轮追问",
    ],
    recommendedFor: [
      "感情与关系走向",
      "职业与抉择",
      "二选一决策",
      "年运与阶段主题",
    ],
    typicalQuestions: ["这次换工作合适吗?", "我们的关系会如何发展?"],
  },
};

export function getDisciplineIntro(tabId: string): DisciplineIntro | null {
  return DISCIPLINE_INTROS[tabId] ?? null;
}

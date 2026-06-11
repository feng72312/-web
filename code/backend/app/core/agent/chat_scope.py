from __future__ import annotations

import re

CHAT_SCOPE_GUARDRAIL = (
    "【服务范围】你只回答预测、命理、占卜、风水、起名、合盘、择日及相关术数问题。"
    "若用户提问与术数无关(如编程、作业、菜谱、闲聊八卦、泛娱乐、无关翻译等), "
    "请礼貌拒绝并引导其回到问事、排盘、解读或择术方向, 不要展开无关内容。"
    "若问事涉及健康、法律、投资等重大决策, 可结合术数给趋势参考, "
    "但必须提醒用户咨询对应领域专业人士。"
    "【输出禁忌】禁止在回复末尾添加免责声明、娱乐参考、AI生成、仅供娱乐等套话, "
    "不要提及模型名称或服务商."
)

_ON_TOPIC_HINTS: tuple[str, ...] = (
    "八字",
    "紫微",
    "六爻",
    "梅花",
    "奇门",
    "大六壬",
    "塔罗",
    "风水",
    "命盘",
    "合盘",
    "运势",
    "婚姻",
    "事业",
    "财运",
    "流年",
    "大运",
    "起卦",
    "排盘",
    "用神",
    "占卜",
    "命理",
    "五行",
    "十神",
    "夫妻",
    "感情",
    "工作",
    "升学",
    "考试",
    "择日",
    "起名",
    "姓名",
    "星命",
    "卦象",
    "本卦",
    "变卦",
    "宫位",
    "问事",
    "解读",
    "术数",
    "结婚",
    "离婚",
    "恋爱",
    "合作",
    "搬家",
    "出行",
    "官非",
    "健康",
    "牌阵",
    "卦",
    "盘",
    "预测",
)

_OFF_TOPIC_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"写.{0,8}代码|编程|debug|修bug|爬虫脚本|部署教程",
        r"\b(python|javascript|typescript|react|vue|java)\b",
        r"菜谱|怎么做.{0,6}菜|食材用量|健身计划",
        r"翻译.{2,40}英|中英互译|译成英文",
        r"写作文|论文提纲|读后感|写简历|营销文案",
        r"游戏攻略|电视剧|明星八卦|饭圈|旅游攻略",
        r"讲个笑话|段子|绕口令|陪聊|角色扮演",
    )
)

SCOPE_REFUSAL = (
    "本助手仅解答预测、命理、占卜、排盘、风水、起名、择日与问事相关内容。"
    "请围绕你的具体问题、命盘、卦象、牌阵或合盘继续提问。"
)


def is_chat_message_in_scope(message: str) -> tuple[bool, str | None]:
    text = message.strip()
    if len(text) < 2:
        return False, "请输入与问事或术数相关的内容."
    lowered = text.lower()
    if any(hint in text or hint in lowered for hint in _ON_TOPIC_HINTS):
        return True, None
    if any(pattern.search(text) for pattern in _OFF_TOPIC_PATTERNS):
        return False, SCOPE_REFUSAL
    return True, None

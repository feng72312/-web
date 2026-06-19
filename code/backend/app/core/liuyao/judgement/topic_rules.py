from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TopicRule:
    topic_id: str
    topic_label: str
    keywords: tuple[str, ...]
    candidate_yong_shen: str
    alternate_yong_shen: tuple[str, ...] = ()
    special_rules: tuple[str, ...] = ()
    priority: int = 10
    rule_id: str = ""


TOPIC_RULES: tuple[TopicRule, ...] = (
    TopicRule(
        "wealth",
        "求财",
        ("财", "钱", "投资", "生意", "借贷", "工资", "收入", "求财", "盈利"),
        "妻财",
        rule_id="topic:wealth:yong_shen:qicai",
    ),
    TopicRule(
        "career",
        "求官仕途",
        ("官", "工作", "升职", "事业", "职位", "领导", "功名", "仕途", "考试录用"),
        "官鬼",
        rule_id="topic:career:yong_shen:guangui",
    ),
    TopicRule(
        "exam",
        "考试文书",
        ("考试", "学习", "文书", "证书", "学校", "录取", "学业", "文凭"),
        "父母",
        rule_id="topic:exam:yong_shen:fumu",
    ),
    TopicRule(
        "marriage",
        "婚姻感情",
        ("婚", "恋", "嫁", "娶", "感情", "对象", "夫妻", "订婚"),
        "妻财",
        ("官鬼", "世爻"),
        ("男占婚多取妻财, 亦看世应",),
        12,
        "topic:marriage:yong_shen:qicai",
    ),
    TopicRule(
        "self_illness",
        "自占疾病",
        ("我病", "自占", "自己病", "我身体", "我健康"),
        "世爻",
        ("官鬼",),
        ("自占病先看世爻, 官鬼为病象",),
        14,
        "topic:self_illness:yong_shen:shi",
    ),
    TopicRule(
        "illness",
        "疾病",
        ("病", "医", "身体", "疾", "健康", "患", "症"),
        "官鬼",
        ("世爻",),
        ("占病官鬼为病, 自占兼看世爻",),
        11,
        "topic:illness:yong_shen:guangui",
    ),
    TopicRule(
        "parents",
        "父母长辈",
        ("父母", "父亲", "母亲", "长辈", "老人"),
        "父母",
        rule_id="topic:parents:yong_shen:fumu",
    ),
    TopicRule(
        "siblings",
        "兄弟同辈",
        ("兄弟", "竞争", "同辈", "合伙", "手足"),
        "兄弟",
        rule_id="topic:siblings:yong_shen:xiongdi",
    ),
    TopicRule(
        "children",
        "子孙孕产",
        ("子", "孕", "产", "生育", "后代", "怀孕", "子女"),
        "子孙",
        rule_id="topic:children:yong_shen:zisun",
    ),
    TopicRule(
        "lawsuit",
        "官非诉讼",
        ("官非", "诉讼", "官司", "口舌", "是非", "避讼"),
        "官鬼",
        ("子孙",),
        ("官非看官鬼, 子孙可解",),
        rule_id="topic:lawsuit:yong_shen:guangui",
    ),
    TopicRule(
        "travel",
        "出行",
        ("出行", "旅行", "远行", "出门", "路程", "舟车"),
        "世爻",
        ("官鬼",),
        rule_id="topic:travel:yong_shen:shi",
    ),
    TopicRule(
        "lost_item",
        "失物",
        ("失物", "丢失", "遗失", "找寻", "找东西"),
        "妻财",
        rule_id="topic:lost_item:yong_shen:qicai",
    ),
    TopicRule(
        "weather",
        "天气",
        ("天气", "晴雨", "风雨", "下雨", "下雪"),
        "父母",
        ("子孙",),
        rule_id="topic:weather:yong_shen:fumu",
    ),
    TopicRule(
        "house",
        "田宅",
        ("房", "宅", "屋", "置业", "田宅", "搬迁"),
        "父母",
        ("官鬼",),
        rule_id="topic:house:yong_shen:fumu",
    ),
    TopicRule(
        "friend",
        "朋友外人",
        ("朋友", "外人", "应事"),
        "应爻",
        special_rules=("问朋友外人以应爻为用神, 常不验",),
        priority=5,
        rule_id="topic:friend:yong_shen:ying",
    ),
)

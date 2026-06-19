from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.agent.prompts import _format_excerpts, build_chart_context
from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.liunian_context import (
    build_liunian_prompt_block,
    is_liunian_event_question,
)
from app.core.knowledge.qishi_context import build_qishi_prompt_block
from app.core.knowledge.tiaohou_context import build_tiaohou_prompt_block
from app.core.knowledge.mcq_reasoning_mode import should_structured_mcq_reasoning
from app.core.knowledge.contest_channel_route import (
    has_explicit_timing_signal,
    is_yingqi_question,
    uses_full_judgement_chain,
)
from app.core.knowledge.option_exclusion import build_option_exclusion_block
from app.core.knowledge.models import CompressedContext
from app.core.knowledge.family_option_scorer import build_family_option_score_block
from app.core.knowledge.family_subtheme import infer_family_subtheme
from app.core.knowledge.children_option_scorer import build_children_option_score_block
from app.core.knowledge.children_subtheme import infer_children_subtheme
from app.core.knowledge.career_subtheme import infer_career_subtheme
from app.core.knowledge.health_subtheme import infer_health_subtheme
from app.core.knowledge.target_year_block import build_health_option_years_anchor
from app.core.knowledge.year_option_scorer import build_year_option_score_block
from app.core.knowledge.luck_prompt_util import is_year_option_mcq

DEFAULT_FEWSHOT_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "contest8_fewshot.json"
)

CONTEST_REASONING_GUIDE = """
命理师大赛选择题作答要点:
0. 先读「穷通宝鉴调候」与「滴天髓气势」: 定日干月令喜用忌, 再论格局体用.
1. 先读「经典判盘链预结论」: 选项须与判盘链互证, 冲突时以调候/格局/岁运主裁为准.
2. 先定格局与体用, 再看日主强弱与用神喜忌, 勿脱离命盘臆测.
3. 问职业/财运/事业: 结合财星、官杀、食伤与大运流年, 看何运得助或受制.
4. 问婚姻/感情/子女: 看配偶星、桃花、合冲刑害, 及对应大运流年是否引动.
5. 问健康: 看五行偏枯、刑冲穿害, 对应脏腑与大运流年加重或缓解.
6. 问具体年份事件: 必须对照大运、流年与四柱作用, 勿只凭单柱或直觉.
7. 题目若给出虚龄或大限区间, 先用大运起运年龄换算到公历流年再判断.
8. 四选一须选最贴合命盘与运程的一项; 相近时选与用神/忌神作用最一致者.
""".strip()

JUDGEMENT_MANDATORY_GUIDE = """
判盘链硬约束:
- 调候/格局/岁运/气势为典籍主裁, 命例摘录仅可参考, 不得推翻主裁.
- 选项若与【穷通宝鉴调候】【滴天髓气势】【流年岁运规则】或判盘链预结论明显矛盾, 优先排除.
- 不得凭常识叙事或常见人生经验猜选.
""".strip()

QISHI_REASONING_GUIDE = """
气势体用题: 先看五行偏枯与清浊流通, 再与格局喜忌、调候用神对照.
偏旺宜泄宜制, 偏弱宜帮宜印; 勿把财星官杀简单等同职业或财运答案.
""".strip()

LIUNIAN_EVENT_GUIDE = """
流年事件题: 必须用上文「流年岁运规则」「流年时间轴」与「目标年结构化断语」中的目标年干支、十神、冲合.
先定目标年所在大运, 再论流年太岁与四柱作用; 岁运并临、真太岁、冲合刑害须逐项核对.
官杀/七杀/伤官见官多关联官非压力; 偏财正财多关联财运而非必然横财; 印星受克多关联母亲健康文书; 食伤多关联变动口舌.
不得凭常识或常见叙事猜选, 须用命盘线索排除矛盾选项.
""".strip()

MARRIAGE_REASONING_GUIDE = """
婚姻感情题断法:
1. 男命配偶星为正财/偏财, 女命为正官/七杀; 先看配偶星在命局是否透干通根, 再看日支(配偶宫)刑冲合害.
2. 有明确目标年/虚龄/大运时: 须先读【虚龄大运锚点】与流年时间轴, 再论该年是否引动配偶星或配偶宫; 勿跳过岁运凭原局猜婚变.
3. 无明确目标年: 以原局结构+当前大运趋势推断婚恋状态; 不得默认选「离婚/外遇/从未结婚」等极端项, 须逐项排除.
4. 合冲配偶宫、配偶星透干/入墓/被合去、桃花引动 -> 可论婚恋变动; 仅印比旺而无财官杀引动 -> 不宜断闪婚或热恋.
5. 选项含「奉子成婚/冲喜/联姻/外遇」等叙事时, 须与流年十神及冲合一一对照, 勿凭常见故事选.
6. 判盘链 confidence 非 strong 或有 conflicts 时, 至少保留 2 个待选, 禁止断言式排除至唯一项.
""".strip()

HEALTH_REASONING_GUIDE = """
健康疾病题断法:
1. 五行脏腑: 金=肺/大肠/骨骼/皮肤; 木=肝胆/神经; 水=肾/膀胱/泌尿/耳; 火=心/小肠/血脉/眼; 土=脾胃/肌肉/消化.
2. 病灾信号: 七杀/官杀攻身、伤官见官、枭印夺食、用神或印星受冲穿刑、日支(身体)被冲 -> 可论病伤手术; 须与选项字面症状/器官一致才可选.
3. 有目标年/虚龄/大运时: 须先读【虚龄大运锚点】与流年时间轴, 再论该年是否加重病灾; 勿跳过岁运凭原局猜病名.
4. 区分手术/住院/癌/骨折/慢性/先天: 突发外伤看冲刃; 慢性看五行偏枯; 婴幼儿先天病看原局结构, 勿用后期流年硬套.
5. 选项含多种近义病名(如乳癌/妇科病/鼻癌)时, 须逐项对照选项字面, 禁止仅因见七杀就选最重项.
6. 财旺、食伤旺之年不等于健康恶化; 有财无官杀冲克 -> 不宜优先选重病/手术/意外项.
7. 判盘链 confidence 非 strong 或有 conflicts 时, 至少保留 2 个待选, 禁止断言式排除至唯一项.
""".strip()

HEALTH_YEAR_EVENT_GUIDE = """
健康应期/择年题断法:
1. 须提取每个选项中的公历年份, 或题干目标年, 分别定位大运与流年干支, 逐项核对.
2. 病灾/手术/意外之年: 优先看七杀/官杀透干、伤官见官、用神或印星被冲合穿、日支被冲.
3. 题干若给虚龄/大运名, 先读【虚龄大运锚点】, 不得换算到其它大运.
4. 若有【健康选项年份锚点】, 须与排盘表互证, 不得单凭分数或常识叙事作答.
""".strip()

HEALTH_DAYUN_SPAN_GUIDE = """
大运期间疾病题断法:
1. 题干虚龄区间或具名大运即本题目标运; 须先读【虚龄大运锚点】, 在该运内看五行偏枯与十神.
2. 选项为器官/系统(呼吸/泌尿/肠胃等)时, 按五行脏腑与运限十神取象, 须与选项字面一致.
3. 勿把其它大运的典型病象硬套到本题区间; 运干运支与日主/用神关系决定哪类系统易出问题.
""".strip()

HEALTH_DIAGNOSIS_GUIDE = """
疾病种类/器官/诊断题断法:
1. 先读选项字面病名或器官, 再查命盘五行与宫位是否支撑; 禁止先定抽象病灾再硬套选项.
2. 心脏/肺/脑/肾/肠胃/骨骼/皮肤等须与五行及选项一致: 火=心血脉; 金=肺骨; 水=肾泌尿; 土=脾胃; 木=肝胆.
3. 婴幼儿/先天病: 以原局偏枯、时柱/日支受冲为主; 勿用尚未发生的大运流年编造故事.
4. 手术器官题: 题干若给年份, 须定位该年流年冲合与选项器官五行对应关系.
""".strip()

HEALTH_STATUS_GUIDE = """
健康状况/症状叙事题断法:
1. 作答顺序: 先读每个选项的字面症状/体重/器官/行为(吸烟/运动等), 再查命盘是否支撑; 禁止先写抽象病象块再硬套.
2. 问目前/现时/某年健康状况: 有目标年则须叠该年流年; 无目标年则以原局+当前大运趋势推断.
3. 选项含年份+事件叙事(如某年确诊/某年手术)时, 须逐条核对各选项年份的岁运, 勿只选听起来最严重的项.
4. 相近症状(肥胖/肝病/脚患/鼻癌/无节制吸烟等)须逐项排除, 勿凭常见职业病常识猜中间项.
""".strip()

HEALTH_MANDATORY_GUIDE = """
健康题强制约束:
- 禁止仅因七杀/官杀透干就断重病、残疾或必然手术; 须选项字面含对应症状/器官/事件才可判符合.
- 禁止把财年、食伤年一律断成健康恶化; 须见病灾信号(冲用神/印星/日支)再论.
- 病名/器官/系统近义时(如乳癌vs妇科、心脏vs肺炎), 须对照选项字面, 不得凭十神大类模糊选一项.
- confidence 非 strong 时至少保留 2 项待选.
""".strip()

_HEALTH_SUBTHEME_GUIDES = {
    "health-year-event": HEALTH_YEAR_EVENT_GUIDE,
    "health-dayun-span": HEALTH_DAYUN_SPAN_GUIDE,
    "health-diagnosis": HEALTH_DIAGNOSIS_GUIDE,
    "health-status": HEALTH_STATUS_GUIDE,
}


def get_health_subtheme_guide(subtheme: str | None) -> str:
    if not subtheme:
        return HEALTH_REASONING_GUIDE
    extra = _HEALTH_SUBTHEME_GUIDES.get(subtheme, "")
    if extra:
        return HEALTH_REASONING_GUIDE + "\n" + extra
    return HEALTH_REASONING_GUIDE


HEALTH_YEAR_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【置信】
写明判盘链 confidenceBand (strong/medium/weak) 与是否存在 conflicts; 若非 strong 或有冲突, 不得断言式排除, 至少保留 2 项待选.

【病灾象】
写出原局五行偏枯、用神/印星/日支受冲合情况, 及题干目标年的大运流年十神(来自上文排盘).

【选项年份】
逐条写出各选项涉及的公历年份、虚龄、所在大运干支、流年干支与天干十神.

【选项排除】
A: 符合/不符合 - 一句理由(须引用选项年份岁运与病灾象, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项的年份/病灾链最贴合; 若两项仍接近, 写明差在哪.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

HEALTH_DAYUN_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【置信】
写明判盘链 confidenceBand 与 conflicts; 非 strong 时至少保留 2 项待选.

【运限病象】
写出题干虚龄区间/大运干支、运干十神、五行偏枯, 及该运内易出问题之脏腑系统(来自上文锚点与排盘).

【选项对照】
A: 符合/不符合 - 一句理由(须对照选项字面器官/系统与运限五行十神)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项最贴合本题大运区间; 若两项仍接近, 写明差在哪.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

HEALTH_DIAGNOSIS_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【置信】
写明判盘链 confidenceBand 与 conflicts; 非 strong 时至少保留 2 项待选.

【五行脏腑】
写出原局五行偏枯、相关宫位/十神, 及题干目标年(若有)的流年冲合.

【选项排除】
A: 符合/不符合 - 一句理由(须引用选项字面病名/器官与五行, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项最贴合; 若两项仍接近, 写明差在哪.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

HEALTH_STATUS_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【置信】
写明判盘链 confidenceBand 与 conflicts; 非 strong 时至少保留 2 项待选.

【选项对照】
A: 符合/不符合 - 一句理由(须先读选项字面症状/行为/年份叙事, 再引命盘或目标年流年)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项最贴合; 禁止仅因十神大类选最重或最轻项.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

GUANFEI_REASONING_GUIDE = """
官非题: 官杀、伤官见官、劫财逢冲多主压力与官非; 须对照选项中的牢狱/扣留/刑事关键词.
有财无官杀之年勿优先选横财或纯健康项.
""".strip()

XUELI_REASONING_GUIDE = """
学历题断法(静态层级):
1. 先看第1~3步大运十神, 再看原局印星/食伤/财星关系; 勿只看原局有印就断大学以上.
2. 印星旺不等于高学历: 财坏印、印被合去、官杀攻身、身弱印轻 -> 学业中断或仅基础教育.
3. 食伤过旺无制、比劫夺财 -> 贪玩分心, 未必能完成高等教育; 驿马、偏财动 -> 海外或异地读书.
4. 层级校准: 仅有印但身弱/财重 -> 中学或专科; 印轻受克 -> 小学/辍学/肄业; 勿默认选最高项.
5. 香港用语: 中五/中六/中七对应本地中学层级, 勿与大学/硕士混为一档.
6. 禁止因「伤官佩印」「偏印透出」就直接选大学/硕士; 须在选项层级中择最贴合者.
7. 选项同为「大学」层级时: 驿马/冲马、偏财动、伤官无制多见海外或玩乐读书; 印星清纯、官印相生多见专心本地升学.
8. 极低学历(小学/辍学/肄业): 财坏印而印星有根、仅受制未绝 -> 倾向小学等最低完成档; 官伤混杂、大运冲克印星 -> 倾向辍学; 勿在小学与辍学间默认选较高项.
9. 同层级比较: 若多个选项均为大学层级, 须在大学项内比较(海外/玩乐/专心), 勿因财坏印直接降级到大专; 仅当全部大学项均不符合时才考虑大专.
""".strip()

XUELI_YINGQI_MANDATORY_GUIDE = """
学历应期题(选项含升学/毕业年份):
- 须提取每个选项中的公历年份, 分别定位所在大运与流年干支, 逐项核对是否支撑该选项.
- 勿当作静态层级题; 勿跳过选项年份直接凭原局断学历高低.
- 若上文有【选项年份岁运评分】, 须优先参考并与排盘表互证.
""".strip()

XUELI_YINGQI_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【选项年份】
逐条写出各选项涉及的公历年份、虚龄、所在大运干支、流年干支与天干十神(来自上文排盘).

【选项排除】
A: 符合/不符合 - 一句理由(须引用选项年份的岁运十神, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项的升学/毕业年份链最贴合命盘; 若两项仍接近, 写明差在哪.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

CAREER_MAJOR_GUIDE = """
科系取向题: 在确认有高等教育前提下, 按五行十神取象:
- 木火偏旺或食伤泄秀 -> 文艺类(美术/音乐/设计/传媒)
- 金水偏旺或官杀清透 -> 理工/金融/会计/法律
- 土金厚重 -> 工程/建筑/实务/管理
- 同一五行对应多个行业时, 须与选项名称逐项对照, 勿凭热门专业常识猜选.
""".strip()

CAREER_WEALTH_GUIDE = """
财富/收入/投资题断法:
1. 财旺不等于发财: 须同时看日主能否任财、食伤是否生财、比劫是否夺财、财星是否有根气.
2. 身弱财多: 多主财来财去、难聚财或负债, 勿见偏财就断横财; 有财无扶身大运 -> 不宜断大富.
3. 食伤生财、官印护财、大运扶身承财 -> 可论收入提升或创业有成; 财库逢冲合须分入库与破库.
4. 问投资/理财/买房: 偏财动、劫财透、财杀相战 -> 倾向亏损或负债; 印比扶身、官印相生 -> 倾向稳定增值.
5. 选项含具体金额/负债/投资结果叙事时, 须与原局财印比及大运流年互证, 勿凭故事常识选中间项.
6. 有明确目标年/选项年份时: 须先定位大运流年, 再论该年财星引动是否真主得财或破财.
""".strip()

CAREER_STATUS_GUIDE = """
职业/行业/职位现状题断法:
1. 作答顺序: 先读每个选项的字面职业/行业名称, 再查命盘是否支撑该具体职业; 禁止先写抽象十神结论再硬套选项.
2. 官杀看职位/体制: 正官/七杀透干不等于必然公务员; 须选项含公职/管理/执法语义方可选; 七杀旺亦可为技术、销售、竞争性行业.
3. 印星看资质/稳定: 印旺偏教育/文职/专业技术; 但印弱、财坏印、食伤旺时仍可从事保险、销售、手艺、自营, 勿见无印就排除非文职.
4. 食伤看手艺/口才/创意: 理发、厨师、设计、律师、传媒等须选项字面吻合; 勿仅因食伤透干就把所有「服务/手艺」选项判符合.
5. 财星看经商/销售: 偏财旺可经商或金融销售; 但财旺不等于老板, 打工/受薪/推销仍常见; 证券/保险/地产销售多取偏财+食伤, 不等于企业主.
6. 常见职业取象(须与选项字面一致才可选):
   - 制造业/工厂/蓝领: 金土、官杀、比劫
   - 银行/金融/证券/保险推销: 偏财、食伤、金水
   - 会计/审计/数据处理: 金、正财、印星
   - 律师/公务员/管理: 官杀、官印相生
   - 理发/美容/手艺: 水木、食伤、偏财
   - 教师/文职: 印星、正官
   - 护士/医护: 印星、官杀、土金
7. 学历-职业层级题: 须先定原局+大运可达的学历上限, 再选对应选项; 印食伤配置能支撑博士/高工则勿选「摆摊/高职/小老板」等低层级项.
8. 工作性质/收入叙事题(选项较长): 须逐条核对收入、负债、稳定/打工/自营等叙事, 勿只凭十神大类选「中间项」.
9. 问目前/现职: 以原局+当前大运为主; 无明确目标年时不编造流年故事.
""".strip()

CAREER_YEAR_EVENT_GUIDE = """
职业/事业应期题断法:
1. 须提取每个选项中的公历年份或虚龄区间, 分别定位所在大运与流年干支, 逐项核对.
2. 转行/创业/升职/失业: 看官杀(职位)、财星(收入/创业)、食伤(变动/表达)在该年是否透干引动或冲合原局.
3. 大运切换之年: 须先定进入何运, 再叠流年; 勿把前运末年的惯性延续到后运.
4. 题干含虚龄/大运名时, 先读【虚龄大运锚点】, 不得换算到其它大运.
5. 选项为叙事(如「一直打工」「创业失败后再就业」)时, 须与运限十神及冲合逐条对照, 勿凭人生故事选.
6. 若有【选项年份岁运评分】, 须与排盘互证, 不得单凭分数作答.
""".strip()

_CAREER_SUBTHEME_GUIDES = {
    "wealth": CAREER_WEALTH_GUIDE,
    "career-status": CAREER_STATUS_GUIDE,
    "career-year-event": CAREER_YEAR_EVENT_GUIDE,
    "major-industry": CAREER_MAJOR_GUIDE,
}


def get_career_subtheme_guide(subtheme: str | None) -> str:
    if subtheme and subtheme in _CAREER_SUBTHEME_GUIDES:
        return _CAREER_SUBTHEME_GUIDES[subtheme]
    return QISHI_REASONING_GUIDE


CAREER_WEALTH_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【财星体用】
原局财星/食伤/比劫关系及当前大运对任财能力的影响(各一句, 引用排盘).

【选项排除】
A: 符合/不符合 - 一句理由(须引用十神或大运, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项最贴合; 若两项仍接近, 写明差在哪.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

CAREER_WEALTH_YEAR_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【财星体用】
原局财星/食伤/比劫关系; 财富应期题须明确所用十神.

【选项年份】
逐条写出各选项涉及的公历年份、所在大运、流年干支及对财星/任财能力的作用.

【选项排除】
A: 符合/不符合 - 一句理由(须引用选项年份与财星, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项与财富引动最贴合.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

CAREER_STATUS_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【选项对照】
A(写出该选项职业/行业关键词): 符合/不符合 - 一句理由(须对照选项字面职业, 引用排盘十神, 勿空泛)
B(写出该选项职业/行业关键词): 符合/不符合 - 一句理由
C(写出该选项职业/行业关键词): 符合/不符合 - 一句理由
D(写出该选项职业/行业关键词): 符合/不符合 - 一句理由

【结论】
说明哪一选项最贴合; 若两项仍接近, 写明差在哪及为何取该项.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

CAREER_STATUS_MANDATORY_GUIDE = """
职业现状题: 须先逐条读选项字面职业/行业/收入叙事, 再与命盘互证.
禁止仅因七杀/正官透干就选公务员/执法; 禁止仅因食伤透干就选律师/厨师/理发师/设计.
学历-职业题须先定可达学历层级, 再选对应职业选项; 勿默认选最低或最高极端项.
""".strip()

CAREER_YEAR_EVENT_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【目标年/运限】
写出题干目标公历年或虚龄区间、所在大运、流年干支、天干十神、关键冲合(来自上文排盘).

【选项排除】
A: 符合/不符合 - 一句理由(须引用十神或冲合, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项最贴合; 若两项仍接近, 写明差在哪及如何取舍.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

CAREER_MAJOR_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【五行科系】
原局五行偏枯、食伤/印星/官杀对专业取向的指示(各一句, 引用排盘).

【选项排除】
A: 符合/不符合 - 一句理由(须引用五行十神取象, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项科系最贴合.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

CAREER_YINGQI_MANDATORY_GUIDE = """
职业财运应期题(选项含年份或题干含虚龄/大运):
- 须提取每个选项中的公历年份, 分别定位大运与流年, 核对是否引动财星/官杀/食伤.
- 财富题: 财旺不等于发财, 须看日主能否任财; 勿跳过选项年份只凭原局猜.
- 职业变动题: 看官杀(职位)、食伤(变动)在该年是否透干或冲合.
- 若上文有【选项年份岁运评分】, 须与排盘互证, 不得单凭分数作答.
""".strip()

STATIC_XUELI_MANDATORY_GUIDE = """
静态学历题: 以原局印食伤财与早年大运为主; 勿强行编造具体流年故事.
选项层级接近时, 优先排除明显过高(博士/硕士)或过低(文盲)的极端项.
极低学历题: 印星得令有根而仅财坏印 -> 优先小学等最低完成档, 勿默认选辍学.
""".strip()

STATIC_XUELI_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【印星学业】
原局印星/食伤/财印关系, 以及第1~2步大运十神对学业的影响(各一句, 引用排盘).

【层级排除】
A: 过高/过低/可能 - 一句理由(须引用十神或大运, 勿空泛)
B: 过高/过低/可能 - 一句理由
C: 过高/过低/可能 - 一句理由
D: 过高/过低/可能 - 一句理由

【结论】
说明为何剩余一项层级最贴合; 若两项仍接近, 写明差在哪.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

FAMILY_ORIGIN_REASONING_GUIDE = """
家庭出身题断法(静态):
1. 年柱看祖上及早年家运, 月柱为父母宫; 男命偏财为父、正印为母, 女命偏财为父、正印为母(以盘内财印位置为准).
2. 贫富: 须区分「家庭财力(父星/年柱财星)」与「日主能否任财」; 身弱财多主自身难聚财, 不必然等于贫穷家庭出身.
3. 财旺身强或官印相生可小康以上; 身弱财多、比劫夺财、财星入墓被冲 -> 倾向贫或普通; 勿见财就断富, 亦勿见财杀旺一律判贫.
4. 父星(偏财)得令、有库、杀印护财或年柱财旺时, 仍可选「富贵家庭出身」, 即使日主偏弱; 但选项仅有贫/小康/富贵层级且无父母职业细节时, 身弱财多、父星不旺 -> 优先贫穷, 勿升档到小康.
5. 父母寿元: 父星受克、合去、入墓或坐死绝 -> 父短寿; 母星(印)有根得生 -> 母长寿; 勿颠倒父母寿元.
6. 家庭关系: 印星受克、比劫争财、伤官见官 -> 父母不和或缘薄; 比劫看兄弟姐妹数量与亲疏.
7. 选项仅贫/富/小康/富贵层级时: 优先排除孤儿/大富等极端; 财旺身弱 -> 贫或普通; 勿凭「偏财藏、月柱有财」就选父从商/小康等过高叙事.
8. 题干问「出身贫或富/家境」且选项仅为贫/小康/富贵/孤儿层级(无父母职业细节): 以年柱/月柱财星、父星是否得库得令论家庭财力; 年柱财库旺、父星有根时可选「富贵家庭出身」, 与日主身弱不矛盾.
9. 选项含「孤儿院/寄养」: 仅当父母星全无或年月柱严重冲刑时才可选; 勿因身弱杀重就选孤儿, 父母星有库时应先在贫/小康/富贵中比较.
10. 勿默认选小康; 看财星是否真旺、日主能否任财, 勿凭「财官印俱全」就断富贵.
""".strip()

FAMILY_DEATH_FATHER_GUIDE = """
丧父应期/父星题断法:
1. 只论偏财(父星)及年柱/月柱, 勿用印星断丧父.
2. 流年冲、合、刑、克偏财或冲父星之根 -> 丧父候选; 合去父星(如甲己合财)在童限亦可应.
3. 印星透干生扶、合化助身之年通常非丧父; 勿仅因父星 merely 透干就选.
4. 须逐选项比对; 若有【家庭出身选项规则分】, 须与排盘互证, 不得单凭分数否定冲根/合去之年或推翻主象.
""".strip()

FAMILY_DEATH_MOTHER_GUIDE = """
丧母应期/母星题断法:
1. 只论正印/偏印(母星)及月柱, 勿用偏财断丧母.
2. 印星受冲克、入墓、被财坏或大运损印 -> 丧母候选; 巳亥冲、财坏印等优先.
3. 流年生扶、合化或伏吟助印星(如卯戌合火助印)通常非丧母, 规则分低者倾向排除.
4. 须逐选项比对; 若有【家庭出身选项规则分】, 须与排盘互证, 不得单凭分数作答.
""".strip()

FAMILY_WEALTH_TIER_GUIDE = """
家庭贫富层级题断法:
1. 年柱看祖上及早年家运, 月柱为父母宫; 问家庭出身时看父星/年柱财库, 与日主身弱不矛盾.
2. 财旺身强或官印相生可小康以上; 身弱财多主自身难聚财, 不必然等于贫穷家庭出身.
3. 父星得令、有库、杀印护财或年柱财旺时, 仍可选「富贵家庭出身」; 选项仅有贫/小康/富贵层级时, 勿升档到叙事项.
4. 选项含「孤儿院/寄养」: 仅当父母星全无或年月柱严重冲刑时才可选.
5. 若有【家庭出身选项规则分】, 须与年月柱财星互证; 规则分不得作为唯一依据, 身弱财多仍须优先贫穷选项.
""".strip()

FAMILY_RELATION_GUIDE = """
家庭关系/父母状况题断法:
1. 父母关系: 印星受克、比劫争财、伤官见官 -> 不和或缘薄; 财印相战主吵闹, 冲合严重主离异.
2. 父母职业/背景叙事: 偏财主父、印星主母; 财库/偏财旺 -> 父从商; 印旺 -> 母公职或文职.
3. 兄弟姐妹: 比劫看数量与亲疏; 伤官旺则兄弟姐妹缘薄.
4. 选项含长叙事时须逐条核对与父母星是否一致, 勿凭常识选「小康」或「和谐」.
5. 若有【家庭出身选项规则分】, 规则分仅供参考, 须与父母星/年月柱互证.
""".strip()

_FAMILY_SUBTHEME_GUIDES = {
    "family-death-father": FAMILY_DEATH_FATHER_GUIDE,
    "family-death-mother": FAMILY_DEATH_MOTHER_GUIDE,
    "family-wealth-tier": FAMILY_WEALTH_TIER_GUIDE,
    "family-relation": FAMILY_RELATION_GUIDE,
}


def get_family_subtheme_guide(subtheme: str | None) -> str:
    if subtheme and subtheme in _FAMILY_SUBTHEME_GUIDES:
        return _FAMILY_SUBTHEME_GUIDES[subtheme]
    return FAMILY_ORIGIN_REASONING_GUIDE


STATIC_JIATING_MANDATORY_GUIDE = """
静态家庭出身题: 以年柱、月柱与父母星及早年大运为主; 勿强行编造无题干依据的流年故事.
贫富题: 身弱财多不为富(就命主而言), 但问家庭出身时仍须看父星/年柱财库; 年柱财旺仍可选富贵出身, 勿与丧父丧母题混论.
父母寿元题须先定父星母星再论长短, 勿颠倒.
""".strip()

STATIC_JIATING_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【父母家运】
年柱/月柱与父母星(财/印)关系, 以及第1~2步大运对父母星的影响(各一句, 引用排盘).

【选项排除】
A: 符合/不符合 - 一句理由(须引用父母星或年月柱, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明为何剩余一项最贴合; 若两项仍接近, 写明差在哪.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

JIATING_YINGQI_MANDATORY_GUIDE = """
家庭应期题(父母离世/变故年份或选项含年份):
- 须提取每个选项中的公历年份, 分别定位大运与流年, 核对是否引动父星/母星(财/印).
- 题干含「父亲/父」: 只论偏财(父星)及月柱/年柱; 查流年冲、合、刑、克偏财, 勿用印星断丧父.
- 题干含「母亲/母」: 只论正印/偏印(母星)及月柱; 查流年冲、合、刑、克印星, 勿用偏财断丧母.
- 丧父/丧母年: 合去父星(如甲己合财)、冲墓、七杀攻财、印星受冲等优先于「父星/母星 merely 透干」.
- 童限或未入大运之年, 若流年强引动对应父母星, 仍可选, 勿仅因年龄小排除.
- 丧父年: 流年冲父星之根(如亥冲午)、合去父星(甲己合等)在童限亦可应; 须比较各选项, 勿默认选最晚或冲力间接之年.
- 【选项年份岁运评分】仅供参考: 若流年直接冲/合父星根, 不得仅因规则分低就排除该年; 童限之年与冲根之年仍须保留为丧父候选.
- 丧母年: 流年生扶、合化或伏吟助印星(如卯戌合火、午火助印)通常非丧母; 优先选印星受冲克、入墓、被财坏或大运损印之年.
- 勿把「父星透干受克」或「地支刑动」默认当作最佳丧父/丧母年; 须逐选项比对, 引动明确且符合题干者优先.
- 若上文有【选项年份岁运评分】, 须与排盘互证, 但不得单凭分数否定冲根/合去之年.
""".strip()

JIATING_YINGQI_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【父母星】
先写父星(偏财)与母星(印)在命局位置; 本题问父亲则只评父星, 问母亲则只评母星.

【选项年份】
逐条写出各选项涉及的公历年份、所在大运、流年干支及对该题父母星的冲/合/克作用.

【选项排除】
A: 符合/不符合 - 一句理由(须引用选项年份与父母星, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项的年份与父母星引动最贴合.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

ZINV_REASONING_GUIDE = """
子女题断法(通用):
1. 时柱为子女宫; 男命以官杀为子女星, 女命以食伤为子女星, 勿颠倒.
2. 生育/得子之年: 流年引动子女星(透干、通根)或冲动子女宫(时支)为候选; 须逐选项年份核对.
3. 子女数量/状况叙事题: 须结合原局子女星强弱、时柱与大运趋势, 勿凭常识猜「多子」或「无子」.
4. 流产/子女有损: 子女星受冲克、时柱穿害, 或食伤/官杀被合去之年可论; 与顺利生产须区分.
""".strip()

CHILDREN_BIRTH_YEAR_GUIDE = """
子女出生年份题断法:
1. 先定性别: 男命只看官杀(正官/七杀)为子女星, 女命只看食伤(食神/伤官); 男命禁止把食伤当作生育主星.
2. 逐选项公历年份查大运流年: 子女星透干、通根或得生 -> 生育候选; 仅印星/比劫年而无子女星引动 -> 通常非生产年.
3. 时柱(时支)被冲、刑、合动常主子女宫动; 须同时见子女星(男官杀/女食伤)引动方可论生产, 勿仅凭时柱冲动选年.
4. 若有【子女选项规则分】, 须与排盘互证; 不得单凭分数作答, 亦不得忽略规则分较高的引动年.
""".strip()

CHILDREN_DAYUN_SPAN_GUIDE = """
大运期间子女运题断法:
1. 先读【虚龄大运锚点】: 若题干大运名称与虚龄区间不一致, 以虚龄对应的实际大运为准, 勿因名称不符拒答.
2. 在该运整体趋势下, 结合选项叙事(子女数量、平安、有损、外宠等)与原局子女星、时柱、妻星对照.
3. 叙事选项须逐项核对: 三子均平安/头胎有损/外宠生子等, 须有原局与运限依据, 勿凭故事常识选.
4. 选项内若含具体年份(如1996), 须在该运内叠流年核对, 勿脱离运限区间.
""".strip()

CHILDREN_STATUS_GUIDE = """
婚恋与子女状况题断法:
1. 先看配偶星(男财女官)与子女星(男官杀女食伤)在原局强弱, 再对照选项中的年份与叙事.
2. 未婚/无子女: 原局子女星弱、时柱空破, 或大运长期克子女星; 勿见有恋爱叙事就选已婚多子.
3. 奉子成婚/先孕后婚: 流年引动子女星同时合动配偶星或婚姻宫.
4. 多子/子女数量: 须看子女星是否成局、时柱是否多根, 勿默认选「育二子」等中间项.
5. 选项含多个年份时, 须逐段核对婚恋与生育顺序是否与大运流年一致.
""".strip()

_CHILDREN_SUBTHEME_GUIDES = {
    "children-birth-year": CHILDREN_BIRTH_YEAR_GUIDE,
    "children-dayun-span": CHILDREN_DAYUN_SPAN_GUIDE,
    "children-status": CHILDREN_STATUS_GUIDE,
}


def get_children_subtheme_guide(subtheme: str | None) -> str:
    if subtheme and subtheme in _CHILDREN_SUBTHEME_GUIDES:
        return _CHILDREN_SUBTHEME_GUIDES[subtheme]
    return ZINV_REASONING_GUIDE


ZINV_YINGQI_MANDATORY_GUIDE = """
子女应期题(出生年份/生育年份):
- 须提取每个选项中的公历年份, 分别定位大运与流年, 核对是否引动子女星(男官杀/女食伤)或子女宫(时柱).
- 勿把男命食伤年或女命官杀年当作主生育年; 勿跳过选项年份只凭原局猜.
- 若上文有【子女选项规则分】, 须与排盘互证, 不得单凭分数作答.
""".strip()

ZINV_YINGQI_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【子女星】
写明性别、子女星(男官杀/女食伤)与子女宫(时柱)在命局中的位置; 出生年份题须明确所用十神.

【选项年份】
逐条写出各选项涉及的公历年份、所在大运、流年干支及对子女星/子女宫的作用.

【选项排除】
A: 符合/不符合 - 一句理由(须引用选项年份与子女星, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项与子女引动最贴合.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

ZINV_DAYUN_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【运限子女】
先读虚龄大运锚点, 写出本题实际大运区间; 原局子女星、时柱、妻星/夫星与在该运内的总体趋势.

【选项排除】
A: 符合/不符合 - 一句理由(须引用运限与子女叙事, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项最贴合该运子女状况.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

ZINV_STATUS_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【命局婚子】
配偶星、子女星、时柱及当前大运对婚恋与生育的总体倾向(各一句, 引用排盘).

【选项排除】
A: 符合/不符合 - 一句理由(须引用十神或选项年份, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明哪一选项最贴合.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

LIUNIAN_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【置信】
写明判盘链 confidenceBand (strong/medium/weak) 与是否存在 conflicts; 若非 strong 或有冲突, 不得断言式排除, 至少保留 2 项待选.

【目标年】
写出题干目标公历年、所在大运、流年干支、天干十神、关键冲合(来自上文排盘).

【选项排除】
A: 符合/不符合 - 一句理由(须引用十神或冲合, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明为何剩余一项最贴合; 若两项仍接近, 写明差在哪及如何取舍.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()

CONSERVATIVE_ANSWER_GUIDE = """
保守作答约束:
- 判盘链 confidenceBand 非 strong, 或存在 conflicts 时: 禁止把任一选项判为「必然不符合/一定不对」; 选项排除须保留至少 2 项「待选/可能符合」.
- 仅当 confidenceBand=strong 且无 conflicts 时, 方可把 3 项标为不符合、唯一项标为符合.
- 不得用命例摘录或常识叙事推翻上文【穷通宝鉴调候】【滴天髓气势】【流年岁运规则】.
- 用神/调候题须先核对上文用神提示与透干, 再对照选项.
""".strip()

YINGQI_MANDATORY_GUIDE = """
应期题作答要点(流年/虚龄/大运):
- 先读【虚龄大运锚点】与「流年时间轴」, 定目标公历年、所在大运、流年干支与十神.
- 题干若给虚龄区间或大运干支, 不得换算到其它大运; 须在该运内叠流年再对选项.
- 以结构化排盘与岁运规则为主, 命例摘录仅作弱参考, 不得覆盖排盘表.
""".strip()

YINGQI_REASONING_FORMAT = """
请严格按下列格式作答(不要增删标题):

【目标年】
写出题干目标公历年(或虚龄换算结果)、所在大运干支、流年干支、天干十神、关键冲合(来自上文排盘).

【选项排除】
A: 符合/不符合 - 一句理由(须引用十神或冲合, 勿空泛)
B: 符合/不符合 - 一句理由
C: 符合/不符合 - 一句理由
D: 符合/不符合 - 一句理由

【结论】
说明为何剩余一项最贴合; 若两项仍接近, 写明差在哪及如何取舍.

答案: X
(最后一行必须是「答案:」加一个字母 A/B/C/D, 不要在此行后追加其他内容)
""".strip()


def _format_options(options: list[str]) -> str:
    lines: list[str] = []
    for opt in options:
        letter = opt.strip()[:1].upper() if opt.strip() else "?"
        lines.append(f"{letter}. {opt}")
    return "\n".join(lines)


def _format_fewshot(examples: list[dict[str, Any]]) -> str:
    if not examples:
        return ""
    blocks: list[str] = ["参考范例(仅供推理方法, 勿照搬结论):"]
    for idx, ex in enumerate(examples, start=1):
        blocks.append(
            f"范例{idx}: 问: {ex.get('question', '')}\n"
            f"选: {ex.get('answer', '')} ({ex.get('answer_text', '')})"
        )
    return "\n".join(blocks)


def load_fewshot_examples(path: Path | None = None) -> list[dict[str, Any]]:
    p = path or DEFAULT_FEWSHOT_PATH
    if not p.is_file():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return list(data.get("examples") or [])


def _filter_fewshot(
    examples: list[dict[str, Any]],
    *,
    exclude_question_id: str | None,
    max_items: int,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ex in examples:
        if exclude_question_id and ex.get("question_id") == exclude_question_id:
            continue
        out.append(ex)
        if len(out) >= max_items:
            break
    return out


def _format_judgement_block(judgement: dict[str, Any] | None) -> str:
    if not judgement:
        return ""
    opinions = (judgement.get("arbitration") or {}).get("judgeOpinions") or []
    if not opinions:
        return ""
    lines: list[str] = []
    ordered_roles = (
        "month",
        "tiaohou",
        "geju",
        "qishi",
        "shishen",
        "base",
        "suiyun",
        "interactions",
        "comprehensive",
    )
    opinion_map = {
        str(row.get("role") or ""): row
        for row in opinions
        if row.get("role") != "case"
    }
    for role in ordered_roles:
        row = opinion_map.get(role)
        if not row:
            continue
        classic = row.get("classic", "")
        summary = row.get("summary", "")
        boundary = row.get("boundary", "")
        rule_ids = row.get("ruleIds") or []
        line = f"- {role}/{classic}: {summary}"
        if rule_ids:
            line += f" [ruleIds={','.join(rule_ids[:6])}]"
        if boundary:
            line += f" (边界: {boundary})"
        lines.append(line)
    if not lines:
        return ""
    return (
        "\n\n经典判盘链预结论(须与选项互证, 命例不得越权覆盖主裁典籍):\n"
        + "\n".join(lines)
    )


def _build_confidence_guard_block(judgement: dict[str, Any] | None) -> str:
    if not judgement:
        return ""
    arb = judgement.get("arbitration") or {}
    band = str(arb.get("confidenceBand") or "medium")
    conflicts = list(arb.get("conflicts") or [])
    lines = [
        f"【判盘链置信】band={band}",
    ]
    if conflicts:
        lines.append("冲突点:")
        for item in conflicts[:4]:
            lines.append(f"- {item}")
    if band != "strong" or conflicts:
        lines.append(CONSERVATIVE_ANSWER_GUIDE)
    return "\n\n" + "\n".join(lines) if lines else ""


def build_contest_mcq_parts(
    chart: dict[str, Any],
    question: str,
    options: list[str],
    *,
    compressed: CompressedContext | None = None,
    rag_excerpts: list[dict[str, str]] | None = None,
    fewshot_examples: list[dict[str, Any]] | None = None,
    current_question_id: str | None = None,
    use_option_elimination: bool | None = None,
    judgement: dict[str, Any] | None = None,
    judgement_profile: str | None = None,
) -> tuple[str, str]:
    context = build_chart_context(
        chart,
        compressed=compressed,
        rag_excerpts=[],
    )
    dayun_lines: list[str] = []
    from app.core.knowledge.luck_chart import get_dayun_timeline

    for d in get_dayun_timeline(chart):
        dayun_lines.append(
            f"第{d.get('index')}运 {d.get('ganzhi')} "
            f"虚龄{d.get('startAge')}-{d.get('endAge')} "
            f"起运年{d.get('startYear')}"
        )
    dayun_block = "\n".join(dayun_lines) if dayun_lines else "(无大运列表)"
    fs_list = _filter_fewshot(
        list(fewshot_examples or []),
        exclude_question_id=current_question_id,
        max_items=4,
    )
    # 流年专用 few-shot 易与通用范例冲突, 默认仅用通用 few-shot
    fewshot = _format_fewshot(fs_list)
    fewshot_block = f"\n\n{fewshot}" if fewshot else ""
    is_event = is_liunian_event_question(question)
    if use_option_elimination is None:
        use_option_elimination = should_structured_mcq_reasoning(question, options)
    theme = infer_question_theme(question)
    full_judgement = (
        judgement_profile == "full"
        if judgement_profile is not None
        else uses_full_judgement_chain(question, options)
    )
    yingqi_mode = (
        judgement_profile == "yingqi"
        if judgement_profile is not None
        else is_yingqi_question(question, options)
    )
    static_xueli_mode = (
        theme == "学历"
        and not full_judgement
        and not yingqi_mode
        and not has_explicit_timing_signal(question, options)
    )
    xueli_yingqi_mode = (
        theme == "学历"
        and yingqi_mode
        and has_explicit_timing_signal(question, options)
    )
    static_jiating_mode = (
        theme == "家庭出身"
        and not full_judgement
        and not yingqi_mode
        and not has_explicit_timing_signal(question, options)
    )
    jiating_yingqi_mode = (
        theme == "家庭出身"
        and yingqi_mode
        and has_explicit_timing_signal(question, options)
    )
    zinv_yingqi_mode = (
        theme == "子女"
        and yingqi_mode
        and has_explicit_timing_signal(question, options)
    )
    career_subtheme = (
        infer_career_subtheme(question, options) if theme == "职业财运" else None
    )
    career_yingqi_mode = (
        theme == "职业财运"
        and yingqi_mode
        and (
            has_explicit_timing_signal(question, options)
            or is_year_option_mcq(options)
            or career_subtheme == "career-year-event"
        )
    )
    family_subtheme = (
        infer_family_subtheme(question, options) if theme == "家庭出身" else None
    )
    children_subtheme = (
        infer_children_subtheme(question, options) if theme == "子女" else None
    )
    health_subtheme = (
        infer_health_subtheme(question, options) if theme == "健康疾病" else None
    )
    static_light_theme_mode = static_xueli_mode or static_jiating_mode
    tiaohou_block = build_tiaohou_prompt_block(
        chart,
        judgement=judgement if full_judgement else None,
        compressed=compressed,
    )
    tiaohou_note = f"\n\n{tiaohou_block}" if tiaohou_block and full_judgement else ""
    qishi_block = build_qishi_prompt_block(
        chart, judgement=judgement if full_judgement else None
    )
    qishi_note = f"\n\n{qishi_block}" if qishi_block and full_judgement else ""
    liunian_block = build_liunian_prompt_block(
        chart,
        question,
        compressed,
        options=options,
        judgement=judgement if full_judgement else None,
        force=bool(
            yingqi_mode
            or (use_option_elimination and not static_light_theme_mode)
            or (
                full_judgement
                and has_explicit_timing_signal(question, options)
            )
            or (
                full_judgement
                and theme == "健康疾病"
                and health_subtheme
                in ("health-year-event", "health-dayun-span", "health-status")
                and (
                    has_explicit_timing_signal(question, options)
                    or health_subtheme == "health-dayun-span"
                )
            )
            or (
                theme == "职业财运"
                and career_subtheme in ("career-year-event", "wealth")
                and (
                    has_explicit_timing_signal(question, options)
                    or is_year_option_mcq(options)
                )
            )
        ),
    )
    liunian_note = f"\n\n{liunian_block}" if liunian_block else ""
    exclusion_block = ""
    if use_option_elimination:
        excl = build_option_exclusion_block(chart, question, options)
        if excl:
            exclusion_block = f"\n\n{excl}"
    year_score_block = ""
    if use_option_elimination and theme == "家庭出身":
        fb = build_family_option_score_block(
            chart, question, options, subtheme=family_subtheme
        )
        if fb:
            year_score_block = f"\n\n{fb}"
    elif use_option_elimination and theme == "子女":
        cb = build_children_option_score_block(
            chart, question, options, subtheme=children_subtheme
        )
        if cb:
            year_score_block = f"\n\n{cb}"
    elif use_option_elimination and is_year_option_mcq(options):
        ys = build_year_option_score_block(chart, question, options)
        if ys:
            year_score_block = f"\n\n{ys}"
    health_years_block = ""
    if use_option_elimination and theme == "健康疾病" and health_subtheme in (
        "health-year-event",
        "health-status",
    ):
        hb = build_health_option_years_anchor(chart, question, options)
        if hb:
            health_years_block = f"\n\n{hb}"
    theme_guide = ""
    if theme == "婚姻感情":
        theme_guide = f"\n\n{MARRIAGE_REASONING_GUIDE}"
    elif theme == "健康疾病":
        theme_guide = (
            f"\n\n{get_health_subtheme_guide(health_subtheme)}"
            f"\n\n{HEALTH_MANDATORY_GUIDE}"
        )
    elif theme == "官非":
        theme_guide = f"\n\n{GUANFEI_REASONING_GUIDE}"
    elif theme == "学历":
        theme_guide = f"\n\n{XUELI_REASONING_GUIDE}"
    elif theme == "职业财运":
        theme_guide = f"\n\n{get_career_subtheme_guide(career_subtheme)}"
    elif theme in ("家庭出身",):
        theme_guide = f"\n\n{get_family_subtheme_guide(family_subtheme)}"
    elif theme in ("子女",):
        theme_guide = f"\n\n{get_children_subtheme_guide(children_subtheme)}"
    event_guide = (
        f"\n\n{LIUNIAN_EVENT_GUIDE}"
        if is_event
        or (
            yingqi_mode
            and not xueli_yingqi_mode
            and not jiating_yingqi_mode
            and not zinv_yingqi_mode
        )
        else ""
    )
    if xueli_yingqi_mode and use_option_elimination:
        elimination_guide = f"\n\n{XUELI_YINGQI_REASONING_FORMAT}"
    elif jiating_yingqi_mode and use_option_elimination:
        elimination_guide = f"\n\n{JIATING_YINGQI_REASONING_FORMAT}"
    elif zinv_yingqi_mode and use_option_elimination:
        if children_subtheme == "children-dayun-span":
            elimination_guide = f"\n\n{ZINV_DAYUN_REASONING_FORMAT}"
        elif children_subtheme == "children-status":
            elimination_guide = f"\n\n{ZINV_STATUS_REASONING_FORMAT}"
        else:
            elimination_guide = f"\n\n{ZINV_YINGQI_REASONING_FORMAT}"
    elif career_yingqi_mode and use_option_elimination:
        if career_subtheme == "wealth":
            elimination_guide = f"\n\n{CAREER_WEALTH_YEAR_REASONING_FORMAT}"
        else:
            elimination_guide = f"\n\n{CAREER_YEAR_EVENT_REASONING_FORMAT}"
    elif theme == "职业财运" and use_option_elimination:
        if career_subtheme == "major-industry":
            elimination_guide = f"\n\n{CAREER_MAJOR_REASONING_FORMAT}"
        elif career_subtheme == "wealth":
            if is_year_option_mcq(options):
                elimination_guide = f"\n\n{CAREER_WEALTH_YEAR_REASONING_FORMAT}"
            else:
                elimination_guide = f"\n\n{CAREER_WEALTH_REASONING_FORMAT}"
        elif career_subtheme == "career-year-event":
            elimination_guide = f"\n\n{CAREER_YEAR_EVENT_REASONING_FORMAT}"
        else:
            elimination_guide = f"\n\n{CAREER_STATUS_REASONING_FORMAT}"
    elif full_judgement and theme == "健康疾病" and use_option_elimination:
        if health_subtheme == "health-year-event":
            elimination_guide = f"\n\n{HEALTH_YEAR_REASONING_FORMAT}"
        elif health_subtheme == "health-dayun-span":
            elimination_guide = f"\n\n{HEALTH_DAYUN_REASONING_FORMAT}"
        elif health_subtheme == "health-diagnosis":
            elimination_guide = f"\n\n{HEALTH_DIAGNOSIS_REASONING_FORMAT}"
        else:
            elimination_guide = f"\n\n{HEALTH_STATUS_REASONING_FORMAT}"
    elif yingqi_mode and use_option_elimination:
        elimination_guide = f"\n\n{YINGQI_REASONING_FORMAT}"
    elif static_xueli_mode and use_option_elimination:
        elimination_guide = f"\n\n{STATIC_XUELI_REASONING_FORMAT}"
    elif static_jiating_mode and use_option_elimination:
        elimination_guide = f"\n\n{STATIC_JIATING_REASONING_FORMAT}"
    elif use_option_elimination:
        elimination_guide = f"\n\n{LIUNIAN_REASONING_FORMAT}"
    else:
        elimination_guide = ""
    judgement_note = _format_judgement_block(judgement) if full_judgement else ""
    confidence_guard = (
        _build_confidence_guard_block(judgement) if full_judgement else ""
    )
    mandatory_guide = (
        JUDGEMENT_MANDATORY_GUIDE
        if full_judgement
        else STATIC_XUELI_MANDATORY_GUIDE
        if static_xueli_mode
        else STATIC_JIATING_MANDATORY_GUIDE
        if static_jiating_mode
        else XUELI_YINGQI_MANDATORY_GUIDE
        if xueli_yingqi_mode
        else JIATING_YINGQI_MANDATORY_GUIDE
        if jiating_yingqi_mode
        else ZINV_YINGQI_MANDATORY_GUIDE
        if zinv_yingqi_mode
        else CAREER_YINGQI_MANDATORY_GUIDE
        if career_yingqi_mode
        else CAREER_STATUS_MANDATORY_GUIDE
        if theme == "职业财运" and career_subtheme == "career-status"
        else YINGQI_MANDATORY_GUIDE
        if yingqi_mode
        else ""
    )
    case_excerpt_limit = 5 if full_judgement else 0
    if rag_excerpts and case_excerpt_limit > 0:
        case_note = (
            "\n\n命例讲解摘录(来自知识库RAG, 可参考同类命盘断法, 勿与当前命主混为一谈):\n"
            f"{_format_excerpts(rag_excerpts[:case_excerpt_limit])}"
        )
    else:
        case_note = ""
    primary_count = len(
        ((judgement or {}).get("tieredEvidence") or {}).get("primaryEvidence") or []
    )
    no_primary_note = ""
    if full_judgement and judgement is not None and primary_count == 0:
        no_primary_note = (
            "\n\n[置信约束] 当前命盘无主裁典籍锚点, 作答须保守, "
            "优先排除与调候/格局/岁运/气势段落矛盾的选项."
        )
    system = (
        f"{context}\n\n"
        f"大运序列:\n{dayun_block}\n\n"
        f"{CONTEST_REASONING_GUIDE}"
        f"\n\n{mandatory_guide}"
        f"{tiaohou_note}"
        f"{qishi_note}"
        f"{theme_guide}"
        f"{event_guide}"
        f"{elimination_guide}"
        f"{judgement_note}"
        f"{confidence_guard}"
        f"{no_primary_note}"
        f"{liunian_note}"
        f"{exclusion_block}"
        f"{year_score_block}"
        f"{health_years_block}"
        f"{fewshot_block}"
        f"{case_note}"
    )
    if use_option_elimination:
        if static_xueli_mode:
            format_hint = (
                "须按格式完成【印星学业】【层级排除】【结论】; "
                "勿因见印就断大学以上. 最后一行写「答案:」+ 一个字母."
            )
        elif xueli_yingqi_mode:
            format_hint = (
                "须按格式完成【选项年份】【选项排除】【结论】; "
                "逐选项核对升学/毕业年份与大运流年, 勿当静态层级题. "
                "最后一行写「答案:」+ 一个字母."
            )
        elif static_jiating_mode:
            if family_subtheme == "family-wealth-tier":
                format_hint = (
                    "须按格式完成【父母家运】【选项排除】【结论】; "
                    "贫富层级题看年柱父星财库, 身弱仍可富贵出身; "
                    "若有【家庭出身选项规则分】须互证. 最后一行写「答案:」+ 一个字母."
                )
            else:
                format_hint = (
                    "须按格式完成【父母家运】【选项排除】【结论】; "
                    "父母关系/状况题须引用父母星. 最后一行写「答案:」+ 一个字母."
                )
        elif jiating_yingqi_mode:
            if family_subtheme == "family-death-mother":
                format_hint = (
                    "须先写【父母星】, 再按格式完成【选项年份】【选项排除】【结论】; "
                    "丧母题只论印星冲合, 助印之年通常非丧母. 最后一行写「答案:」+ 一个字母."
                )
            else:
                format_hint = (
                    "须先写【父母星】, 再按格式完成【选项年份】【选项排除】【结论】; "
                    "丧父题只论偏财冲合. 最后一行写「答案:」+ 一个字母."
                )
        elif zinv_yingqi_mode:
            if children_subtheme == "children-dayun-span":
                format_hint = (
                    "须按格式完成【运限子女】【选项排除】【结论】; "
                    "大运名称与虚龄不符时以锚点为准. 最后一行写「答案:」+ 一个字母."
                )
            elif children_subtheme == "children-status":
                format_hint = (
                    "须按格式完成【命局婚子】【选项排除】【结论】; "
                    "男官杀女食伤. 最后一行写「答案:」+ 一个字母."
                )
            else:
                format_hint = (
                    "须先写【子女星】, 再按格式完成【选项年份】【选项排除】【结论】; "
                    "男命看官杀、女命看食伤. 最后一行写「答案:」+ 一个字母."
                )
        elif career_yingqi_mode:
            if career_subtheme == "wealth":
                format_hint = (
                    "须先写【财星体用】, 再按格式完成【选项年份】【选项排除】【结论】; "
                    "财旺不等于发财, 须看任财能力. 最后一行写「答案:」+ 一个字母."
                )
            else:
                format_hint = (
                    "须按格式完成【目标年/运限】【选项排除】【结论】; "
                    "逐选项核对大运流年与官杀财食伤引动. 最后一行写「答案:」+ 一个字母."
                )
        elif theme == "职业财运":
            if career_subtheme == "major-industry":
                format_hint = (
                    "须按格式完成【五行科系】【选项排除】【结论】; "
                    "同一五行多个行业须逐项对照. 最后一行写「答案:」+ 一个字母."
                )
            elif career_subtheme == "wealth":
                if is_year_option_mcq(options):
                    format_hint = (
                        "须先写【财星体用】, 再按格式完成【选项年份】【选项排除】【结论】; "
                        "财旺不等于发财. 最后一行写「答案:」+ 一个字母."
                    )
                else:
                    format_hint = (
                        "须按格式完成【财星体用】【选项排除】【结论】; "
                        "须看日主能否任财, 勿见财就断发财. 最后一行写「答案:」+ 一个字母."
                    )
            elif career_subtheme == "career-year-event":
                format_hint = (
                    "须按格式完成【目标年/运限】【选项排除】【结论】; "
                    "须先读虚龄大运锚点. 最后一行写「答案:」+ 一个字母."
                )
            else:
                format_hint = (
                    "须按格式完成【选项对照】【结论】; "
                    "先读各选项字面职业/行业, 禁止仅因七杀/食伤透干就选公务员/律师/手艺. "
                    "最后一行写「答案:」+ 一个字母."
                )
        elif full_judgement and theme == "婚姻感情":
            format_hint = (
                "须先读判盘链与【虚龄大运锚点】(若有), 再按格式完成【置信】【目标年】【选项排除】【结论】; "
                "男看财、女看官杀为配偶星; confidence 非 strong 时至少保留 2 项待选. "
                "最后一行写「答案:」+ 一个字母."
            )
        elif full_judgement and theme == "健康疾病":
            if health_subtheme == "health-year-event":
                format_hint = (
                    "须先读判盘链、【虚龄大运锚点】与【健康选项年份锚点】(若有), "
                    "再按格式完成【置信】【病灾象】【选项年份】【选项排除】【结论】; "
                    "confidence 非 strong 时至少保留 2 项待选. 最后一行写「答案:」+ 单字母."
                )
            elif health_subtheme == "health-dayun-span":
                format_hint = (
                    "须先读【虚龄大运锚点】与流年块, 再按格式完成【置信】【运限病象】【选项对照】【结论】; "
                    "confidence 非 strong 时至少保留 2 项待选. 最后一行写「答案:」+ 单字母."
                )
            elif health_subtheme == "health-diagnosis":
                format_hint = (
                    "须先读判盘链与目标年流年(若有), 再按格式完成【置信】【五行脏腑】【选项排除】【结论】; "
                    "须对照选项字面病名/器官. 最后一行写「答案:」+ 单字母."
                )
            else:
                format_hint = (
                    "须先读判盘链与流年块(若有目标年), 再按格式完成【置信】【选项对照】【结论】; "
                    "先读各选项字面症状, 禁止仅因七杀就选最重项. "
                    "confidence 非 strong 时至少保留 2 项待选. 最后一行写「答案:」+ 单字母."
                )
        else:
            format_hint = (
                "须先读【规则预排除】, 再按格式完成【目标年】【选项排除】【结论】; "
                "若推翻预排除须写明依据. 最后一行写「答案:」+ 一个字母."
            )
        user = (
            f"命理师大赛四选一, 须先推理再作答.\n"
            f"题目: {question}\n"
            f"选项:\n{_format_options(options)}\n\n"
            f"{format_hint}"
        )
    else:
        extra_hints: list[str] = []
        if tiaohou_block:
            extra_hints.append("调候题须优先依据上文【穷通宝鉴调候】段取舍, 勿凭常识猜选")
        if qishi_block:
            extra_hints.append("气势题须优先依据上文【滴天髓气势】段取舍")
        if judgement_note:
            extra_hints.append("须与经典判盘链预结论互证, 命例不得越权")
        if confidence_guard and "保守作答" in confidence_guard:
            extra_hints.append("置信非strong或有冲突时须保守作答, 勿断言式排除")
        if is_event:
            extra_hints.append("流年题须依据上文大运流年与冲合十神, 勿凭常识猜选")
        hint_suffix = ""
        if extra_hints:
            hint_suffix = "\n" + "; ".join(extra_hints)
        user = (
            f"请回答以下命理师大赛四选一题目.\n"
            f"题目: {question}\n"
            f"选项:\n{_format_options(options)}\n\n"
            f"要求: 只输出一个大写字母 A/B/C/D (若选项为小写 a/b/c/d 则输出对应小写), "
            f"不要输出解释、标点或其他文字.{hint_suffix}"
        )
    return system, user


def _ziwei_palace_lines(palaces: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for palace in palaces[:12]:
        major = "、".join(s.get("name", "") for s in palace.get("majorStars") or [])
        minor = "、".join(s.get("name", "") for s in (palace.get("minorStars") or [])[:4])
        lines.append(
            f"{palace.get('name', '')} {palace.get('stemBranch', '')} "
            f"主星:{major or '无'} 辅星:{minor or '无'} "
            f"大限:{palace.get('decadalRange', '')}"
        )
    return "\n".join(lines) or "(无宫位)"


ZIWEI_CONTEST_GUIDE = """
紫微斗数大赛四选一要点:
1. 先看命宫、身宫、三方四正主星与亮度, 定体性.
2. 问婚姻看夫妻宫, 问事业看官禄宫, 问财看财帛, 问健康看疾厄, 问子女看子女宫.
3. 题干若含公历年份, 须结合该年流年/大限/小限飞宫与四化.
4. 四选一选与盘象及流年最贴合的一项, 勿凭常识臆测.
""".strip()


def build_contest_ziwei_mcq_parts(
    ziwei_chart: dict[str, Any],
    question: str,
    options: list[str],
    *,
    rag_excerpts: list[dict[str, str]] | None = None,
    judgement: dict[str, Any] | None = None,
) -> tuple[str, str]:
    meta = ziwei_chart.get("meta") or {}
    limits = ziwei_chart.get("limits") or {}
    excerpt_block = _format_excerpts(rag_excerpts or [])
    judgement_block = _format_ziwei_judgement_block(judgement)
    guard = (
        "约束: 须依据裁判链与典籍摘录作答, 不得编造宫星; "
        "不得用命例或现代讲义推翻主裁证据; 证据不足时选最接近边界者.\n"
    )
    system = (
        f"{guard}"
        f"你是紫微斗数专家, 按南派三合盘断四选一.\n"
        f"{ZIWEI_CONTEST_GUIDE}\n\n"
        f"真太阳时: {ziwei_chart.get('trueSolarTime', '')}\n"
        f"四柱: {ziwei_chart.get('fourPillars', {})}\n"
        f"局数: {meta.get('bureau', '')} 命主:{meta.get('soul', '')} "
        f"身主:{meta.get('body', '')} 生肖:{meta.get('zodiac', '')}\n"
        f"十二宫:\n{_ziwei_palace_lines(ziwei_chart.get('palaces') or [])}\n\n"
        f"大限序列: {limits.get('decadal', [])}\n"
        f"流年: {limits.get('yearly', {})}\n"
        f"当前大限/小限: {limits.get('current', {})}\n\n"
        f"裁判链:\n{judgement_block}\n\n"
        f"紫微典籍摘录:\n{excerpt_block}"
    )
    user = (
        f"命理师大赛四选一, 问事: {question}\n"
        f"选项:\n{_format_options(options)}\n\n"
        f"要求: 只输出一个大写字母 A/B/C/D (小写选项则输出 a/b/c/d), 不要解释."
    )
    return system, user


def build_contest_liuyao_mcq_parts(
    liuyao_chart: dict[str, Any],
    yong_shen: dict[str, Any],
    question: str,
    options: list[str],
    *,
    rag_excerpts: list[dict[str, str]] | None = None,
    judgement: dict[str, Any] | None = None,
) -> tuple[str, str]:
    ben = liuyao_chart.get("benGua", {}) or {}
    lines = liuyao_chart.get("lines", []) or []
    line_text = "\n".join(
        f"第{item.get('position')}爻 {item.get('stem', '')}{item.get('branch', '')} "
        f"{item.get('liuqin', '')} {item.get('liushen', '')}"
        f"{' 世' if item.get('isShi') else ''}"
        f"{' 应' if item.get('isYing') else ''}"
        f"{' 动' if item.get('isMoving') else ''}"
        for item in lines
    )
    excerpt_block = _format_excerpts(rag_excerpts or [])
    judgement_block = _format_liuyao_judgement_block(judgement)
    guard = (
        "约束: 须依据裁判链与典籍摘录作答, 不得编造爻位; "
        "不得用现代讲义推翻主裁证据; 证据不足时选最接近边界者.\n"
    )
    system = (
        f"{guard}"
        f"你是六爻纳甲专家, 按《增删卜易》思路占断四选一, 结合裁判链、月建日辰、世应、动爻生克.\n"
        f"起卦: {liuyao_chart.get('meta', {}).get('castNote', '')}\n"
        f"本卦: {ben.get('name', '')} 变卦: {(liuyao_chart.get('bianGua') or {}).get('name', '无')}\n"
        f"动爻: {liuyao_chart.get('movingLines', [])}\n"
        f"月建: {liuyao_chart.get('monthJian', '')} 日辰: {liuyao_chart.get('dayChen', '')}\n"
        f"用神: {yong_shen.get('yongShen', '')} (第{yong_shen.get('position', '')}爻, "
        f"来源{yong_shen.get('source', 'rule')})\n"
        f"六爻:\n{line_text}\n\n"
        f"裁判链:\n{judgement_block}\n\n"
        f"六爻典籍摘录:\n{excerpt_block}"
    )
    user = (
        f"命理师大赛四选一, 问事: {question}\n"
        f"选项:\n{_format_options(options)}\n\n"
        f"要求: 只输出一个大写字母 A/B/C/D (小写选项则输出 a/b/c/d), 不要解释."
    )
    return system, user


def _format_ziwei_judgement_block(judgement: dict[str, Any] | None) -> str:
    if not judgement:
        return "(暂无裁判链)"
    rows: list[str] = []
    topic = judgement.get("topic") or {}
    if topic.get("topicLabel"):
        palaces = topic.get("targetPalaces") or []
        rows.append(
            f"- [占事] {topic.get('topicLabel')}"
            + (f" / 主题宫 {'、'.join(palaces)}" if palaces else "")
        )
    for judge in judgement.get("judges") or []:
        role = judge.get("role", "")
        summary = judge.get("summary", "")
        rows.append(f"- [{role}] {summary}")
    arbitration = judgement.get("arbitration") or {}
    if arbitration.get("summary"):
        rows.append(f"- [仲裁] {arbitration.get('summary')}")
    if arbitration.get("conflicts"):
        rows.append(f"- [冲突] {'; '.join(arbitration.get('conflicts') or [])}")
    tiered_summary = judgement.get("tieredEvidenceSummary") or {}
    if tiered_summary.get("note"):
        rows.append(f"- [证据] {tiered_summary.get('note')}")
    return "\n".join(rows) or "(暂无裁判链)"


def _format_liuyao_judgement_block(judgement: dict[str, Any] | None) -> str:
    if not judgement:
        return "(暂无裁判链)"
    rows: list[str] = []
    for judge in judgement.get("judges") or []:
        role = judge.get("role", "")
        summary = judge.get("summary", "")
        rows.append(f"- [{role}] {summary}")
    arbitration = judgement.get("arbitration") or {}
    if arbitration.get("summary"):
        rows.append(f"- [仲裁] {arbitration.get('summary')}")
    if arbitration.get("conflicts"):
        rows.append(f"- [冲突] {'; '.join(arbitration.get('conflicts') or [])}")
    tiered_summary = judgement.get("tieredEvidenceSummary") or {}
    if tiered_summary.get("note"):
        rows.append(f"- [证据] {tiered_summary.get('note')}")
    return "\n".join(rows) or "(暂无裁判链)"


def build_bazi_ziwei_arbitrate_parts(
    question: str,
    options: list[str],
    bazi_letter: str,
    ziwei_letter: str,
    *,
    bazi_note: str = "",
    ziwei_note: str = "",
) -> tuple[str, str]:
    system = (
        "你是命理师大赛仲裁员. 八字与紫微两通道对同一四选一给出不同字母时, "
        "须结合题干与选项, 判断哪一通道更符合题意, 只输出最终字母."
    )
    user = (
        f"题目: {question}\n"
        f"选项:\n{_format_options(options)}\n\n"
        f"八字通道答案: {bazi_letter or '无'}\n"
        f"八字要点: {(bazi_note or '(无)')[:400]}\n\n"
        f"紫微通道答案: {ziwei_letter or '无'}\n"
        f"紫微要点: {(ziwei_note or '(无)')[:400]}\n\n"
        f"要求: 只输出一个大写字母 A/B/C/D, 不要解释."
    )
    return system, user


def build_contest_mcq_prompt(
    chart: dict[str, Any],
    question: str,
    options: list[str],
    *,
    compressed: CompressedContext | None = None,
    rag_excerpts: list[dict[str, str]] | None = None,
    fewshot_examples: list[dict[str, Any]] | None = None,
) -> str:
    system, user = build_contest_mcq_parts(
        chart,
        question,
        options,
        compressed=compressed,
        rag_excerpts=rag_excerpts,
        fewshot_examples=fewshot_examples,
    )
    return f"{system}\n\n{user}"

## ADDED Requirements

### Requirement: 按题型分流的 MCQ 通道路由

大赛基准评测 MUST 在调用 LLM 之前, 将每道 MCQ 归入且仅归入一种 prompt 通道: `full`、`yingqi`、`static-light` 或 `other`。其中 `static-light` 与 `yingqi` 在学历、家庭出身题型上 MAY 进一步使用题型专用 prompt 变体 (见「静态题型专用 prompt 指南」).

#### Scenario: 婚姻或健康题使用 full 通道

- **WHEN** `infer_question_theme(question)` 为婚姻感情或健康疾病
- **THEN** 系统运行 `BaziJudgementChain`, 启用命例 RAG, 并向 prompt 注入判盘预结论与保守作答约束

#### Scenario: 无应期信号的学历或家庭出身使用 static-light 通道

- **WHEN** 题型为学历或家庭出身, 且 `has_explicit_timing_signal(question, options)` 为 false
- **THEN** 系统跳过判盘链与命例 RAG, 不注入完整流年时间轴块, 启用该题型轻量结构化推理格式, 并要求最后一行输出 `答案:` + 单字母

#### Scenario: 无应期信号的子女题使用 static-light 通道

- **WHEN** 题型为子女, 且 `has_explicit_timing_signal(question, options)` 为 false
- **THEN** 系统跳过判盘链与命例 RAG, 关闭结构化 elimination 推理, 不 force 完整流年块, 要求模型输出单字母 MCQ 答案

#### Scenario: 应期题使用 yingqi 通道

- **WHEN** 题型不是婚姻感情/健康疾病, 且 (`has_explicit_timing_signal(question, options)` 为 true 或题型为流年事件), 且不属于「学历/家庭出身 + 选项含年份」的题型专用 yingqi 变体所单独覆盖的路径
- **THEN** 系统跳过全量判盘链与命例 RAG, 注入虚龄/大运锚点与通用应期推理格式, 且不施加保守约束

#### Scenario: 学历选项含年份时使用学历应期变体

- **WHEN** 题型为学历, 且 `has_explicit_timing_signal(question, options)` 为 true (含选项内多个公历年份)
- **THEN** 系统走 yingqi 通道, 使用学历应期 mandatory 与「选项年份」推理格式, 并 MAY 注入选项年份岁运评分块

#### Scenario: 家庭出身选项含年份时使用家庭应期变体

- **WHEN** 题型为家庭出身, 且 `has_explicit_timing_signal(question, options)` 为 true
- **THEN** 系统走 yingqi 通道, 使用家庭应期 mandatory 与「选项年份 + 父母星」推理格式, 并 MAY 注入家庭出身选项规则分块

### Requirement: 虚龄大运锚点

题干涉及虚龄区间和/或具名大运 (如甲戌大运) 时, prompt MUST 包含基于命盘时间轴计算出的锚点, 映射到结构化大运行。

#### Scenario: 虚龄区间且大运干支在盘中存在

- **WHEN** 题干含虚龄区间, 且大运干支标签存在于 chart 时间轴中
- **THEN** prompt 在 LLM 推理前包含匹配大运的序号、干支、虚龄区间与公历年份区间

#### Scenario: 盘中找不到题干所指大运

- **WHEN** 题干具名大运未出现在 chart 时间轴中
- **THEN** 锚点块明确说明未匹配, 并指示模型对照完整大运序列核对

### Requirement: 分阶段题型准确率门禁

各题型提升 MUST 分阶段验收, 每阶段有明确准确率门禁; 未通过门禁不得要求合并前必须跑完全量 200 题 (最终阶段除外)。

#### Scenario: P0 静态题型门禁

- **WHEN** P0 静态题型任务全部完成
- **THEN** 静态子集评测 (不少于 20 题) 报告学历+家庭出身+子女合计准确率 >= 40%

#### Scenario: P1 应期题型门禁

- **WHEN** P1 应期题型任务全部完成
- **THEN** 流年事件子集 (19 题) 准确率 >= 52%

#### Scenario: P3 职业财运门禁

- **WHEN** P3 职业财运 prompt 任务完成 (5.1-5.1e)
- **THEN** 职业财运子集 (38 题) 准确率 >= 14/32 (约 43.8%); 当前 p2 基线 **18/38 (47.4%)** 已通过

#### Scenario: P3 职业+性格合计门禁 (待完成)

- **WHEN** P3 全部任务 (含 5.2 RAG top_k 与 5.3 联合子集) 完成
- **THEN** 职业财运 + 性格外貌子集合计准确率 >= 18/47

#### Scenario: 全量 200 题门禁

- **WHEN** P0-P4 全部任务完成
- **THEN** 连续两次全量 200 题评测准确率均 >= 69/200 (34.5%)

### Requirement: 题型子集评测

后端 MUST 提供脚本或命令行参数, 在不修改数据集文件的前提下, 按题型列表和/或 question_id 列表过滤 Contest8 MCQ 并评测。

#### Scenario: 运行单一题型子集

- **WHEN** 操作者指定题型列表 (如 `学历,家庭出身`) 运行子集评测
- **THEN** 系统仅评测匹配题型的题目, 并输出含 `correct`/`total`/`accuracy` 与 `questionIds` 的 JSON

#### Scenario: 按 question_id 过滤子集

- **WHEN** 操作者指定 `--ids P018-Q6,P027-Q11` 等逗号分隔 ID
- **THEN** 系统仅评测数据集中存在的对应题目 (仍可与 `--themes` 组合过滤)

### Requirement: Val 集冒烟不退步

每个阶段完成后 MUST 评测 val 划分 (40 题); 相对上一阶段 val 基线不得退步超过 1 题, 除非有 documented 权衡批准。

#### Scenario: Val 冒烟通过

- **WHEN** 某阶段完成且 val 基线为 14/40
- **THEN** 新一轮 val 结果 >= 13/40

### Requirement: 静态题型专用 prompt 指南

系统 MUST 为 static-light 下的学历与家庭出身注入题型专用推理指南, 且不得使用婚姻/健康 full 通道的保守约束。

#### Scenario: 静态学历 prompt

- **WHEN** 学历题处于 static-light 通道
- **THEN** prompt 包含学历层级断法 (印星/财坏印/早运大运/同层级比较), 并使用「印星学业 + 层级排除」轻量格式, 而非完整「目标年 + 流年时间轴」模板

#### Scenario: 静态家庭出身 prompt

- **WHEN** 家庭出身题处于 static-light 通道
- **THEN** prompt 包含父母星与年月柱断法 (偏财为父、印为母、贫富贵判断), 并使用「父母家运 + 选项排除」轻量格式

### Requirement: 家庭出身子题型路由

`infer_question_theme == 家庭出身` 时, 系统 MUST 进一步路由至子题型, 并注入对应专用推理指南 (替代单一 `FAMILY_ORIGIN_REASONING_GUIDE`).

#### Scenario: 丧父应期子类

- **WHEN** 题干或选项表明父亲去世/丧父, 且选项含年份
- **THEN** 子类为 `family-death-father`, prompt 使用丧父专用指南与应期格式

#### Scenario: 丧母应期子类

- **WHEN** 题干或选项表明母亲离世/丧母, 且选项含年份
- **THEN** 子类为 `family-death-mother`, prompt 使用丧母专用指南与应期格式

#### Scenario: 贫富层级子类

- **WHEN** 题干或选项主要为贫/富/小康/孤儿等层级, 且无长叙事混合
- **THEN** 子类为 `family-wealth-tier`, prompt 使用贫富层级专用指南

#### Scenario: 家庭关系叙事子类

- **WHEN** 题干问父母关系/状况/背景, 或选项含职业叙事与贫富混合
- **THEN** 子类为 `family-relation`, prompt 使用关系叙事专用指南

### Requirement: 家庭出身选项规则分

家庭出身 structured MCQ 在启用 elimination 推理时 MUST 尝试注入 `【家庭出身选项规则分】` 提示块; 规则分仅供与排盘互证, 不得作为唯一作答依据.

#### Scenario: 家庭出身题优先规则分块

- **WHEN** 题型为家庭出身且启用 structured MCQ
- **THEN** 系统使用 `build_family_option_score_block` 替代通用 `build_year_option_score_block`

#### Scenario: 规则分提示不得强制选最高分

- **WHEN** 规则分块注入 prompt
- **THEN** 块内说明 MUST 明确规则分仅供参考, 不得单凭分数排除冲根/合去之年或强行选富贵层级

### Requirement: 题型关键词纠偏

`infer_question_theme` MUST 在通用关键词匹配前处理已知冲突, 避免题干同时含「毕业/大学」与职业取向词时被误判为学历。

#### Scenario: 毕业后行业归职业财运

- **WHEN** 题干含「行业」「从事」「科系」或「现职」之一
- **THEN** `infer_question_theme` 返回 `职业财运`, 即使题干同时含「毕业」或「大学」

#### Scenario: 身家年薪投资归职业财运

- **WHEN** 题干含「身家」「年薪」或「投资」之一
- **THEN** `infer_question_theme` 返回 `职业财运`

### Requirement: 选项年份识别

应期信号检测 MUST 将 MCQ 选项内、中文或英文逗号后的公历年份计入选项年份型 MCQ。

#### Scenario: 中文逗号前缀年份

- **WHEN** 某选项文本含 `，2004年` 或 `,2004年` 等形式
- **THEN** `is_year_option_mcq(options)` 将该选项计为含年份选项; 当含年份选项数 >= 2 时 `has_explicit_timing_signal` 为 true

### Requirement: 子女应期子题型路由

`infer_question_theme == 子女` 且存在应期信号时, 系统 MUST 进一步路由至子题型, 并注入对应专用推理指南.

#### Scenario: 子女出生年份子类

- **WHEN** 题干问哪年/何时生孩子, 或选项为纯公历年份
- **THEN** 子类为 `children-birth-year`, prompt 使用出生年份 mandatory 与「子女星 + 选项年份」格式

#### Scenario: 大运期间子女运子类

- **WHEN** 题干含虚龄区间/大运名称并问子女运
- **THEN** 子类为 `children-dayun-span`, prompt 使用运限子女格式; 大运名称与虚龄不一致时以锚点为准

#### Scenario: 婚恋子女状况子类

- **WHEN** 题干或选项含婚恋与子女数量/状况叙事
- **THEN** 子类为 `children-status`, prompt 使用命局婚子格式

### Requirement: 子女出生年选项规则分

子女 `children-birth-year` structured MCQ MUST 尝试注入 `【子女选项规则分】` 提示块; 男命以官杀、女命以食伤为主信号; 规则分仅供互证.

#### Scenario: 子女题优先子女规则分块

- **WHEN** 题型为子女且子类为 `children-birth-year` 且启用 structured MCQ
- **THEN** 系统使用 `build_children_option_score_block` 替代通用岁运评分块

#### Scenario: 规则分不得强制选最高分

- **WHEN** 子女规则分块注入 prompt
- **THEN** 块内 MUST 说明规则分仅供参考, 分差较小时不得单凭分数作答

### Requirement: 子女背景财运题纠偏

题干主问赚大钱/买房而「孩子」仅为背景时, `infer_question_theme` MUST 返回 `职业财运` 而非 `子女`.

#### Scenario: 孩子抱怨但主问发财年

- **WHEN** 题干含赚到大钱/赚大钱与买房/通勤等财运事件词
- **THEN** `infer_question_theme` 返回 `职业财运`

### Requirement: Full 通道多数投票

婚姻感情与健康疾病 (full 通道) 在操作者未显式提高 `--votes` 时, 评测 MUST 默认使用 `votes=3` 以缓解 LLM 波动.

#### Scenario: 婚姻题默认三票

- **WHEN** 题型为婚姻感情且 CLI `--votes` 为 1 (默认)
- **THEN** `predict_one` 实际执行 3 次 MCQ 推理并以多数票作为预测字母

#### Scenario: 非 full 通道保持单票

- **WHEN** 题型为 yingqi 或 static-light 且 `--votes` 为 1
- **THEN** 实际投票次数为 1

### Requirement: Full 通道保守约束

判盘链 `confidenceBand` 非 `strong` 或存在 conflicts 时, prompt MUST 注入保守作答约束, 禁止断言式排除至仅剩 1 项.

#### Scenario: 中低置信 marriage 保守

- **WHEN** 婚姻感情题处于 full 通道且 confidenceBand 为 medium 或 weak
- **THEN** prompt 包含保守约束, 选项排除须保留至少 2 项待选

### Requirement: 职业财运子题型路由

`infer_question_theme == 职业财运` 时, 系统 MUST 通过 `infer_career_subtheme` 进一步路由至子题型, 并注入对应专用推理指南与结构化格式 (替代通用 `QISHI_REASONING_GUIDE`).

#### Scenario: 财富收入子类

- **WHEN** 题干或选项含财运/身家/收入/投资/买房等财富信号
- **THEN** 子类为 `wealth`, prompt 使用 `CAREER_WEALTH_GUIDE`; 选项含年份时使用 `CAREER_WEALTH_YEAR_REASONING_FORMAT`, 否则使用 `CAREER_WEALTH_REASONING_FORMAT`

#### Scenario: 职业现状子类

- **WHEN** 题干问目前/现职/从事行业/职业名称, 且无应期年份主导
- **THEN** 子类为 `career-status`, prompt 使用 `CAREER_STATUS_GUIDE` 与 `CAREER_STATUS_MANDATORY_GUIDE`, 格式为「选项对照 + 结论」(禁止先写抽象十神块再硬套选项)

#### Scenario: 职业应期子类

- **WHEN** 题干或选项含公历年份/虚龄/哪年工作变动/突破, 或选项为纯年份 MCQ
- **THEN** 子类为 `career-year-event`, prompt 使用 `CAREER_YEAR_EVENT_GUIDE` 与 `CAREER_YEAR_EVENT_REASONING_FORMAT`; 含应期信号时 MAY 走 yingqi 通道并 force 流年块

#### Scenario: 科系取向子类

- **WHEN** 题干含「科系」或「读什么科」
- **THEN** 子类为 `major-industry`, prompt 使用 `CAREER_MAJOR_GUIDE` 与 `CAREER_MAJOR_REASONING_FORMAT`

### Requirement: 职业财运主题词扩展

`infer_question_theme` 对职业财运的关键词 MUST 包含 `身家`、`年薪`、`投资`, 避免「目前身家」等题被误判为综合题.

#### Scenario: 身家题归职业财运

- **WHEN** 题干含「身家」或「年薪」或「投资」
- **THEN** `infer_question_theme` 返回 `职业财运`

### Requirement: 职业财运子集评测与 p2 基线

职业财运 prompt 迭代 MUST 使用固定子集 (当前约 38 题) 评测; 生产基线以 p2 配置为准.

#### Scenario: 子集评测输出 careerSubtheme

- **WHEN** 运行 `run_contest_theme_subset.py --themes 职业财运`
- **THEN** JSON 报告每题含 `careerSubtheme` 字段 (wealth / career-status / career-year-event / major-industry)

#### Scenario: p2 为职业 prompt 生产基线

- **WHEN** 文档或后续变更引用职业财运 prompt 基线
- **THEN** 以 `contest8_sub_qishi_p2.json` 为准 (**18/38 = 47.4%**, 2026-06 子集实测); p3/p3b 二次分流实验已回退, 不得作为默认 prompt

#### Scenario: P3 职业财运门禁 (未完全达成)

- **WHEN** P3 职业财运阶段验收
- **THEN** 子集准确率目标 >= 14/32 (约 43.8%); p2 实测 18/38 已通过该门禁, 性格外貌子集待 P3 后续任务

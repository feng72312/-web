## 1. 基础 (路由 + 测试)

- [x] 1.1 新增 `contest_channel_route.py`, 支持 `full` / `yingqi` / static-light 判定
- [x] 1.2 yingqi 跳过判盘链与命例 RAG; static-light 跳过完整流年块
- [x] 1.3 在 `target_year_block.py` 增加虚龄/大运干支锚点
- [x] 1.4 单元测试 `tests/test_contest_channel_route.py`
- [x] 1.5 新增 `scripts/run_contest_theme_subset.py`, 支持 `--themes` / `--ids` 过滤评测
- [ ] 1.6 在 `report/命理师大赛/命理师大赛-评测说明.md` 记录基线数字

## 2. P0 - 静态题型 (学历 / 家庭出身 / 子女)

**目标:** 静态子集 (20 题) >= 8/20 (40%); 全量 200 中三类合计 >= 15/30 (50%)

- [x] 2.1 收窄 yingqi: 静态题型须满足 `has_explicit_timing_signal`
- [x] 2.2 学历/家庭 static-light 启用轻量结构化; 子女仍关闭 structured elimination
- [x] 2.3 增加静态题型 prompt 指南 (学历 `XUELI_*`, 家庭 `JIATING_*` / 子题型 guide)
- [x] 2.4 学历子集 8 题门禁 6/8 (75%), 报告 `contest8_sub_xueli_final.json`
- [x] 2.5 家庭出身 A+B: `family_subtheme.py` + `family_option_scorer.py` + prompt 接线
- [x] 2.6 家庭出身子集 14 题最佳 5/14 (35.7%), 报告 `contest8_sub_jiating_ab2.json`
- [x] 2.7 学历+家庭 22 题合计 11/22 (50%), 达 P0 静态 >= 40% 门禁
- [x] 2.8 子女子集 5 题 (P014 改判职业财运): 规则分校准后 `contest8_sub_zinv_p1.json` **3/5 (60%)**, 较 p0 1/5 提升
- [ ] 2.9 val 40 题 smoke, 要求 >= 14/40 (不退步)

**P0-E 家庭实验 (已回退, 不保留):**

- [ ] ~~2.10 方案 C votes=3~~ (abc 4/14, 未超 ab2)
- [ ] ~~2.11 方案 D+E 加权投票/强化 death 打分~~ (de2 3/14, 未超 ab2)

## 3. P1 - 应期题型 (流年事件 / 综合应期)

**目标:** 流年事件 >= 10/19 (52.6%, 对齐 fewshot); 综合 >= 15/43 (35%)

- [x] 3.1 应期 prompt 格式, 不含保守约束
- [x] 3.2 流年块内嵌虚龄/大运锚点
- [x] 3.3 修复 `format_liunian_timeline`: 题干含虚龄+大运名时输出完整运段; 选项含年份时展开整运流年
- [x] 3.4 应期信号识别支持「哪年」「那年」 (路由层 + liunian block 触发)
- [x] 3.5 跑流年事件子集 (19 题): `contest8_sub_liunian_p1b.json` **7/19 (36.8%)**, 未达门禁 >= 10/19; 婚姻 year-event 外溢子集 **1/10** 与 p5 持平
- [ ] 3.6 对比上轮 `wrong_liunian` 标签, 修复前 3 类失败模式 -- p1b 流年错题 12 题中 wrong_liunian 11 题, 待逐题 diff

## 4. P2 - 婚姻感情 + 健康疾病 (full 通道)

**目标:** 婚姻感情 >= 15/43 (35%); 健康疾病维持 >= 5/10 (50%)

- [x] 4.1 仅在 full 通道启用 `votes=3` (`resolve_contest_votes`)
- [x] 4.2 健康题含虚龄/大运时注入锚点: `health_subtheme` + `build_health_option_years_anchor` + full 通道流年 force
- [x] 4.3 审查保守约束: 仅 confidence=strong 时允许断言式排除 (prompt 更新)
- [x] 4.4 跑婚姻子集 (43 题) -- p5 **12/43** 为婚姻 prompt 基线; 门禁 >= 15/43 未达
- [x] 4.6 p5 回退 p2 prompt + 子题型仅评测元数据: `contest8_sub_hunyin_p5.json` **12/43 (27.9%)**
- [x] 4.7 p6 A类子题型路由 11/43 已回退
- [x] 4.5a 健康 p1 子集: `contest8_sub_jiankang_p1.json` **4/10 (40%)**; **定为健康 prompt 生产基线**
- [x] 4.5b 健康 p2 (status 选项对照 + dayun 五行脏腑表): `contest8_sub_jiankang_p2.json` **3/10 (30%)**, 已回退
- [x] 4.5c RAG 在线重跑 p2: `contest8_sub_jiankang_p2_rag.json` **3/10 (30%)**, 已回退
- [ ] 4.5 健康子集不低于 5/10 (维持基线) -- p1 4/10 未达, 暂停 prompt 迭代

## 5. P3 - 职业财运 + 性格外貌

**当前下一阶段:** 婚姻以 p5 收束后转入本阶段。

**目标:** 职业财运 >= 14/32 (维持); 性格外貌 >= 6/15 (40%)

- [x] 5.1 职业财运子题型分流: `career_subtheme.py` + `CAREER_*` guide/format 接线 (wealth/career-status/career-year-event/major-industry)
- [x] 5.1b 跑职业财运子集 p1: `contest8_sub_qishi_p1.json` **12/38 (31.6%)**, 较 bazi_liunian 基线 15/38 (39.5%) **-3**; wealth 4/8, year-event 5/12, status 3/17 (17.6%); 门禁未达
- [x] 5.1c p2 career-status 优化: 选项优先格式【选项对照】+ 反刻板映射 guide + `CAREER_STATUS_MANDATORY_GUIDE`
- [x] 5.1d 跑职业财运子集 p2: `contest8_sub_qishi_p2.json` **18/38 (47.4%)**, 较 p1 +6, 较 bazi_liunian 基线 15/38 **+3**; **定为职业 prompt 基线**
- [x] 5.1e p3 尝试已回退; **保留 p2 prompt 为生产基线** (`contest8_sub_qishi_p2.json` 18/38)
- [ ] 5.2 other 通道命例 RAG top_k 从 5 降至 2
- [ ] 5.3 跑职业+性格子集, 门禁合计 >= 18/47

## 6. P4 - 长尾 + 全量门禁

**目标:** 全量 >= 69/200 (34.5%), stretch 73/200

- [ ] 6.1 田宅/官非/子女应期: 扩展 `keys_liunian.py` 分类规则
- [ ] 6.2 2025 test 切片 (40 题) 逐题 diff 并修复
- [ ] 6.3 全量 200 题连跑 2 次, 均 >= 69/200
- [ ] 6.4 `write_contest_200_liunian_report.md` 增加通道分布章节
- [ ] 6.5 标记变更完成, 执行 `openspec archive improve-contest-accuracy-by-theme --yes`

## 7. 每阶段通用校验

- [x] 7.1 `py -3.10 -m pytest tests/test_contest_channel_route.py tests/test_contest8_rag.py tests/test_mcq_reasoning_mode.py tests/test_family_subtheme.py tests/test_family_option_scorer.py tests/test_children_subtheme.py tests/test_children_option_scorer.py tests/test_career_subtheme.py tests/test_career_prompts.py tests/test_health_subtheme.py tests/test_health_prompts.py tests/test_health_option_years_anchor.py -q`
- [ ] 7.2 LLM 评测前确认 RAG `http://127.0.0.1:8100/health` 返回 200
- [ ] 7.3 在 PR/任务记录中写明相对上一轮 JSON 的准确率 delta

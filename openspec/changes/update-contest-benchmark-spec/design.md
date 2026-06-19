## 规格漂移对照 (归档前 vs 当前实现)

| 主题 | 旧规格 (归档写入) | 当前实现 |
|------|-------------------|----------|
| static-light 输出 | 仅单字母, 关闭结构化推理 | 学历/家庭出身: 轻量结构化格式 + 最后一行 `答案: X`; 子女: 仍无结构化 elimination |
| static-light prompt | 未区分题型 | `XUELI_*` / `JIATING_*` 指南与 mandatory 块 |
| 静态+年份选项 | 泛 yingqi | `xueli_yingqi_mode` / `jiating_yingqi_mode` 专用格式与岁运评分 |
| 流年块 | static 与 yingqi 未区分 | static 学历/家庭不 force 完整 `build_liunian_prompt_block` |
| 题型分类 | 未说明 | 「毕业+行业/科系」等归职业财运 |
| 年份选项 regex | 未说明 | 选项内 `，2004年` 等中文逗号前缀计入 `is_year_option_mcq` |
| 子集脚本 | 仅按 theme | `run_contest_theme_subset.py` 支持 `--ids` |

## 设计原则 (写入规格)

1. **static-light != 无推理**: 指跳过判盘链、命例 RAG、完整流年时间轴; 允许题型专用短格式结构化。
2. **yingqi 可分型**: 通用 `YINGQI_*` 用于流年/综合应期; 学历/家庭出身在「选项含年份」时用专用 mandatory + format。
3. **子女保持最轻**: 无应期时仍不走结构化 elimination (与 P0 实验一致, 样本仅 6 题)。

| 家庭子题型/规则分 | 未说明 | `family_subtheme.py` + `family_option_scorer.py` + prompt 接线 |

## 非目标

- 不纳入方案 C/D/E (家庭应期 votes=3、规则分加权投票、合成流年 death 强化); 以 ab2 为保留基线.

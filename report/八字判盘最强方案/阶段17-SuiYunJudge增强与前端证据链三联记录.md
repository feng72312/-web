# 阶段17-SuiYunJudge增强与前端证据链三联记录

## 阶段目标

将 SuiYunJudge 与阶段16流年 prompt 对齐, 动态挂载大运/流年图谱 ruleIds; 前端证据链分区展示调候/岁运/格局三类主裁证据喵

## 本阶段变更

### SuiYunJudge 增强

- 新增 `_collect_suiyun_rules`: 首步大运干支 + suiyun 总则 + liunian 基础规则
- 挂载 suiyun category: `dayun_core`, `suiyun_core`
- 挂载 liunian category: `core`, `dayun_synergy`, `push_method`
- ruleIds 由 1 条扩展为约 4-6 条 (含 liunian:*)

### 证据链分组 (后端)

- `evidence.py` 新增:
  - `_build_tiaohou_evidence_item` (调候: ...)
  - `_build_suiyun_evidence_items` (大运干支/岁运总则/流年规则)
- geju / tiaohou / suiyun 三类裁判均输出分组 evidenceChain

### 前端 BaziJudgementPanel

- 证据链三区: 调候(穷通宝鉴) -> 岁运(三命通会/命理探源) -> 格局(子平真诠)
- suiyun 裁判意见 ruleIds 按 大运干支/岁运总则/流年规则 分组
- CSS: `.bazi-evidence-tiaohou-groups`, `.bazi-evidence-suiyun-groups`

### 测试

- 新建 `tests/test_suiyun_judge_enhanced.py`

## 验证结果

| 验证项 | 结果 |
|--------|------|
| pytest suiyun+evidence+judges | 9 passed |
| contest 全量重跑 | 用户要求跳过 |

## 路线衔接

- 阶段15: 调候 prompt 块
- 阶段16: 流年 prompt 块 (keys_liunian 动态规则)
- 阶段17: 判盘链 suiyun ruleIds 与前端证据链与上述两块对齐

## 仍待深化

1. SuiYunJudge 尚未按题目主题挂载 event_guanfei/event_marriage 等 (仅 prompt 层有)
2. 当前大运仍取首步, 未按目标年定位 active dayun
3. 从格真/假从精细触发

## 状态结论

**完成**. 判盘链岁运 ruleIds 增厚, 前端调候/岁运/格局证据三联展示已接通喵

# 紫微流月两口径 · mingpan 流月工具 · 奇门字段速查（2026-09-23 沉淀）

> 主题：流月扫描的引擎选择与口径分歧、mingpan 新工具用法、`generateQimen` 可用字段。
> 配套：逐月扫描流程 → SKILL.md「逐月扫描」章节；跨引擎验证 → `cross-engine-verification-2026-09.md`。

## 一、紫微流月两套口径（实测不一致，必须并列）

同一盘、同一月份，**流月命宫落宫不同**（2026-10 实测）：

| 口径 | 数据点 | 2026 年 10 月落宫 |
|---|---|---|
| iztro（`a.horoscope(new Date(y,m-1,15)).monthly.earthlyBranch`） | 流月命宫地支 → 对本命宫 | 本命**子女**宫 |
| mingpan（`mcp__mingpan__ziwei_liuyue`） | 农历九月流月宫位 | 本命**福德**宫 |

**根源**：流月命宫起法流派差异（斗君法 / 流年命宫起法）。

**处理规范（同"命卦/宅卦异判"原则）**：
1. **两口径并列陈述、注明来源，不擅自取舍**
2. **交叉验证的关键在"忌星"**——实测两口径四化忌星**完全一致**（2026-10 天机忌 ✓、2026-11 文曲忌 ✓）：**宫位定法不同但四化信号一致 → 忌星结论可用，宫位须标注口径**
3. **月界差异**：八字按**节气月**、紫微按**农历月**，错开约 2-3 天；跨月事件须标明所用月界
4. 只有一个引擎可用时：**优先取四化链最全者**（mingpan 给"本命/大限/小限/流年/流月"五层）

## 二、mingpan 流月工具（2026-09-21 接入，替代"写临时脚本 + iztro"）

| 工具 | 参数 | 返回 |
|---|---|---|
| `mcp__mingpan__bazi_liuyue` | `{year,month,day,hour,gender,ganzhiYear}` | 12 个**节气月**（干支月 + 节气起止 + 公历日期区间） |
| `mcp__mingpan__ziwei_liuyue` | `{year,month,day,hour,gender,lunarYear}` | 12 个**农历月**（流月宫位 + 宫内主星 + 五层四化） |

- `ganzhiYear` 可传干支串（`"丙午"`）或公历年；`lunarYear` 传公历年
- **一次调用即得全年逐月表** → 逐月扫描不必再写临时脚本
- 输出含跨界信息（大限/小限同列），小限维度顺带可用

## 三、`generateQimen` 可用字段（2026-09-23 实测补充）

顶层字段（实测）：`method` `scope` `juMethod` `timeInfo` `ganzhi` `isYangDun` `juShu` `zhiFu` `zhiShi` `patternTags` `patternDetails` `palaceInsights` `voidBranches` `voidPalaces` `horseStar` `specialConditions` `seasonality` `jiuGongGe` `classicPatterns` `stemRelations` `patternCombos` `directions` `yingQi` `timestamp` `evidenceAnalysis`

**两个高价值字段（此前未记录）**：
- **`r.patternDetails[]`**：每个格局标签的 `{tag, summary}`——**summary 是白话释义，可直接引用**（如"门伏吟：八门回原位，事项推进迟滞，宜耐心等待"）
- **`r.yingQi`**：**应期结构**——`rhythm`（快/中/慢）+ `triggerConditions[]`（触发条件，如"空亡在申，待冲寅填实之月日应"）+ `sources[]` + `description` + `limitations`
  - ✅ **问"什么时候应"必须引用 `yingQi`，不要自己编天数**——该字段自带纪律："快/中/慢只表示盘内相对节奏，不对应固定日数/月数"
  - 实测用法：奇门断"伏吟局应期偏迟 + 空亡待冲填实"→ 与八字流月"寅月财机"交叉，两派同指 2027 年 2 月（**多派独立指向同一时间窗 = 提高置信度的正确姿势**）

**字段陷阱（2026-09-23 复现确认）**：
- `jiuGongGe[]` 每宫的**门/神/天盘在地子对象里**——`renPan{door}`（八门）、`shenPan{god}`（八神）、`tianPan{star,stem}`、`diPan{stem}`；顶层取 `g.door` / `g.tianPanGan` 会得 `undefined`
- `r.directions` 机械输出不可照搬（`goodDirections` 常为空数组、`avoidDirections` 列满八宫）——按 SKILL.md「择方」原则交叉综合
- `r.timeInfo.juMethodNote` 给定局依据（拆补法/超神接气），`zhiFu`/`zhiShi` 直接给值符值使

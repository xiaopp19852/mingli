---
name: bazi-paipan
description: "八字排盘：根据公历/农历出生年月日时排出四柱（年柱、月柱、日柱、时柱）、藏干、十神、五行旺衰、大运、流年。确定性算法，可手工推算或用万年历数据校验。供 mingli-synthesis 伞形 skill 调用。"
version: 0.1.0
metadata:
  hermes:
    tags: [bazi, mingli, paipan, 八字]
    related_skills: [mingli-synthesis]
---

# 八字排盘（BaZi Paipan）

## 用途

根据出生时间排出四柱八字，输出供命理解读的结构化数据。本 skill 负责**排盘（确定性计算）**，解读由调用方（mingli-synthesis）完成。

## 计算层优先级（2026-08-07 更新）

1. **首选 `mcp__mingyu__bazi_prompt` / `bazi_calculate`**（mingyu MCP 已接入 Hermes）：四柱/十神/藏干/大运/神煞/旺衰/格局/调候全都有，且带证据链。参数：`dateType: solar, year, month, day, gender, timeIndex`（时辰索引）或 `birthHour/birthMinute + useTrueSolarTime + birthLongitude`
2. **详盘引擎 `scripts/bazi-python/bazi.py`**（china-testing/bazi，⭐1451）：当用户需要**合冲刑害/五行分数/命宫胎元/中医五行/大运精确起运**等深度信息时使用。输出极详尽（四柱/纳音/藏干/十神/强弱/大运/神煞/合冲刑害全会）。
   - ⚠️ **参数是农历**：`python bazi.py <农历年> <农历月> <农历日> <时辰数> [-n女命]`（时辰数 0-23，如未时=14）；公历生日需先转农历（可用 lunar_python 或让 mingyu calendar 工具换算）
   - 依赖：lunar_python、bidict、colorama（均已装）
3. **轻量引擎 `scripts/paipan.py`**（lunar_python 兼容层）：公历快速排盘，MCP 不可用时回退
4. **零依赖引擎 `scripts/zero-dep/pai_pan.py`**（2026-09-21 吸收自 GitHub jinchenma94/bazi-skill ⭐3154，MIT）：**纯 Python 标准库、零第三方依赖**——Python 缺库 / node 不可用时的最稳回退。支持 `--solar/--lunar`、`--shichen/--hour`、边界警告、大运流年、十神藏干。
   - 已三引擎交叉验证：示例命主甲 辰男 → 乙丑 壬午 戊寅 丙辰；示例命主丁 酉男 → 己亥 丙寅 辛丑 丁酉（与 mingyu-core、iztro 完全一致）
   - 用法：`python <本skill目录>/scripts/zero-dep/pai_pan.py --solar 示例命主甲 --shichen 辰 --sex 男`
   - 随附参考表：`scripts/zero-dep/references/`（五行/神煞/大运/时辰对照表，与脚本同口径）
5. 永不手工推算四柱

## 排盘引擎（已落地，2026-08-07 移植）

本 skill 自带可用引擎 `scripts/paipan.py`（源自 GitHub BIG-CR/ShenSuan，MIT）：

- **精确模式**：同目录 `scripts/sxtwl.py` 兼容层基于 `lunar_python`（寿星天文历系算法），无需编译 C++ 扩展；Python 3.14 上 sxtwl 无法编译，兼容层是官方推荐路径
- **回退模式**：无 lunar_python 时自动用纯 Python 近似算法（节气用固定日期近似，精度打折，confidence 降级）
- 输出：四柱表 + 纳音 + 藏干 + 十神 + 神煞 + 大运（精确起运年龄）+ 真太阳时/节气边界/早夜子时硬性检查提醒
- `--json` 参数输出结构化 JSON（供数据契约直接引用）

### 调用方式

```powershell
$env:PYTHONIOENCODING='utf-8'
python <本skill目录>/scripts/paipan.py <年> <月> <日> <时> <分> <经度> <纬度> <性别> [--json]
```

示例：`python ...\divination\bazi-paipan\scripts\paipan.py 1990 8 7 14 30 116.4 39.9 男 --json`

参数说明：
- 时间用公历；时/分用 24 小时制
- 经度/纬度从出生地查（北京 116.4, 39.9；上海 121.5, 31.2；广州 113.3, 23.1…）；未知用 120.0, 30.0 并注明
- 性别：男/女

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| birth_solar | 是 | 公历日期时间，如 "1990-08-07 14:30" |
| gender | 是 | 影响大运顺逆排法 |
| birth_place | 推荐 | 用于真太阳时修正（经度每偏离东经120° 1°，时间差 4 分钟） |

若用户给农历，先换算公历（可用 lunar/sxtwl 类库或万年历）。

## 排盘步骤（核心算法）

### 1. 真太阳时修正
`真太阳时 = 北京时间 + (当地经度 - 120°) × 4 分钟`。跨时辰（23:00 前后）时必须修正，否则日柱/时柱可能错位。

### 2. 年柱
以**立春**为界（不是春节）：立春前属上一年。年柱天干地支查六十甲子表。

### 3. 月柱
以**节气**为界，寅月从立春起：
- 立春→惊蛰 = 寅月（正月），惊蛰→清明 = 卯月（二月），依此类推
- 月干用"五虎遁"：年干甲己→丙寅起，乙庚→戊寅，丙辛→庚寅，丁壬→壬寅，戊癸→甲寅

### 4. 日柱
必须查**万年历**（日干支是 60 天一循环，但平闰年累积错位，无法心算可靠获得；用 sxtwl/lunar_python 库或权威万年历）。注意 23:00-24:00 归属**次日**日柱（子时换日，流派分歧：多数按"晚子时算次日"）。

### 5. 时柱
以 23:00 为子时起点，每 2 小时一个时辰（子丑寅卯辰巳午未申酉戌亥）。时干用"五鼠遁"：日干甲己→甲子起，乙庚→丙子，丙辛→戊子，丁壬→庚子，戊癸→壬子。

### 6. 十神
以日干为我：生我=印（正印/偏印）、我生=食伤（食神/伤官）、克我=官杀（正官/七杀）、我克=财（正财/偏财）、同我=比劫（比肩/劫财）。按天干阴阳定正偏。

### 7. 五行统计
四柱八个字（含藏干）各五行计数，得旺衰倾向。

### 8. 大运
阳年男/阴年女顺排，阴年男/阳年女逆排（年干定阴阳）。起运岁数 = 出生到最近换月节气的天数 ÷ 3。每步大运十年。

### 9. 流年
当前年份干支，与日主/大运作用（看合冲刑害）。

## 输出数据契约（YAML）

```yaml
system: bazi
input_used:
  birth_solar: "1990-08-07 14:30"
  true_solar_time: "1990-08-07 14:18"
  gender: "男"
  birth_place: "北京"
result:
  pillars:
    year:  {stem: 庚, branch: 午, hidden: [丁, 己]}
    month: {stem: 甲, branch: 申, hidden: [庚, 壬, 戊]}
    day:   {stem: 丙, branch: 子, hidden: [癸]}
    hour:  {stem: 乙, branch: 未, hidden: [己, 丁, 乙]}
  day_master: {stem: 丙, element: 火, yin_yang: 阳}
  five_elements: {金: 3, 木: 1, 水: 2, 火: 2, 土: 1}   # 含藏干
  ten_gods: {year_stem: 偏财, month_stem: 偏印, hour_stem: 正印, ...}
  na_yin: {year: 路旁土, month: 泉中水, day: 涧下水, hour: 砂中金}
  dayun:
    - {start_age: 4, span: "1994-2004", stem_branch: 癸未, ten_god: 正官}
    - {start_age: 14, span: "2004-2014", stem_branch: 壬午, ten_god: 七杀}
  current_year: {year: 2026, stem_branch: 丙午, relation: "与日主比肩"}
key_points:
  - "日主丙火生于申月，金旺火囚，喜木火扶身"
  - "正印透干，学业/文书运好；偏财坐年，财源在外"
  - "当前大运（若适用）对事业的影响：…"
  - "2026 丙午年火旺，对日主为帮身之年，利于行动"
confidence: high|medium|low
disclaimer: "本系统输出为传统文化符号解读，非科学预测，仅供参考。"
```

## 工具与校验

- **排盘引擎（已落地）**：`scripts/paipan.py` + `scripts/sxtwl.py` 兼容层（lunar_python），Python 3.14 免编译。执行方式见上文"排盘引擎"章节
- 依赖：`pip install lunar_python`（2026-08-07 已装）
- 手工排盘后必须自检：年柱立春边界、月柱节气边界、日柱是否查表、真太阳时是否跨时辰
- 引擎输出的"硬性检查提醒"（真太阳时/节气日/早夜子时）必须如实转述给用户
- 若引擎无法运行 → confidence: low，并明确告知用户"排盘未经精确计算"

## 诚实边界

- 排盘是确定性算法，可复现；**解读**是主观体系
- 不同流派对晚子时归属、藏干取法有分歧，标注所用流派

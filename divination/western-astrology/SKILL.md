---
name: western-astrology
description: "西方占星排盘：根据出生时间地点计算太阳/月亮/上升星座、十大行星落座与相位、宫位（Placidus等宫位制）。需要天文历计算（可调用库）。供 mingli-synthesis 伞形 skill 调用。"
version: 0.1.0
metadata:
  hermes:
    tags: [astrology, zhanxing, 占星, 星座]
    related_skills: [mingli-synthesis]
---

# 西方占星排盘（Western Astrology）

## 用途

计算出生星盘（Natal Chart）：行星位置、星座、宫位、相位。本 skill 负责**排盘**，解读由调用方完成。

## 计算层优先级（2026-08-07 更新）

1. **首选 `mcp__mingyu__astrolabe_prompt` / `divine_astrolabe`**（mingyu MCP 已接入 Hermes）：星体/宫位/相位/逆行/太阳返照/容许度全支持，附结构化证据与精度边界。参数：出生时间 + `birthLongitude`/`birthLatitude` + 时区；双盘关系用 `astrolabe_synastry_prompt`
2. **本地回退 `mingyu-core` 直接调用**（2026-08-07 实测可用，无需 MCP）：
   ```js
   // 在 C:\Users\Administrator\Documents\mingyu 下运行
   import { generateAstrolabe } from 'mingyu-core/divination/astrolabe';
   generateAstrolabe({ year: '1985', month: '6', day: '8', hour: '6', minute: '0',
     latitude: '42.3', longitude: '88.5', timeZoneId: 'Asia/Shanghai' });
   ```
   - ⚠️ **数值参数必须是字符串**（requireNumber 校验 `typeof === 'string'`），timezone 用 `timeZoneId`（IANA 名，处理历史夏令时）或纯数字字符串 `'8'`（`'+08:00'` 会被拒）
   - 返回结构：`planets[]`（name/label/sign/degree/minute/house/retrograde）、`angles[]`（Ascendant/Midheaven…）、`houses[12]`、`aspects[]`（body1/type/body2/deviation/orb）、`summary`（elements/modalities/retrograde/patterns）
3. **再回退**：用 `pyswisseph`/`flatlib` 计算（本机 Python 3.14 可用）；无库时用近似表降级
4. 出生时间不精确时上升/宫位不可靠，明确降级

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| birth_solar | 是 | 公历出生日期时间 |
| birth_place | 是(推荐) | 城市名或经纬度；决定上升星座与宫位，缺失则无法排宫位 |
| timezone | 推荐 | 缺省按出生地时区推断 |

## 排盘步骤

### 1. 天文历计算（核心）
- 行星黄经：太阳、月亮、水星、金星、火星、木星、土星、天王星、海王星、冥王星（+ 南北交点、凯龙星可选）
- **必须用天文历库**，手算不可行：`pyswisseph`（瑞士星历，业界标准）、`astropy`、`skyfield`、`flatlib`（封装 swisseph 的占星库）
- 无库时可用在线 API（如 astro.com 数据）或明确降低 confidence

### 2. 星座判定
行星黄经 ÷ 30° → 星座（0-29° 白羊，30-59° 金牛…）。太阳星座即太阳落座。

### 3. 上升星座（ASC）
出生地经纬度 + 恒星时 + 黄赤交角 → 上升点黄经 → 落座。**依赖精确出生时间**（误差几分钟可能改上升）。

### 4. 宫位制
- 常用 Placidus（不等宫，需精确出生时间）；时间不精确时用 Equal（等宫）
- 十二宫：命宫(1)、财帛(2)、兄弟(3)、田宅(4)、子女(5)、奴仆(6)、夫妻(7)、疾厄(8)、迁移(9)、官禄(10)、交友(11)、玄秘(12)

### 5. 相位
行星黄经差：合相(0°)、六分(60°)、四分(90°)、三分(120°)、对冲(180°)。容许度：日月 8-10°，行星 6-8°（标注所用容许度）。

## 输出数据契约（YAML）

```yaml
system: astrology
input_used:
  birth_solar: "1990-08-07 14:30"
  birth_place: "北京"
  timezone: "+08:00"
  house_system: Placidus
result:
  ascendant: {sign: 处女, degree: "12°34'"}
  midheaven: {sign: 双子, degree: "28°10'"}
  planets:
    sun:    {sign: 狮子, degree: "14°45'", house: 10}
    moon:   {sign: 双子, degree: "03°20'", house: 8}
    mercury:{sign: 狮子, degree: "01°12'", house: 10}
    venus:  {sign: 处女, degree: "25°08'", house: 11}
    mars:   {sign: 天秤, degree: "18°55'", house: 12}
    jupiter:{sign: 巨蟹, degree: "02°30'", house: 9}
    saturn: {sign: 摩羯, degree: "16°42'", house: 4}
    uranus: {sign: 摩羯, degree: "04°15'", house: 4}
    neptune:{sign: 摩羯, degree: "11°33'", house: 4}
    pluto:  {sign: 天蝎, degree: "15°21'", house: 2}
  aspects:
    - {p1: sun, p2: moon, type: 三分, orb: "2°"}
    - {p1: mars, p2: saturn, type: 四分, orb: "1°"}
  houses:
    house1: {sign: 处女, ruler: 水星}
    house10: {sign: 双子, ruler: 水星}
key_points:
  - "太阳狮子落 10 宫，事业心强，渴望公众认可"
  - "月亮双子落 8 宫，情绪波动大，对深层资源/心理议题敏感"
  - "火星天秤 12 宫四分土星，行动力易受阻，宜以柔克刚"
  - "土星摩羯落 4 宫，原生家庭/根基议题是长期功课"
confidence: high|medium|low
disclaimer: "本系统输出为传统文化符号解读，非科学预测，仅供参考。"
```

## 工具与校验

- **优先**：Python 安装 `pyswisseph` 或 `flatlib` 计算；`astropy` 可算黄经但需自行处理宫位
- 校验点：太阳落座应与出生日期常识一致（如 8 月初应为狮子）；上升需与生时核对
- 无库且无法访问星历 → 仅输出太阳/月亮/上升的大致星座（用近似表），confidence: low 并注明"未做精确星历计算"

## 诚实边界

- 占星体系（本命盘/流年推运/合盘）解读是主观体系；排盘数据是天文事实
- 出生时间不精确时，上升与宫位不可靠，明确降级
- 注明星历来源与容许度设定

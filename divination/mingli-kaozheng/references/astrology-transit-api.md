# 占星流年推运 API（mingyu-core astrolabe-scope，2026-08-07 实测）

占星流年推运（行运 transit / 太阳返照 / 次限推进 / 太阳弧）用于与八字流年互证。
`western-astrology` skill 本体受保护不可编辑，本文件作为其"计算层 2.2"的详细版。

## 代码（在 C:\Users\Administrator\Documents\mingyu 下运行）

```js
import { generateAstrolabe } from 'mingyu-core/divination/astrolabe';
import { buildAstrolabeScopeContext } from 'mingyu-core/divination/astrolabe-scope';

const raw = generateAstrolabe({
  year: '1985', month: '6', day: '8', hour: '6', minute: '0',
  latitude: '42.3', longitude: '88.5', timeZoneId: 'Asia/Shanghai',
});
const natal = raw?.result ?? raw;   // 兜底：generateAstrolabe 返回值可能无 .result 顶层

// dateStr 只传年份 YYYY——传完整日期会报 "流年必须提供 YYYY 格式的明确日期"
const ctx = buildAstrolabeScopeContext(natal, 'yearly', '2026');
const r = ctx?.result ?? ctx;
```

## 输出结构（r.promptText 为解读主输入）

`promptText` 字符串包含五段（JSON 化后一次性给出）：
1. **本命宫主星**：每宫宫头星座 + 宫主星落座落宫
2. **主要行运相位**：如 `天王星☌上升（合相，偏差0.10°，紧密，精准）`——行运行星 vs 本命四轴/行星
3. **行运落宫**：木星/土星/天王/海王/冥王当年落本命第几宫
4. **太阳返照**（solar return）：当年生日时刻返照盘主要相位（如"太阳合相太阳 紧密"）
5. **次限推进 + 太阳弧**：`calculateSecondaryProgressionEvidence` / `calculateSolarArcEvidence` 结果

## 参数怪癖（都是实测踩过的坑）

| 项 | 规则 |
|---|---|
| astrolabe 数值参数 | **必须是字符串**（requireNumber 校验 typeof==='string'）：`'1985'` 非 `1985` |
| timezone | 用 `timeZoneId: 'Asia/Shanghai'`（IANA 名，处理历史夏令时）或纯数字字符串 `'8'`；`'+08:00'` 会被正则拒绝 |
| scope 日期 | `buildAstrolabeScopeContext` 的 dateStr **只传年份 `'2026'`** |
| 返回值兜底 | `raw?.result ?? raw` 再取 `.planets` / `.angles` |
| 行运基准 | 默认取当年 7-01 中午（出生地时区）——年中快照，解读时注明 |

## 互证方法论

- **两系统同向 = 高置信**：占星行运信号与八字流年干支结论一致时，判词权重最高
- 实测互证案例（示例命主甲 辰时命局）：
  - 2027：行运**天王星合上升**（精准 0.10°）↔ 八字丁未年**丑未冲**"根基重组" → 同向：2027 是变动重组年
  - 2028：行运**土星拱天顶** ↔ 八字戊申**申金生水**"转机元年" → 同向：2028 是起势年
  - 2026：行运金星冲本命月亮（入相）↔ 八字丙午火年 → 同向：感情/财务拉锯
- **占星补八字什么**：人格结构（群星双子=信息型）、关系模式（金星落座）、时代压力（外行星行运）——八字不直接给的视角

## 占星解读要点（本命盘）

- 上升 + 太阳/月亮/水星/火星落座落宫 → 人格结构
- 金星落座落宫 → 感情/审美/财富模式（如金星金牛12宫=暗桃花、慢热）
- 土星落座 → 长期功课（如土星天蝎6宫=工作/健康纪律）
- 格局：Grand Trine（天赋）/ T-Square（张力）/ Mystic Rectangle
- 外行星逆行（天王海王冥王）是时代印记，80年代出生者普遍，不单独断吉凶

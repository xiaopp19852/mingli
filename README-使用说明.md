# 命理技能包（Divination Skills Pack）

> 面向 AI Agent（Claude Code / Cursor / Codex / Hermes / 其他支持 Skill 机制的 Agent）的中式术数推演技能集。
> 打包日期：2026-09-23 ｜ 版本：1.0 ｜ 引擎：mingyu-core（可选）

## 一、这是什么

一套**方法论 + 解读框架**的技能集，覆盖传统术数主流体系。技能本身**不做排盘计算**——排盘交给确定性引擎（mingyu-core / lunar_python / iztro），
AI 只负责**解读、交叉验证与合参**。这是本包的核心设计原则：**排盘零误差，解读有据可依**。

## 二、包含技能（共 16 个）

| 技能 | 作用 |
|---|---|
| `bazi-paipan` | 八字排盘（子平 × 盲派双口径），四级计算层（MCP → 详盘 → 轻量 → 零依赖） |
| `ziwei-paipan` | 紫微斗数排盘（安星、四化、大限流年） |
| `qimen-paipan` | 奇门遁甲起局（时家转盘，含格局判读） |
| `western-astrology` | 西方占星排盘（行星落座、宫位、相位） |
| `zhouyi-hexagram` | 周易起卦（梅花易数 / 金钱卦、装卦断卦） |
| `tarot-reading` | 塔罗牌解读（韦特 78 张、常用牌阵） |
| `tarot-pro` | 塔罗进阶（专业牌阵与解读框架） |
| `shensuan` | 单一体系深度判词（八面输出、每法 400 字） |
| `bazi-ziwei` | 八字 + 紫微双盘印证（含命盘海报渲染） |
| `fengshui-master` | 风水（八宅游年 + 玄空飞星 + 形势峦头） |
| `mingli-synthesis` | **多系统合参编排（五轮圆桌协议）**——本包核心 |
| `mingli-paipan-practice` | 实战规范（跨引擎验证、时辰流派、话术纪律） |
| `mingli-kaozheng` | 古籍考据与论证方法 |
| `mingli-guji-lunzheng` | 五部古籍为纲的论证法（附九籍要点摘要） |
| `zhongxi-huzheng` | 中西体系互证（东方算应期、西方算结构） |
| `yueyuan` | 子平八字专业分析系统（含研究性取径） |

## 三、安装

把本目录下的子目录整体复制到你的 Agent 技能目录：

```bash
# Hermes Agent
cp -R divination ~/.hermes/skills/

# Claude Code
cp -R divination ~/.claude/skills/

# Cursor
cp -R divination .cursor/skills/

# Codex
cp -R divination ~/.codex/skills/
```

## 四、计算引擎依赖（可选，建议装）

技能是"解读层"，排盘需要引擎。三种任选：

**方式 A：mingyu-core（完整功能，56 工具）**
```bash
git clone <mingyu-core 仓库> && cd mingyu-core && pnpm install && pnpm build
```

**方式 B：Python 轻量（推荐给不想装 Node 的人）**
```bash
pip install lunar_python bidict colorama
# bazi-paipan/scripts/paipan.py 即可用
```

**方式 C：零依赖回退（最稳）**
```bash
# bazi-paipan/scripts/zero-dep/pai_pan.py —— 纯 Python 标准库，无任何第三方依赖
python pai_pan.py --solar 1990-05-27 --shichen 卯 --sex 男
```

**紫微斗数**：`bazi-ziwei/` 下的 Node 脚本需 `npm install`（lunar-typescript）。

## 五、三条铁律（本技能包的核心纪律）

1. **排盘零误差**——AI **绝不手工推算**四柱/星盘/卦象；一律用引擎，且关键盘面用**多引擎交叉验证**（四柱必须完全一致）
2. **古籍为纲**——以《滴天髓》《子平真诠》《穷通宝鉴》《三命通会》《渊海子平》五部为纲，无据不妄断；引文须核对原文
3. **诚实输出**——不套话、不迎合、不用弹性话术；结论标注置信度（高/中/低）；分歧如实并列，不强行调和

## 六、推荐工作流

```
信息采集（生辰/问事时刻，缺则追问）
  → 真太阳时修正（跨时辰边界时双版并列）
  → 引擎排盘（多引擎交叉验证）
  → 各体系独立解读（隔离，互不污染）
  → 五轮圆桌合参（立论→质询→辩论→修正→综合）
  → 输出（共识/分歧/应期/行动建议 + 置信度）
```

## 七、免责声明

- 本技能包输出基于公开的传统术数规则与古籍文献，属**传统文化符号体系**，**非科学预测**
- 不构成医疗、法律、投资、婚姻等任何决策建议；重大事项请咨询相应专业人士
- 术数推演结果与现实事件的因果关系未经科学证实，请以批判性思维对待所有输出
- 命盘分析涉及个人隐私数据，使用者应自行负责数据合规

## 八、关于本包的内容说明

**本包已移除全部真实个人命例**（案例库、风险扫描、合盘实例、风水实勘记录等），
文中出现的「示例命主甲/乙/丙…」均为**虚构占位符**，不对应任何真实个人。

如果你希望 AI 自己的命例库也能沉淀，建议在自己的实例里建立 `references/` 案例目录——
本包的 `mingli-paipan-practice/SKILL.md` 描述了规范做法（脱敏后参考）。

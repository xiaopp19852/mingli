# 超大型 MCP 结果（合盘类）落盘提取法（2026-09-21 实测）

## 现象

`mcp__mingyu__bazi_compatibility` / `mcp__mingyu__ziwei_compatibility` 单次调用返回 **~72-74 万字符**（700KB+）→ 工具层直接拦截，内容**自动落盘**：

```
<hermes-home>/cache/terminal/hermes-results/call_<NN>_<id>.txt
```

返回值里只给 preview（约 1500 字符）+ 落盘路径。**不要重跑**（同样巨大、浪费一轮），直接解析落盘文件。

## 解包陷阱（两层）

顶层是 `{"result": ...}`，而 `result` 可能是：

- **dict**（本次实测）
- **JSON 字符串**（其他工具见过）

→ 循环 unwrap 3-4 层，两种都要容错：

```python
import json, sys
sys.stdout.reconfigure(encoding='utf-8')   # Windows 下中文必加，否则 UnicodeEncodeError

def load(p):
    d = json.loads(open(p, encoding='utf-8').read())
    for _ in range(4):
        if isinstance(d, dict) and 'result' in d:
            r = d['result']
            d = json.loads(r) if isinstance(r, str) else r
        else:
            break
    return d
```

## 字段路径（实测，直接取这些最省 token）

**八字合盘**（`compatibility` 下）：
- `dayMasterRelation`：`person1ToPerson2`（克对方/受克）、`person2GanAsPerson1TenGod`（对方日干是我的什么十神）
- `crossPillarRelations[]`：`layer`(天干/地支) / `type`(五合候选/天干冲/六害/六破/三刑/同支) / `person1Pillar`/`person2Pillar` / `person1Value`/`person2Value`
- `crossBranchCombinations[]`：三会/三合，`status`=组合齐备
- `tenGodMappings[]`：双向十神（observer/source/pillar/stem/stemTenGod/branchMainQiTenGod）
- `usefulGodCoverage[]`：`favorable`/`unfavorable` + `sources`（谁给谁供五行）
- `counterEvidence[]`、`limitations[]`、`summaryFact`
- **`promptText`（≈5.7K 字符）= 引擎自带的解读提示词，性价比最高，优先读它**

**紫微合盘**（`compatibility` 下）：
- `palaceOverlays[]` → **多为空对象**，真实内容在 `evidence.items[]`
- `crossMutagenPlacements[]`：`star`/`mutagen`/`targetPalace`（谁的四化落对方哪一宫）
- **`evidence.items[]`**：`level`（主证/辅证/反证）+ `title` + `detail` + `source` + `tags`——**结论直接读这里**
- `summaryFact`（宫位/四化命中统计）、`limitations[]`

## 通用纪律

- 脚本放临时目录、跑完即删（`rm -f`）；不在 mingyu 工作区留文件（该目录是 git 仓库）
- 一次脚本打印**精简结论**（关键字段 + 前 N 条列表），不要 print 整个 JSON
- 落盘文件可反复读，不必重跑工具；同一个文件解析脚本可复用（本次一改字段名/路径即可）

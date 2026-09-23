# 神算 ShenSuan 集成评估（2026-08-07）

外部八字引擎候选：https://github.com/BIG-CR/ShenSuan （MIT，star 少但质量高，2026-06 更新）

## 仓库结构

- SKILL.md（23KB）— Claude Code skill 主体：三大分类 26 法（八字 12 / 问事 8 / 环境 6）
- paipan.py（27.6KB, 712 行）— 八字排盘引擎：sxtwl 驱动 + 纯 Python 回退
- methods.json / tiaohou.json / shensha.json / calendar_reference.json / cases.json / industry_wuxing.json — 知识库
- test_skill.sh — 测试脚本

## 评估结论

强项：
- paipan.py 含真太阳时修正（经度 + 均时差 Spencer 公式）、节气边界/早夜子时硬检查、精确起运年龄（距节气天数÷3）
- 判词规范：每法≥400字、八面硬性输出（格局/性格/事业/财富/人际/感情/流年/行动）、禁词表（算命/预测/吉凶→分析/参考/觉察）
- 交互铁律：首轮全量问 → 追问到底 → 确认再进 → 不替用户选分类

局限：
- 路径写死 `.claude/skills/`，auto-memory 为 Claude 机制，装 Hermes 需改路径
- 自述局限：紫微斗数/七政四余/铁板神数、奇门/大六壬需外部专业软件
- 无西方占星/塔罗（由本套件 divination 补位）
- 本机未装 sxtwl 时走近似回退（节气用固定日期近似），装库后满血

## 实测记录（本机 python 3.14，无 sxtwl）

```powershell
$env:PYTHONIOENCODING='utf-8'
python paipan.py 2004 1 19 12 0 118.5 25.5 男
```
正常输出四柱/纳音/藏干/十神/神煞/大运/真太阳时偏移，exit 0。
安装 sxtwl 提升精度：`pip install sxtwl`

## 国内网络下载配方（raw.githubusercontent.com 直连超时）

1. jsDelivr CDN（首选，实测成功）：
   `curl.exe -sL --max-time 40 -o <dst> "https://cdn.jsdelivr.net/gh/BIG-CR/ShenSuan@main/<file>"`
2. GitHub API contents（base64）备选——注意 PowerShell 5.1 中
   `[Convert]::FromBase64String($j.content -replace '\s','')` 会报"重载参数计数为 2"；
   先把 content 存入中间变量再转换，或直接用方法 1。

## 集成路径（待用户决策）

1. `pip install sxtwl` + 移植 paipan.py → bazi-paipan/scripts/（把"算法描述"升级为"真能算"）
2. 整仓装为独立 skill（改 .claude/skills 路径适配 Hermes，内存机制换成 Hermes memory）
3. 吸收八面输出/400 字判词/禁词规范进 mingli-synthesis 的输出铁律

# Divination Skills 打包分发工作流（2026-08-08 实测）

把整套 divination skill 体系打包成 zip 给其他 AI（Claude Code / Cursor / Codex / Gemini CLI / 其他 Hermes 实例）使用的方法。产物：`C:\Users\Administrator\Documents\divination-pack\divination-skills.zip`（约 1.2 MB）。

## 一、打包步骤（PowerShell）

```powershell
$src = "C:\Users\Administrator\AppData\Local\Hermes Agent CN Desktop\data\hermes-home\skills\divination"
$dst = "C:\Users\Administrator\Documents\divination-pack\divination"
$pack = "C:\Users\Administrator\Documents\divination-pack"

# 1. 复制（排除 node_modules —— 26MB 本地依赖，目标环境需自行 npm install）
Get-ChildItem $src -Directory | ForEach-Object {
  $target = Join-Path $dst $_.Name
  Get-ChildItem $_.FullName -Recurse -File | Where-Object { $_.FullName -notmatch 'node_modules' } |
    ForEach-Object {
      $destFile = Join-Path $target $_.FullName.Substring($_.DirectoryName.Length).TrimStart('\')
      New-Item -ItemType Directory -Force -Path (Split-Path $destFile) | Out-Null
      Copy-Item $_.FullName $destFile -Force
    }
}

# 2. 清理 .pyc 和 __pycache__（Python 编译缓存，跨机不兼容）
Get-ChildItem $dst -Recurse -File -Filter "*.pyc" | Remove-Item -Force
Get-ChildItem $dst -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# 3. 压缩（README 必须在 zip 内）
Compress-Archive -Path "$dst", "$pack\README-使用说明.md" -DestinationPath "$pack\divination-skills.zip" -CompressionLevel Optimal

# 4. 验证 zip 内容
Add-Type -AssemblyName System.IO.Compression.FileSystem
$z = [IO.Compression.ZipFile]::OpenRead("$pack\divination-skills.zip")
$z.Entries.Count; $z.Entries | Select-Object -First 8 | ForEach-Object { $_.FullName }; $z.Dispose()
```

## 二、关键决策点

1. **node_modules 必须排除**：bazi-ziwei/calculator 的 node_modules 占 26MB，且依赖（lunar-typescript）应由目标环境 `npm install` 安装——README 写明即可
2. **.pyc 必须清理**：Python 编译缓存含绝对路径/版本信息，跨机可能不兼容；纯 .py 源码可在目标机重新编译
3. **README 是必需品**：写明各平台技能目录（Claude Code `~/.claude/skills/`、Cursor `.cursor/skills/`、Codex `~/.codex/skills/`、Hermes `~/.hermes/skills/`）+ 引擎依赖三种方式（mingyu-core 全功能 / Python lunar_python 轻量 / bazi-ziwei Node）+ 三条纪律
4. **引擎与 skill 分离的说明**：skill 是"方法论+解读框架"，mingyu-core（56 工具）是"计算引擎"——别人要完整功能须按 README 装 mingyu

## 三、README 必备内容清单

- 15 个 skill 一览表（名称+作用+触发条件）
- 引擎依赖：方式 A mingyu-core（git clone + pnpm install + build）/ 方式 B Python（pip install lunar_python bidict colorama）/ 方式 C bazi-ziwei Node（npm install）
- 三条铁律：排盘零误差（AI 绝不手排八字/紫微/星盘）、古籍为纲（五部经典，凡古籍无据者不妄断）、诚实输出（视角不是预言，禁套话禁迎合）
- 已知参数陷阱表（mingyu 字符串参数 / timeZoneId / qimen Date 对象 / bazi.py 农历参数）
- 推荐工作流（真太阳时修正 → 算法排盘 → 古籍论证 → 占星推运 → 交叉验证 → 归档）

## 四、验证要点

- 复制后抽查每个子目录的 SKILL.md 存在性（15/15）
- 检查引擎文件完整性（bazi-paipan 的 paipan.py、shensuan 的 JSON 数据）
- zip 条目数核对（约 120 文件 + README）
- 最终包体积目标 < 2 MB（去 node_modules 后）

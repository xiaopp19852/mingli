# Windows 内置 OCR 读取图片文字（PowerShell + WinRT，支持中文）

2026-08-08 验证：本地无 pytesseract/easyocr/paddleocr 时，Windows 11 自带 OCR 引擎（WinRT API）可识别简体中文。用于读取用户上传的命盘截图、命理 prompt 图、聊天记录截图等。

## 完整可用脚本（复制即用）

```powershell
$img = "C:\path\to\image.png"  # 换成实际图片路径

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics,ContentType=WindowsRuntime]

function Await($WinRtTask, $ResultType) {
  $asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
  $asTaskGeneric = $asTask.MakeGenericMethod($ResultType)
  $netTask = $asTaskGeneric.Invoke($null, @($WinRtTask))
  $netTask.Wait(-1) | Out-Null
  $netTask.Result
}

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($img)) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if (-not $engine) { Write-Output "无可用 OCR 引擎（检查系统语言包）"; exit }
Write-Output ("OCR 引擎语言: " + $engine.RecognizerLanguage.DisplayName)

$result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
# 中文识别结果每字带空格，去掉便于阅读
($result.Text -replace ' ', '')
```

## 关键坑（实测踩过）

1. **必须先用 `$null = [Windows.Storage.StorageFile,...]` 加载 3 个 WinRT 类型**——否则 Await 里的泛型 AsTask 找不到类型定义，直接报错
2. `Await` 函数用反射找 `AsTask` 泛型方法并 MakeGenericMethod——这是 WinRT 异步转 .NET Task 的标准包装，不要改动
3. `TryCreateFromUserProfileLanguages()`：中文系统返回简体中文引擎；若返回 null，检查系统是否装了中文语言包
4. 输出 `$result.Text`：中文每字间有空格（OCR 引擎特性），`-replace ' ',''` 后即正常文本
5. 支持 PNG/JPG/BMP；大图（>4K）可能慢，可先用 PIL 缩放到宽 <2000px

## 备选

- 若图片需要"看图"而非"读字"（如命盘图形、海报），本地无视觉模型时：先 OCR 提取文字 + 用 PIL 读尺寸/色块特征，再结合上下文推断——不能替代真正看图，需向用户说明局限

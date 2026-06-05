param(
  [string]$OutputPath = "artifacts\map_years.gif",
  [int]$DelayCs = 85
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$siteRoot = Join-Path $projectRoot "site"
$summaryPath = Join-Path $siteRoot "assets\data\summary.json"
$capturePage = Join-Path $siteRoot "map_capture.html"
$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if (-not (Test-Path $edgePath)) {
  throw "No se encontró Microsoft Edge en: $edgePath"
}

if (-not (Test-Path $summaryPath)) {
  throw "No se encontró summary.json en: $summaryPath"
}

if (-not (Test-Path $capturePage)) {
  throw "No se encontró map_capture.html en: $capturePage"
}

$summary = Get-Content $summaryPath -Encoding utf8 | ConvertFrom-Json
$years = @($summary.available_years | ForEach-Object { [int]$_ } | Sort-Object)

$outputAbsolute = if ([System.IO.Path]::IsPathRooted($OutputPath)) {
  $OutputPath
} else {
  Join-Path $projectRoot $OutputPath
}

$outputDir = Split-Path -Parent $outputAbsolute
$framesDir = Join-Path $projectRoot "artifacts\map_frames"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
New-Item -ItemType Directory -Force -Path $framesDir | Out-Null
Get-ChildItem $framesDir -Filter "*.png" -ErrorAction SilentlyContinue | Remove-Item -Force

$capturePageUri = ([System.Uri]$capturePage).AbsoluteUri

foreach ($year in $years) {
  $framePath = Join-Path $framesDir ("frame_{0}.png" -f $year)
  $url = "$capturePageUri#$year"
  & $edgePath `
    --headless `
    --disable-gpu `
    --hide-scrollbars `
    --window-size=1440,960 `
    "--screenshot=$framePath" `
    "$url" | Out-Null
}

Add-Type -AssemblyName System.Drawing

function New-PropertyItem {
  param(
    [int]$Id,
    [int]$Type,
    [byte[]]$Value
  )

  $item = [System.Runtime.Serialization.FormatterServices]::GetUninitializedObject([System.Drawing.Imaging.PropertyItem])
  $item.Id = $Id
  $item.Type = $Type
  $item.Len = $Value.Length
  $item.Value = $Value
  return $item
}

function Get-GifEncoder {
  return [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/gif" }
}

$frameFiles = Get-ChildItem $framesDir -Filter "*.png" | Sort-Object Name
if ($frameFiles.Count -eq 0) {
  throw "No se generaron frames PNG."
}

$images = New-Object System.Collections.Generic.List[System.Drawing.Image]
foreach ($frame in $frameFiles) {
  $images.Add([System.Drawing.Image]::FromFile($frame.FullName))
}

try {
  $gifEncoder = Get-GifEncoder
  $first = $images[0]

  $delayBytes = New-Object byte[] ($images.Count * 4)
  for ($i = 0; $i -lt $images.Count; $i++) {
    [BitConverter]::GetBytes([int]$DelayCs).CopyTo($delayBytes, $i * 4)
  }

  $loopBytes = [byte[]](0, 0)
  $first.SetPropertyItem((New-PropertyItem -Id 0x5100 -Type 4 -Value $delayBytes))
  $first.SetPropertyItem((New-PropertyItem -Id 0x5101 -Type 3 -Value $loopBytes))

  $encoder = [System.Drawing.Imaging.Encoder]::SaveFlag
  $params = New-Object System.Drawing.Imaging.EncoderParameters 1
  $params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter($encoder, [long][System.Drawing.Imaging.EncoderValue]::MultiFrame)
  $first.Save($outputAbsolute, $gifEncoder, $params)

  $params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter($encoder, [long][System.Drawing.Imaging.EncoderValue]::FrameDimensionTime)
  foreach ($img in $images | Select-Object -Skip 1) {
    $first.SaveAdd($img, $params)
  }

  $params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter($encoder, [long][System.Drawing.Imaging.EncoderValue]::Flush)
  $first.SaveAdd($params)
}
finally {
  foreach ($img in $images) {
    $img.Dispose()
  }
}

Write-Output "GIF generado en: $outputAbsolute"

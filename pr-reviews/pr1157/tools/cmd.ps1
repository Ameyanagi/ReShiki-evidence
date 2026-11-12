$ErrorActionPreference = 'Continue'; $ProgressPreference = 'SilentlyContinue'
. F:\clip2\clipfmt.ps1; . F:\clip2\uia.ps1
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$Harness = 'F:\clip-target\release\deps\clip_harness-50f9cdf591df0772.exe'
$env:CLIP_RSK = 'F:\clip2\caffeine.rsk'
"Paint $((Get-AppxPackage Microsoft.Paint).Version)"
foreach ($v in @(@{n='copy'; i='0'}, @{n='copy-image'; i='1'})) {
  "=== $($v.n)"
  $env:RESHIKI_DATA_DIR = (New-Item -ItemType Directory -Force "F:\clip2\data\copy-$(Get-Random)").FullName
  $env:CLIP_IMAGE_ONLY = $v.i
  & $Harness clip_harness --ignored --exact --nocapture 2>&1 | Select-String 'test result' | % { "harness: $($_.Line)" }
  "before paste: $(([CB]::Dump([NullString]::Value)) -join ' / ')"
  Paint-Paste
  $img = [Windows.Forms.Clipboard]::GetImage()
  if ($img) { $img.Save("F:\clip2\out\paint-$($v.n)-copied-back.png", [Drawing.Imaging.ImageFormat]::Png); "Paint copied back a $($img.Width)x$($img.Height) bitmap -> paint-$($v.n)-copied-back.png" } else { "no image copied back" }
}
"leftover: $((Get-Process mspaint -EA SilentlyContinue | % Id) -join ' ')"

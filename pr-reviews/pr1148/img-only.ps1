param([string]$Harness)
. F:\clip-run\clipfmt.ps1; . F:\clip-run\office.ps1
$key = 'HKCU:\Software\Classes\CLSID\{3BAC2B7E-73A2-4F3A-9CE7-5E9B438C59B4}\LocalServer32'
$installed = '"' + $env:LOCALAPPDATA + '\Programs\ReShiki\reshiki.exe" --ole-server'
"leftover: $((Get-Process WINWORD,EXCEL,msedge -EA SilentlyContinue | % { "$($_.Name)/$($_.Id)" }) -join ' ')"
$env:CLIP_RSK = 'F:\clip-run\caffeine.rsk'
foreach ($n in 1,2) {
  $env:RESHIKI_DATA_DIR = (New-Item -ItemType Directory -Force "F:\clip-run\data\copy-$(Get-Random)").FullName
  $env:CLIP_IMAGE_ONLY = '1'
  & $Harness clip_harness --ignored --exact --nocapture 2>&1 | Select-String 'test result' | % { "harness: $($_.Line)" }
  Edge-Paste "after-image-$n"
}
Set-ItemProperty $key '(default)' $installed; "LocalServer32: $((Get-ItemProperty $key).'(default)')"

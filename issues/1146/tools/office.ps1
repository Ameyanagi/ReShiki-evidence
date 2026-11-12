# Dot-source. Paste the current clipboard into fresh Word/PowerPoint/Excel documents via COM and
# report what landed; every document is closed without saving.
$ErrorActionPreference = 'Continue'
function Kind($t, $map) { if ($map.ContainsKey([int]$t)) { "$t ($($map[[int]$t]))" } else { "$t" } }
$mso = @{ 7='embedded OLE object'; 13='picture'; 28='graphic (SVG)'; 1='autoshape'; 17='text box'; 6='group' }
function Prog($s) { try { $s.OLEFormat.ProgID } catch { '-' } }
function Word-Paste {
  try {
    $w = New-Object -ComObject Word.Application; $w.DisplayAlerts = 0; $d = $w.Documents.Add()
    $w.Selection.Paste()
    $inl = $d.InlineShapes; $sh = $d.Shapes
    $wd = @{ 1='embedded OLE object'; 3='picture'; 8='graphic (SVG)'; 2='linked OLE' }
    $r = "Word: inline=$($inl.Count) floating=$($sh.Count) chars=$($d.Content.Text.Trim().Length)"
    if ($inl.Count -ge 1) { $i = $inl.Item(1); $r += " type=$(Kind $i.Type $wd) progid=$(Prog $i) size=$([math]::Round($i.Width,1))x$([math]::Round($i.Height,1))pt" }
    if ($sh.Count -ge 1) { $s = $sh.Item(1); $r += " shape-type=$(Kind $s.Type $mso) progid=$(Prog $s)" }
    $r
  } catch { "Word: ERROR $_" }
  finally { if ($d) { $d.Saved = $true; $d.Close([ref]0) }; if ($w) { $w.Quit([ref]0) } }
}
function PowerPoint-Paste {
  try {
    $running = [bool](Get-Process POWERPNT -EA SilentlyContinue)
    $p = New-Object -ComObject PowerPoint.Application; $pr = $p.Presentations.Add(-1); $sl = $pr.Slides.Add(1, 12)
    $r = $sl.Shapes.Paste(); $s = $r.Item(1)
    $o = "PowerPoint: shapes=$($r.Count) type=$(Kind $s.Type $mso) progid=$(Prog $s) size=$([math]::Round($s.Width,1))x$([math]::Round($s.Height,1))pt"
    $pr.Saved = -1; $pr.Close(); if (-not $running) { $p.Quit() }; $o
  } catch { "PowerPoint: ERROR $_" }
}
function Excel-Paste {
  try {
    $x = New-Object -ComObject Excel.Application; $x.DisplayAlerts = $false; $wb = $x.Workbooks.Add(); $ws = $wb.Worksheets.Item(1)
    $ws.Range('B2').Select() | Out-Null; $ws.Paste()
    $o = "Excel: shapes=$($ws.Shapes.Count)"
    if ($ws.Shapes.Count -ge 1) { $s = $ws.Shapes.Item(1); $o += " type=$(Kind $s.Type $mso) progid=$(Prog $s)" } else { $o += " B2='$($ws.Range('B2').Text)'" }
    $wb.Close($false); $x.Quit(); $o
  } catch { "Excel: ERROR $_" }
}
function Edge-Paste($tag) {
  $d = "F:\clip-run\edge-$tag-$(Get-Random)"
  $j = & node F:\clip-run\cdp_paste.mjs 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' F:\clip-run\probe.html 9411 $d "F:\clip-run\out\edge-$tag.png" 2>&1
  Start-Sleep 2; Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" | ? CommandLine -like "*$d*" | % { Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue }
  Start-Sleep 1; Remove-Item -Recurse -Force $d -EA SilentlyContinue
  "Edge (Chromium, as WebView2 / new Outlook / Outlook on the web): $($j -join ' ')"
}

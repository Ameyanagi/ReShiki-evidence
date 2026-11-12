# Dot-source. Paint-Paste: paste into a fresh Paint through its Edit menu (UI Automation, works on a
# locked desktop), then Edit > Copy, and report what Paint put back on the clipboard.
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$AE = [Windows.Automation.AutomationElement]; $TS = [Windows.Automation.TreeScope]
$EDIT = [string][char]0x7DE8 + [char]0x96C6; $PASTE = [string][char]0x8CBC + [char]0x308A; $COPY = [string][char]0x30B3 + [char]0x30D4 + [char]0x30FC
function Find-Name($scope, $name, $ctl) {
  for ($i = 0; $i -lt 20; $i++) {
    $all = $scope.FindAll($TS::Descendants, [Windows.Automation.Condition]::TrueCondition)
    foreach ($e in $all) { $c = $e.Current; if ($c.Name -like "$name*" -and $c.ControlType.ProgrammaticName -eq $ctl) { return $e } }
    Start-Sleep -Milliseconds 300
  }
}
function Menu($win, $item) {
  $m = Find-Name $win $EDIT 'ControlType.MenuItem'; if (-not $m) { return "no Edit menu" }
  $m.GetCurrentPattern([Windows.Automation.ExpandCollapsePattern]::Pattern).Expand(); Start-Sleep 1
  $e = Find-Name $AE::RootElement $item 'ControlType.MenuItem'; if (-not $e) { return "no menu item" }
  if (-not $e.Current.IsEnabled) { $m.GetCurrentPattern([Windows.Automation.ExpandCollapsePattern]::Pattern).Collapse(); return "disabled" }
  $e.GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern).Invoke(); return "invoked"
}
function Paint-Paste {
  $p = $null
  try {
    $p = Start-Process mspaint -PassThru; Start-Sleep 6
    $win = $AE::RootElement.FindFirst($TS::Children, (New-Object Windows.Automation.PropertyCondition($AE::ClassNameProperty, 'MSPaintApp')))
    if (-not $win) { return "Paint: no window" }
    $paste = Menu $win $PASTE; Start-Sleep 3
    $copy = Menu $win $COPY; Start-Sleep 2
    
    $mine = (Get-Process mspaint -EA SilentlyContinue | % Id) -join ','
    "Paint: paste=$paste copy=$copy paint-pids=$mine clipboard: " + (([CB]::Dump([NullString]::Value)) | ? { $_ -match 'owner|CF_DIB |CF_UNICODETEXT' }) -join ' / '
  } catch { "Paint: ERROR $_" }
  finally { Get-Process mspaint -EA SilentlyContinue | Stop-Process -Force -EA SilentlyContinue }
}

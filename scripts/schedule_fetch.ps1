param([string]$Action = "run")

$project = Resolve-Path "$PSScriptRoot\.."
$log = "$project\logs\fetch_news.log"
$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$null = New-Item -ItemType Directory -Path "$project\logs" -Force

if ($Action -eq "install") {
    $taskName = "Pusula-NewsFetch"
    $scriptPath = $MyInvocation.MyCommand.Path
    schtasks /Create /TN $taskName /XML @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger><StartBoundary>$(Get-Date -Format "yyyy-MM-dd")T08:00:00</StartBoundary><Enabled>true</Enabled><ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay></CalendarTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec><Command>powershell.exe</Command><Arguments>-NoProfile -ExecutionPolicy Bypass -File "$scriptPath" -Action run</Arguments></Exec>
  </Actions>
  <Settings><StartWhenAvailable>true</StartWhenAvailable><AllowStartOnDemand>true</AllowStartOnDemand></Settings>
</Task>
"@ /F *>$null
    Write-Output "[$date] Task Scheduler'a kaydedildi: $taskName (her gun 08:00)"
    exit
}

if ($Action -eq "remove") {
    Unregister-ScheduledTask -TaskName "Pusula-NewsFetch" -Confirm:$false -ErrorAction SilentlyContinue
    Write-Output "[$date] Task kaldirildi"
    exit
}

try {
    $env:PYTHONIOENCODING = "utf-8"
    $output = & python "$project\scripts\fetch_news.py" 2>&1
    "$date OK: $output" | Out-File -Append -Encoding utf8 $log
} catch {
    "$date HATA: $_" | Out-File -Append -Encoding utf8 $log
}

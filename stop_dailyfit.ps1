param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidPath = Join-Path $Root "data\server\dailyfit.pid"

$stopped = $false

if (Test-Path $PidPath) {
    $pidValue = (Get-Content $PidPath -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if ($pidValue -match "^\d+$") {
        $process = Get-Process -Id ([int]$pidValue) -ErrorAction SilentlyContinue
        if ($process) {
            $command = Get-CimInstance Win32_Process -Filter "ProcessId=$pidValue"
            if ($command.CommandLine -match "uvicorn" -and $command.CommandLine -match "backend\.app:app") {
                Stop-Process -Id ([int]$pidValue) -Force
                $stopped = $true
                Write-Host "Stopped DailyFit Agent PID $pidValue"
            }
        }
    }
    Remove-Item -LiteralPath $PidPath -Force -ErrorAction SilentlyContinue
}

$listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
foreach ($listener in $listeners) {
    $command = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
    if ($command.CommandLine -match "uvicorn" -and $command.CommandLine -match "backend\.app:app") {
        Stop-Process -Id $listener.OwningProcess -Force
        $stopped = $true
        Write-Host "Stopped DailyFit Agent PID $($listener.OwningProcess)"
    }
}

if (-not $stopped) {
    Write-Host "DailyFit Agent was not running on port $Port"
}

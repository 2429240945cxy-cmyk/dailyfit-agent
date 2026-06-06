param(
    [string]$Mode = "live",
    [int]$Port = 8000,
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ServerDir = Join-Path $Root "data\server"
$PidPath = Join-Path $ServerDir "dailyfit.pid"
$OutLogPath = Join-Path $ServerDir "uvicorn.out.log"
$ErrLogPath = Join-Path $ServerDir "uvicorn.err.log"

New-Item -ItemType Directory -Force -Path $ServerDir | Out-Null
Set-Location $Root

$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
    Select-Object -First 1

if ($existing) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($existing.OwningProcess)"
    if ($process.CommandLine -match "uvicorn" -and $process.CommandLine -match "backend\.app:app") {
        Write-Host "DailyFit Agent is already running at http://localhost:$Port"
        if ($OpenBrowser) {
            Start-Process "http://localhost:$Port"
        }
        exit 0
    }
    throw "Port $Port is already used by PID $($existing.OwningProcess): $($process.CommandLine)"
}

$python = (Get-Command python -ErrorAction Stop).Source
$env:DAILYFIT_MODE = $Mode
$arguments = @("-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "$Port")

$process = Start-Process `
    -WindowStyle Hidden `
    -FilePath $python `
    -ArgumentList $arguments `
    -WorkingDirectory $Root `
    -RedirectStandardOutput $OutLogPath `
    -RedirectStandardError $ErrLogPath `
    -PassThru

Set-Content -Path $PidPath -Value $process.Id -Encoding ascii
Start-Sleep -Seconds 3

$health = Invoke-WebRequest -UseBasicParsing "http://localhost:$Port/health" -TimeoutSec 10
Write-Host "DailyFit Agent started: http://localhost:$Port"
Write-Host $health.Content

if ($OpenBrowser) {
    Start-Process "http://localhost:$Port"
}

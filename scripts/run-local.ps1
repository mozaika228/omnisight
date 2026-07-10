#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick launcher for OmniSight local services

.DESCRIPTION
    Runs OmniSight services locally without Docker

.EXAMPLE
    .\run-local.ps1
#>

# Colors
$colors = @{
    Success = "Green"
    Info = "Cyan"
    Warning = "Yellow"
    Error = "Red"
}

function Print-Status {
    param([string]$Message, [string]$Type = "Info")
    $symbol = @{
        "Success" = "✅"
        "Info" = "ℹ️ "
        "Warning" = "⚠️ "
        "Error" = "❌"
    }
    Write-Host "$($symbol[$Type]) $Message" -ForegroundColor $colors[$Type]
}

Print-Status "OmniSight Local Development Setup" -Type Info
Print-Status "================================" -Type Info

# Check Python venv
if (Test-Path "venv\Scripts\Activate.ps1") {
    Print-Status "Virtual environment found" -Type Success
    . .\venv\Scripts\Activate.ps1
} else {
    Print-Status "Virtual environment NOT found. Run setup first:" -Type Error
    Print-Status "python -m venv venv" -Type Info
    Print-Status ".\venv\Scripts\Activate.ps1" -Type Info
    exit 1
}

# Check PostgreSQL
$pgCheck = psql -U omnisight -d omnisight -c "SELECT 1" 2>$null
if ($LASTEXITCODE -eq 0) {
    Print-Status "PostgreSQL is running" -Type Success
} else {
    Print-Status "PostgreSQL is NOT running" -Type Error
    Print-Status "Start PostgreSQL first (psql -U postgres)" -Type Warning
}

# Check Redis
$redisCheck = redis-cli ping 2>$null
if ($LASTEXITCODE -eq 0) {
    Print-Status "Redis is running" -Type Success
} else {
    Print-Status "Redis is NOT running" -Type Warning
    Print-Status "Start Redis in another terminal: redis-server" -Type Info
}

# Check Qdrant
try {
    $qdrantCheck = curl -s http://localhost:6333/health | ConvertFrom-Json
    if ($qdrantCheck.ok) {
        Print-Status "Qdrant is running" -Type Success
    }
} catch {
    Print-Status "Qdrant is NOT running" -Type Warning
    Print-Status "Start Qdrant in another terminal: qdrant.exe" -Type Info
}

Print-Status "Starting FastAPI backend..." -Type Info

# Check if main.py exists, if not create it
if (-not (Test-Path "apps\api\main.py")) {
    Print-Status "Creating stub API..." -Type Warning
    @"
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="OmniSight API", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/v1/videos")
async def list_videos():
    return {"videos": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"@ | Out-File "apps\api\main.py" -Encoding UTF8
    Print-Status "Created stub API in apps/api/main.py" -Type Info
}

Print-Status "🚀 Starting backend on http://localhost:8000" -Type Success
Print-Status "📝 API Docs: http://localhost:8000/docs" -Type Info
Print-Status "Press Ctrl+C to stop" -Type Info

uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

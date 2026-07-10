#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup script for OmniSight local development on Windows (without Docker)

.DESCRIPTION
    Installs and configures all dependencies for running OmniSight locally

.EXAMPLE
    .\setup-local-windows.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Colors for output
$colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
}

function Write-Status {
    param(
        [string]$Message,
        [string]$Status = "Info"
    )
    $color = $colors[$Status]
    if ($Status -eq "Success") { Write-Host "✅ $Message" -ForegroundColor $color }
    elseif ($Status -eq "Error") { Write-Host "❌ $Message" -ForegroundColor $color }
    elseif ($Status -eq "Warning") { Write-Host "⚠️  $Message" -ForegroundColor $color }
    else { Write-Host "ℹ️  $Message" -ForegroundColor $color }
}

# Check for required tools
Write-Host "`n🔍 Checking prerequisites...`n"

$checks = @(
    @{ cmd = "python"; name = "Python 3.10+" },
    @{ cmd = "node"; name = "Node.js 18+" },
    @{ cmd = "npm"; name = "npm" },
    @{ cmd = "git"; name = "Git" }
)

foreach ($check in $checks) {
    try {
        $version = & $check.cmd --version 2>$null
        Write-Status "$($check.name) found: $version" -Status Success
    }
    catch {
        Write-Status "$($check.name) NOT found. Please install from https://nodejs.org, https://www.python.org, etc." -Status Error
        exit 1
    }
}

# Check PostgreSQL
try {
    psql --version
    Write-Status "PostgreSQL found" -Status Success
}
catch {
    Write-Status "PostgreSQL NOT found. Install from https://www.postgresql.org/download/windows/" -Status Warning
    Write-Status "Continuing... (you'll need PostgreSQL later)" -Status Info
}

# Check Redis
try {
    redis-cli --version
    Write-Status "Redis found" -Status Success
}
catch {
    Write-Status "Redis NOT found. Install from WSL (wsl > sudo apt-get install redis-server) or https://github.com/microsoftarchive/redis/releases" -Status Warning
}

# Setup Python virtual environment
Write-Host "`n🐍 Setting up Python environment...`n"

if (Test-Path "venv") {
    Write-Status "Virtual environment already exists" -Status Info
} else {
    Write-Status "Creating virtual environment..." -Status Info
    python -m venv venv
    Write-Status "Virtual environment created" -Status Success
}

# Activate venv
Write-Status "Activating virtual environment..." -Status Info
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`n📦 Installing Python dependencies...`n"
Write-Status "Upgrading pip..." -Status Info
python -m pip install --upgrade pip setuptools wheel

# Install requirements
Write-Status "Installing requirements (this may take a few minutes)..." -Status Info
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Status "Python dependencies installed" -Status Success
} else {
    Write-Status "Failed to install Python dependencies" -Status Error
    exit 1
}

# Setup Node.js frontend
Write-Host "`n🎨 Setting up Node.js frontend...`n"

if (Test-Path "apps/web/node_modules") {
    Write-Status "Node modules already installed" -Status Info
} else {
    Write-Status "Installing Node dependencies (npm install)..." -Status Info
    Push-Location apps/web
    npm install
    Pop-Location
    Write-Status "Node dependencies installed" -Status Success
}

# Setup .env file
Write-Host "`n⚙️  Setting up environment variables...`n"

if (Test-Path ".env") {
    Write-Status ".env file already exists" -Status Info
} else {
    if (Test-Path ".env.example") {
        Write-Status "Creating .env from .env.example..." -Status Info
        Copy-Item .env.example .env
        Write-Status ".env created - please edit with your settings" -Status Success
    } else {
        Write-Status ".env.example not found" -Status Error
        exit 1
    }
}

# Create necessary directories
Write-Host "`n📁 Creating project structure...`n"

$dirs = @(
    "apps/api/routers",
    "apps/api/models",
    "apps/api/schemas",
    "apps/api/services",
    "services/detection/models",
    "services/transcription/models",
    "services/embeddings/models"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Status "Created directory: $dir" -Status Info
    }
}

Write-Host "`n✅ Setup complete!`n"

Write-Host "━" * 60
Write-Host "Next steps:"
Write-Host ""
Write-Host "1. Edit .env file with your settings"
Write-Host "2. Start services in separate terminals:"
Write-Host "   - PostgreSQL: psql -U postgres"
Write-Host "   - Redis: redis-server"
Write-Host "   - Qdrant: qdrant.exe (download from GitHub)"
Write-Host ""
Write-Host "3. Start development servers:"
Write-Host "   # Terminal 1: FastAPI backend"
Write-Host "   .\venv\Scripts\Activate.ps1"
Write-Host "   uvicorn apps.api.main:app --reload"
Write-Host ""
Write-Host "   # Terminal 2: Next.js frontend"
Write-Host "   cd apps/web"
Write-Host "   npm run dev"
Write-Host ""
Write-Host "4. Open http://localhost:3000 in your browser"
Write-Host ""
Write-Host "See LOCAL_SETUP.md for detailed instructions"
Write-Host "━" * 60

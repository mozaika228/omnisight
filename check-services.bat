@echo off
REM Windows batch script to check all OmniSight services

echo.
echo ===== OmniSight Service Status Check =====
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python is installed
) else (
    echo [FAIL] Python not found - https://www.python.org/downloads/
)

REM Check Node.js
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Node.js is installed
) else (
    echo [FAIL] Node.js not found - https://nodejs.org/
)

REM Check PostgreSQL
echo [3/5] Checking PostgreSQL...
psql -U omnisight -d omnisight -c "SELECT 1" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] PostgreSQL is running
) else (
    echo [WARN] PostgreSQL not running - start with: psql -U postgres
)

REM Check Redis
echo [4/5] Checking Redis...
redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Redis is running
) else (
    echo [WARN] Redis not running - start with: redis-server
)

REM Check Qdrant
echo [5/5] Checking Qdrant...
curl -s http://localhost:6333/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Qdrant is running
) else (
    echo [WARN] Qdrant not running - start with: qdrant.exe
)

echo.
echo ===== To start development =====
echo 1. Open 5 PowerShell windows
echo 2. Run in each:
echo    - Terminal 1: psql -U postgres
echo    - Terminal 2: redis-server
echo    - Terminal 3: qdrant.exe
echo    - Terminal 4: .\venv\Scripts\Activate.ps1; uvicorn apps.api.main:app --reload
echo    - Terminal 5: cd apps/web; npm run dev
echo 3. Open http://localhost:3000
echo.
pause

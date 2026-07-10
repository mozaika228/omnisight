# OmniSight Local Development Setup (без Docker)

Этот гайд показывает, как запустить OmniSight локально без Docker Compose.

## 📋 Требования

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Git

## 🚀 Установка на Windows

### 1. Установить зависимости

#### PostgreSQL
```powershell
# Скачать с https://www.postgresql.org/download/windows/
# Или через Chocolatey
choco install postgresql

# Проверить установку
psql --version
```

#### Redis
```powershell
# Через WSL2 (рекомендуется для Windows)
wsl
sudo apt-get install redis-server
redis-cli ping

# ИЛИ через Chocolatey
choco install redis-64

# ИЛИ скачать готовый бинарник
# https://github.com/microsoftarchive/redis/releases
```

#### Node.js
```powershell
choco install nodejs
node --version
npm --version
```

### 2. Создать базу данных PostgreSQL

```powershell
# Подключиться к PostgreSQL
psql -U postgres

# В PostgreSQL терминале:
CREATE DATABASE omnisight;
CREATE USER omnisight WITH PASSWORD 'omnisight_dev_password';
ALTER ROLE omnisight SET client_encoding TO 'utf8';
ALTER ROLE omnisight SET default_transaction_isolation TO 'read committed';
ALTER ROLE omnisight SET default_transaction_deferrable TO on;
ALTER ROLE omnisight SET default_transaction_readonly TO off;
GRANT ALL PRIVILEGES ON DATABASE omnisight TO omnisight;
\q
```

Проверить:
```powershell
psql -U omnisight -d omnisight -c "\dt"
```

### 3. Запустить Redis

```powershell
# Если установлен через Chocolatey
redis-server

# Проверить в другом терминале
redis-cli ping  # Должно вывести PONG
```

### 4. Запустить Qdrant (Vector Database)

```powershell
# Скачать с https://github.com/qdrant/qdrant/releases
# Выбрать qdrant-x86_64-pc-windows-msvc.zip

# Распаковать в папку, например C:\qdrant

cd C:\qdrant
.\qdrant.exe

# Проверить http://localhost:6333/health
# Должно вывести {"ok":true}
```

### 5. Запустить MinIO (Object Storage - опционально)

```powershell
# Скачать бинарник
# https://dl.min.io/server/minio/release/windows-amd64/minio.exe

# Создать папку для данных
mkdir C:\minio_data

# Запустить
$env:MINIO_ROOT_USER = "omnisight"
$env:MINIO_ROOT_PASSWORD = "omnisight_dev_password"
C:\path\to\minio.exe server C:\minio_data --console-address ":9001"

# Или используйте PowerShell скрипт (см. ниже)
```

---

## 🐍 Запустить Backend (FastAPI)

### 1. Создать виртуальное окружение

```powershell
cd c:\Users\Admin\Desktop\Danila IT-projects\omnisight

# Создать venv
python -m venv venv

# Активировать
.\venv\Scripts\Activate.ps1

# Если ошибка с политикой выполнения:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### 2. Установить зависимости

```powershell
# Убедитесь, что venv активирован
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Может занять время из-за ML моделей (torch, transformers)
```

### 3. Настроить .env

```powershell
# Скопировать шаблон
Copy-Item .env.example .env

# Отредактировать .env для локального запуска
# Основные изменения:
# DATABASE_URL=postgresql://omnisight:omnisight_dev_password@localhost:5432/omnisight
# REDIS_URL=redis://localhost:6379/0
# QDRANT_URL=http://localhost:6333
# DEVICE=cpu  (или cuda если есть NVIDIA GPU)
# ENABLE_GPU=false
```

### 4. Создать структуру приложения

```powershell
# Создать основные файлы приложения (см. ниже)
mkdir apps\api\routers
touch apps\api\main.py
touch apps\api\config.py
touch apps\api\database.py
```

### 5. Запустить сервер

```powershell
# Убедитесь, что venv активирован
.\venv\Scripts\Activate.ps1

# Запустить FastAPI
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен на http://localhost:8000

Swagger UI документация: http://localhost:8000/docs

---

## 🎨 Запустить Frontend (Next.js)

### 1. Установить зависимости

```powershell
cd apps\web
npm install
```

### 2. Запустить dev сервер

```powershell
npm run dev
```

Frontend будет доступен на http://localhost:3000

---

## 📊 Проверить все сервисы

```powershell
# PostgreSQL
psql -U omnisight -d omnisight -c "SELECT version();"

# Redis
redis-cli ping  # PONG

# Qdrant
curl http://localhost:6333/health  # {"ok":true}

# FastAPI
curl http://localhost:8000/health

# Next.js
# Открыть http://localhost:3000
```

---

## 🐛 Проблемы и решения

### PostgreSQL не запускается
```powershell
# Проверить статус сервиса
Get-Service postgresql*

# Запустить сервис
Start-Service postgresql-x64-14
```

### Redis connection refused
```powershell
# Убедитесь, что Redis запущен
redis-cli ping

# Если в WSL:
wsl
redis-server
```

### Qdrant не доступен
```powershell
# Убедитесь, что процесс запущен
Get-Process | grep qdrant

# Проверить порт
netstat -ano | findstr :6333
```

### Torch установка медленная/падает
```powershell
# Установить CPU версию (без CUDA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Или использовать pre-built wheels:
# https://pytorch.org/get-started/locally/
```

---

## 🚦 Структура запуска

Откройте **5 терминалов PowerShell**:

| # | Терминал | Команда | Порт |
|---|----------|---------|------|
| 1 | PostgreSQL | `psql -U postgres` (уже работает) | 5432 |
| 2 | Redis | `redis-server` | 6379 |
| 3 | Qdrant | `qdrant.exe` | 6333 |
| 4 | Backend | `uvicorn apps.api.main:app --reload` | 8000 |
| 5 | Frontend | `cd apps/web && npm run dev` | 3000 |

Затем откройте браузер на **http://localhost:3000**

---

## 🎯 Следующие шаги

После успешного запуска:

1. **Создать FastAPI endpoints** в `apps/api/main.py`
2. **Реализовать загрузку видео** (ingestion service)
3. **Добавить модели ML** (YOLO, Whisper, CLIP)
4. **Создать search API**
5. **Построить UI для поиска**

See [API.md](../docs/API.md) для полного API reference.


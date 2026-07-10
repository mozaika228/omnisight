# 🚀 OmniSight Quick Start (Без Docker)

## 📌 На Windows (самый простой способ)

### ✅ Шаг 1: Проверить Python

```powershell
python --version  # Должно быть 3.10+
```

Если нет → https://www.python.org/downloads/

---

### ✅ Шаг 2: Запустить Setup скрипт

```powershell
cd c:\Users\Admin\Desktop\Danila IT-projects\omnisight

# Запустить setup
.\scripts\setup-local-windows.ps1
```

Он автоматически:
- ✓ Создаст виртуальное окружение Python
- ✓ Установит все зависимости
- ✓ Установит Node.js пакеты
- ✓ Создаст .env файл

---

### ✅ Шаг 3: Установить базовые сервисы

Откройте **4 новых окна PowerShell**:

#### Окно 1: PostgreSQL
```powershell
# Если еще не установлен:
choco install postgresql

# Затем создать базу данных:
psql -U postgres -c "
CREATE DATABASE omnisight;
CREATE USER omnisight WITH PASSWORD 'omnisight_dev_password';
GRANT ALL PRIVILEGES ON DATABASE omnisight TO omnisight;
"

# Проверить
psql -U omnisight -d omnisight -c "SELECT version();"
```

#### Окно 2: Redis
```powershell
# Через WSL (рекомендуется):
wsl
sudo apt-get update
sudo apt-get install redis-server
redis-server

# ИЛИ через Chocolatey:
choco install redis-64
redis-server
```

#### Окно 3: Qdrant
```powershell
# Скачать бинарник с https://github.com/qdrant/qdrant/releases
# Выбрать qdrant-x86_64-pc-windows-msvc.zip

# Распаковать и запустить
cd C:\qdrant
.\qdrant.exe

# Проверить: http://localhost:6333/health
```

#### Окно 4: Backend (FastAPI)
```powershell
cd c:\Users\Admin\Desktop\Danila IT-projects\omnisight

# Активировать venv
.\venv\Scripts\Activate.ps1

# Запустить API
uvicorn apps.api.main:app --reload --port 8000
```

---

### ✅ Шаг 4: Запустить Frontend

Откройте **еще одно** окно PowerShell:

```powershell
cd c:\Users\Admin\Desktop\Danila IT-projects\omnisight\apps\web
npm run dev
```

---

### ✅ Шаг 5: Открыть в браузере

```
http://localhost:3000       ← Frontend
http://localhost:8000/docs  ← API Documentation
```

---

## 🎯 Готово!

Вы видите:
- 🟢 Frontend на http://localhost:3000
- 🟢 API на http://localhost:8000
- 🟢 API Docs (Swagger) на http://localhost:8000/docs

---

## 🔧 Если что-то не работает

### "Module not found: torch"
```powershell
# Установить PyTorch (может быть медленно)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### "PostgreSQL connection refused"
```powershell
# Запустить сервис
net start postgresql-x64-14
```

### "Redis connection refused"
```powershell
# Убедитесь, что Redis запущен в другом окне
redis-cli ping  # Должно вывести PONG
```

### "Cannot find qdrant.exe"
```powershell
# Скачать с GitHub
# https://github.com/qdrant/qdrant/releases
# Распаковать и запустить
```

---

## 📊 Структура запуска (5 окон)

| # | Окно | Что запустить | Проверка |
|---|------|---------------|----------|
| 1 | PostgreSQL | `psql -U postgres` | `psql -U omnisight -d omnisight -c "SELECT 1"` |
| 2 | Redis | `redis-server` | `redis-cli ping` → PONG |
| 3 | Qdrant | `qdrant.exe` | http://localhost:6333/health |
| 4 | Backend | `uvicorn apps.api.main:app --reload` | http://localhost:8000/health |
| 5 | Frontend | `npm run dev` (в apps/web) | http://localhost:3000 |

---

## 💡 Быстрые команды

```powershell
# Проверить все сервисы
python scripts/run-local.py

# Только Backend
.\venv\Scripts\Activate.ps1
uvicorn apps.api.main:app --reload

# Только Frontend
cd apps/web && npm run dev

# Очистить установку
rmdir /s venv
rmdir /s apps/web/node_modules
del .env
```

---

## 🎓 Что дальше?

После успешного запуска:

1. **Создать API endpoints** в `apps/api/main.py`
2. **Реализовать загрузку видео**
3. **Интегрировать YOLO** для детекции
4. **Добавить Whisper** для речи
5. **Подключить CLIP** для поиска
6. **Построить UI** для фронтенда

Смотрите [API.md](../docs/API.md) для полного API reference.

---

## 📞 Проблемы?

1. Проверьте [LOCAL_SETUP.md](../LOCAL_SETUP.md) для подробной инструкции
2. Откройте issue на GitHub
3. Запустите `python scripts/run-local.py` для диагностики


# OmniSight FastAPI Backend

## Structure

```
apps/api/
├── main.py           # Application entry point
├── config.py         # Configuration management
├── dependencies.py   # Dependency injection
├── security.py       # Authentication & authorization
├── routers/          # API route groups
│   ├── auth.py       # Authentication endpoints
│   ├── videos.py     # Video management
│   ├── search.py     # Search endpoints
│   ├── jobs.py       # Job management
│   └── health.py     # Health checks
├── models/           # Database models (SQLAlchemy)
├── schemas/          # Pydantic request/response schemas
├── services/         # Business logic
├── database/         # Database configuration
└── utils/            # Utility functions
```

## Starting Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Start server:
   ```bash
   uvicorn main:app --reload
   ```

API will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

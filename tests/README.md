# Testing

OmniSight includes comprehensive test suites for backend and frontend.

## Backend Tests

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=apps --cov=services

# Run specific test
pytest tests/test_api.py::test_upload_video
```

### Test Organization

```
tests/
├── unit/             # Unit tests
│   ├── test_models.py
│   ├── test_schemas.py
│   └── test_services.py
├── integration/      # Integration tests
│   ├── test_api.py
│   ├── test_search.py
│   └── test_processing.py
└── fixtures/         # Test fixtures
    ├── conftest.py
    └── sample_data.py
```

## Frontend Tests

### Running Tests

```bash
# Run all tests
npm run test

# Run with watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

## Performance Tests

```bash
# Backend performance tests
pytest tests/performance/

# Frontend lighthouse
npm run lighthouse
```

## Integration Tests

Full end-to-end tests:

```bash
# Start services
docker-compose up -d

# Run integration tests
pytest tests/integration/ -v

# Stop services
docker-compose down
```

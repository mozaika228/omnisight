# OmniSight

**AI-powered video understanding platform with semantic search capabilities.**

> Find moments in videos using natural language. "Show me all instances where someone is wearing a red jacket."

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)

## 🚀 Features

### MVP v1
- **Video Upload** - Support for MP4, MOV, WebM and other formats
- **Object Detection** - Real-time detection using YOLO v11
- **Speech Recognition** - Automatic transcription with Whisper
- **Visual Understanding** - Frame embeddings with CLIP
- **Semantic Search** - Natural language search across videos
- **Chat Interface** - Multi-turn conversational search

### Roadmap (Phases 2-7)
- Face detection & recognition
- OCR (Optical Character Recognition)
- Scene understanding
- Real-time video streaming
- Mobile applications
- Enterprise analytics

## 📊 Architecture

```
Frontend (Next.js)
    ↓
API Gateway (FastAPI)
    ↓
Microservices (Detection, Transcription, Embeddings, Search, LLM)
    ↓
Data Layer (PostgreSQL, Qdrant, Redis, S3/MinIO)
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design.

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js, React, TypeScript |
| **Backend** | FastAPI, Python 3.10+ |
| **AI/ML** | YOLO v11, Whisper, CLIP, Ollama |
| **Vector DB** | Qdrant |
| **SQL DB** | PostgreSQL |
| **Cache/Queue** | Redis, Celery |
| **Storage** | MinIO (local) / S3 (cloud) |
| **Container** | Docker, Kubernetes |

## ⚡ Quick Start

### Prerequisites
- Docker & Docker Compose 20.10+
- Python 3.10+ (for local development)
- 8GB+ RAM (16GB recommended for GPU)
- NVIDIA GPU (optional, but recommended for faster inference)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/omnisight/omnisight.git
cd omnisight
```

2. **Start services with Docker Compose**
```bash
docker-compose up -d
```

This starts:
- PostgreSQL on localhost:5432
- Qdrant on localhost:6333
- Redis on localhost:6379
- FastAPI on localhost:8000
- Next.js on localhost:3000

3. **Initialize database**
```bash
docker exec omnisight-api python -m scripts.init_db
```

4. **Upload and search a video**

Visit http://localhost:3000 and upload a video file (MP4, MOV, etc.)

Wait for processing (about 2-3x video duration), then try searching:
```
"Person wearing red jacket"
"Someone entering the building"
"Car in the parking lot"
```

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and component design
- **[API.md](docs/API.md)** - REST API reference and examples
- **[AI_PIPELINE.md](docs/AI_PIPELINE.md)** - Machine learning pipeline details
- **[DATABASE.md](docs/DATABASE.md)** - PostgreSQL and Qdrant schema
- **[ROADMAP.md](docs/ROADMAP.md)** - Product roadmap and milestones

## 🔧 Project Structure

```
omnisight/
├── apps/
│   ├── web/           # Next.js frontend
│   └── api/           # FastAPI backend
├── services/          # Microservices
│   ├── ingestion/     # Video upload & frame extraction
│   ├── detection/     # YOLO object detection
│   ├── transcription/ # Whisper speech recognition
│   ├── embeddings/    # CLIP visual embeddings
│   ├── llm/          # LLM integration
│   ├── search/       # Semantic search
│   └── indexing/     # Data indexing pipeline
├── packages/          # Shared code
│   ├── shared/       # Common utilities
│   └── sdk/          # Client SDKs
├── infra/            # Infrastructure as Code
├── docker/           # Docker configurations
├── k8s/              # Kubernetes manifests
├── docs/             # Documentation
└── tests/            # Test suites
```

## 🚀 Getting Started with Development

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env

# Run migrations
python -m scripts.migrate

# Start development server
uvicorn apps.api.main:app --reload
```

### Frontend Setup

```bash
# Install dependencies
cd apps/web
npm install

# Start dev server
npm run dev
```

### Running Tests

```bash
# Backend tests
pytest tests/

# Frontend tests
cd apps/web && npm run test

# Integration tests
pytest tests/integration/
```

## 🐳 Docker

### Build Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build api
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
```

## 🔍 Example: Search Query

### Natural Language Query
```
"Show me all moments where a person is wearing a red jacket"
```

### What Happens Behind the Scenes

1. **Parse Query** - LLM understands intent (find people + red jacket)
2. **Generate Embedding** - Convert query to vector
3. **Search Qdrant** - Find similar frames (cosine similarity)
4. **Filter Results** - Keep frames with person detection (YOLO)
5. **Filter Color** - Keep frames with red clothing (heuristic)
6. **Rank & Return** - Sort by relevance, return timestamps
7. **Synthesize Response** - Generate human-readable answer

### API Request

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "person in red jacket",
        "video_ids": ["video-uuid"],
        "limit": 10
    },
    headers={"Authorization": f"Bearer {token}"}
)

results = response.json()["data"]["results"]
# [
#   {
#     "timestamp_seconds": 35.2,
#     "video_id": "video-uuid",
#     "confidence": 0.92,
#     "frame_url": "..."
#   },
#   ...
# ]
```

## 🔐 Security

- JWT authentication & refresh tokens
- API key support for service-to-service
- Rate limiting per user
- CORS protection
- Data encryption (at rest & in transit)
- PII detection & redaction (optional)

See [ARCHITECTURE.md](docs/ARCHITECTURE.md#security-architecture) for details.

## 📈 Performance

### Processing Speed (GPU)
- **Frame Extraction:** 30 fps (FFmpeg)
- **Object Detection:** 20 fps (YOLO v11-small)
- **Embeddings:** 40 fps (CLIP)
- **Full Pipeline:** ~1.5-2x video duration

### Search Latency
- **Query Embedding:** <10ms
- **Vector Search:** <100ms
- **Ranking & Filtering:** <50ms
- **Total:** <200ms P99

### Scalability
- Horizontal scaling with Kubernetes
- Auto-scaling workers based on queue depth
- Multi-GPU support
- Database read replicas

## 📊 Monitoring & Logging

- **Prometheus** metrics for performance
- **Grafana** dashboards
- **Elasticsearch/Kibana** for log analysis
- **Sentry** for error tracking
- **Jaeger** for distributed tracing

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Quality

```bash
# Format code
black . && isort .

# Lint
flake8 . && pylint .

# Type checking
mypy .

# Tests
pytest
```

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙋 Support

- **Issues:** [GitHub Issues](https://github.com/omnisight/omnisight/issues)
- **Discussions:** [GitHub Discussions](https://github.com/omnisight/omnisight/discussions)
- **Email:** support@omnisight.dev

## 🗺️ Roadmap

See [ROADMAP.md](docs/ROADMAP.md) for detailed development phases and timelines.

## 🌟 Acknowledgments

Built with:
- [YOLO](https://github.com/ultralytics/ultralytics) - Object detection
- [Whisper](https://github.com/openai/whisper) - Speech recognition
- [CLIP](https://github.com/openai/CLIP) - Vision-language model
- [Qdrant](https://qdrant.tech/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python framework
- [Next.js](https://nextjs.org/) - React framework
- And many other open-source projects

---

**OmniSight** - Making video understanding accessible to everyone.


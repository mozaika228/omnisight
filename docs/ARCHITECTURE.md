# OmniSight Architecture

## System Overview

OmniSight is a modular, distributed video understanding platform that combines multiple AI models and services to provide semantic video search and analysis capabilities.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Next.js Web Interface (React + TypeScript)                 │   │
│  │  - Video Upload                                            │   │
│  │  - Search Interface                                        │   │
│  │  - Results Visualization                                  │   │
│  │  - Analytics Dashboard                                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway                                  │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  FastAPI (Python) - REST API + WebSocket                   │   │
│  │  - Authentication & Authorization (JWT)                   │   │
│  │  - Request Validation & Rate Limiting                    │   │
│  │  - Error Handling & Logging                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
        ↓           ↓           ↓           ↓           ↓
   ┌────────────────────────────────────────────────────────┐
   │          Task Queue (Celery + Redis)                  │
   │  - Async Job Scheduling                              │
   │  - Job Status Tracking                               │
   │  - Dead Letter Queue                                 │
   └────────────────────────────────────────────────────────┘
        ↓           ↓           ↓           ↓           ↓
   ┌─────────────────────────────────────────────────────────────────┐
   │                 Microservices Layer                              │
   ├─────────────────────────────────────────────────────────────────┤
   │                                                                   │
   │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
   │  │   Ingestion      │  │   Detection      │  │ Transcription│  │
   │  │   Service        │  │   Service        │  │  Service     │  │
   │  │                  │  │  (YOLO v8/v11)   │  │  (Whisper)   │  │
   │  │ - Download video │  │  - Extract       │  │  - Extract   │  │
   │  │ - Validate file  │  │    bounding      │  │    audio     │  │
   │  │ - Store raw      │  │    boxes         │  │  - Recognize │  │
   │  │ - Extract frames │  │  - Track objects │  │    speech    │  │
   │  │   (FFmpeg)       │  │                  │  │              │  │
   │  └──────────────────┘  └──────────────────┘  └──────────────┘  │
   │                                                                   │
   │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
   │  │   Embeddings     │  │   Indexing       │  │   Search     │  │
   │  │   Service        │  │   Service        │  │   Service    │  │
   │  │  (CLIP/SigLIP)   │  │                  │  │              │  │
   │  │                  │  │ - Normalize data │  │ - Semantic   │  │
   │  │ - Generate frame │  │ - Create indexes │  │   search     │  │
   │  │   embeddings     │  │ - Batch insert   │  │ - Ranking    │  │
   │  │ - Embed queries  │  │   to vector DB   │  │ - Filtering  │  │
   │  │ - Normalize      │  │                  │  │              │  │
   │  └──────────────────┘  └──────────────────┘  └──────────────┘  │
   │                                                                   │
   │  ┌──────────────────┐  ┌──────────────────────────────────────┐ │
   │  │    LLM Service   │  │        Chat Service                  │ │
   │  │                  │  │  (Uses all above services)           │ │
   │  │ - Query parsing  │  │  - Natural language understanding   │ │
   │  │ - Context        │  │  - Multi-turn conversation          │ │
   │  │   generation     │  │  - Result synthesis                 │ │
   │  │ - Result ranking │  │                                      │ │
   │  │ (Ollama/vLLM)    │  │                                      │ │
   │  └──────────────────┘  └──────────────────────────────────────┘ │
   │                                                                   │
   └─────────────────────────────────────────────────────────────────┘
        ↓           ↓           ↓           ↓           ↓
   ┌─────────────────────────────────────────────────────────────────┐
   │                  Data Storage Layer                              │
   ├─────────────────────────────────────────────────────────────────┤
   │                                                                   │
   │  ┌─────────────────────────────────────────────────────────┐   │
   │  │  Vector Database (Qdrant)                              │   │
   │  │  - Frame embeddings                                   │   │
   │  │  - Metadata indexed                                  │   │
   │  │  - Semantic search capabilities                      │   │
   │  └─────────────────────────────────────────────────────────┘   │
   │                                                                   │
   │  ┌─────────────────────────────────────────────────────────┐   │
   │  │  Relational DB (PostgreSQL)                           │   │
   │  │  - Video metadata                                     │   │
   │  │  - Processing jobs                                   │   │
   │  │  - User sessions                                     │   │
   │  │  - Search history                                    │   │
   │  └─────────────────────────────────────────────────────────┘   │
   │                                                                   │
   │  ┌─────────────────────────────────────────────────────────┐   │
   │  │  Object Storage (MinIO / S3)                          │   │
   │  │  - Raw video files                                    │   │
   │  │  - Extracted frames                                  │   │
   │  │  - Processing artifacts                             │   │
   │  └─────────────────────────────────────────────────────────┘   │
   │                                                                   │
   │  ┌─────────────────────────────────────────────────────────┐   │
   │  │  Cache & Queue (Redis)                                │   │
   │  │  - Session cache                                      │   │
   │  │  - Job queue                                          │   │
   │  │  - Rate limiting                                      │   │
   │  │  - Real-time notifications                           │   │
   │  └─────────────────────────────────────────────────────────┘   │
   │                                                                   │
   └─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Gateway (FastAPI)

**Responsibilities:**
- HTTP/REST endpoint for all client requests
- WebSocket for real-time job updates
- JWT authentication & authorization
- Request validation & rate limiting
- Error handling & structured logging

**Key Endpoints:**
- `POST /api/v1/videos/upload` - Upload video
- `POST /api/v1/search` - Semantic search query
- `GET /api/v1/jobs/{job_id}` - Get job status
- `WS /api/v1/stream` - WebSocket for live updates

### 2. Ingestion Service

**Responsibilities:**
- Receive and validate video uploads
- Store videos in object storage
- Extract frames at configurable FPS (default: 1 FPS)
- Validate video format and duration
- Emit events to task queue

**Input:** Video file (MP4, MOV, WebM, etc.)
**Output:** Extracted frames stored in S3/MinIO, metadata in PostgreSQL

### 3. Detection Service

**Responsibilities:**
- Run YOLO v11 for object detection
- Generate bounding boxes for each frame
- Track objects across frames
- Store detection results
- Handle GPU resource management

**Input:** Extracted frames
**Output:** Detection metadata (objects, confidence, boxes) → PostgreSQL

### 4. Transcription Service

**Responsibilities:**
- Extract audio from video
- Run Whisper model for speech-to-text
- Generate timestamps for each segment
- Store transcription results
- Optional translation

**Input:** Original video file
**Output:** Transcription text + timestamps → PostgreSQL

### 5. Embeddings Service

**Responsibilities:**
- Generate CLIP/SigLIP embeddings for frames
- Normalize embeddings to unit vectors
- Batch processing for efficiency
- Optional text embedding for queries

**Input:** Frames + metadata
**Output:** Vector embeddings → Qdrant

### 6. Indexing Service

**Responsibilities:**
- Coordinate data from other services
- Create composite indexes
- Normalize and clean data before storing
- Batch insert to vector DB
- Handle retries and failures

**Input:** Data from Detection, Transcription, Embeddings
**Output:** Indexed data in Qdrant + PostgreSQL

### 7. Search Service

**Responsibilities:**
- Accept semantic search queries
- Convert text queries to embeddings
- Query Qdrant with similarity threshold
- Rank and filter results
- Return matched timestamps and metadata

**Input:** Search query (natural language)
**Output:** Ranked list of matching frames with timestamps

### 8. LLM Service

**Responsibilities:**
- Parse user queries for intent
- Generate search parameters
- Synthesize results
- Generate explanations
- Handle context and memory

**Input:** Natural language query
**Output:** Interpreted parameters + response text

### 9. Chat Service

**Responsibilities:**
- Manage conversation state
- Call other services in sequence
- Aggregate results
- Generate human-readable responses
- Handle multi-turn interactions

**Input:** User message
**Output:** Natural language response with timestamps

## Data Flow

### Video Processing Pipeline

```
User Upload
    ↓
[Ingestion] → Store video + Extract frames
    ↓
[Detection] → YOLO analysis (bounding boxes, objects)
[Transcription] → Whisper (speech-to-text)
    ↓
[Embeddings] → CLIP embeddings for frames
    ↓
[Indexing] → Normalize, create indexes
    ↓
[Search Ready] → Qdrant + PostgreSQL populated
```

### Search Query Pipeline

```
User Query: "Show moments with person + red mug"
    ↓
[LLM Service] → Parse intent, extract parameters
    ↓
[Embeddings] → Generate embedding for query
    ↓
[Search Service] → Query Qdrant (semantic similarity)
    ↓
[Ranking] → Filter by detections (person + red object)
    ↓
[Results] → Return matched timestamps + clips
```

## Service Communication

### Synchronous (REST/HTTP)
- API Gateway ↔ Search Service
- API Gateway ↔ Chat Service
- Chat Service → Search Service

### Asynchronous (Celery + Redis)
- API Gateway → Task Queue
- Task Queue → Ingestion Service
- Task Queue → Detection Service
- Task Queue → Transcription Service
- Task Queue → Embeddings Service
- Task Queue → Indexing Service

### Real-time (WebSocket)
- API Gateway ↔ Frontend
- Job status updates via `/api/v1/stream`

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| API | FastAPI | Fast, async, built-in validation |
| Frontend | Next.js + React | Modern, SSR, great DX |
| AI Models | PyTorch + Ultralytics + OpenAI | Industry standard, proven |
| Vector DB | Qdrant | Fast, scalable, production-ready |
| SQL DB | PostgreSQL | Reliable, full-featured |
| Cache/Queue | Redis | High performance, multi-purpose |
| Object Storage | MinIO (local) / S3 (cloud) | Scalable, standard API |
| Task Queue | Celery | Distributed, reliable, mature |
| Async Tasks | Dramatiq (alternative) | Simpler than Celery, faster |
| Containerization | Docker | Reproducible environments |
| Orchestration | Kubernetes | Production scaling |

## Scalability Considerations

### Horizontal Scaling
- Stateless API Gateway (scale up/down freely)
- Worker services (multiple instances per service)
- Load balancing with nginx/Traefik
- Auto-scaling based on queue depth

### Vertical Scaling
- GPU allocation for Detection/Transcription/Embeddings
- Memory tuning for batch processing
- Connection pooling for databases

### Data Scaling
- Qdrant horizontal scaling with sharding
- PostgreSQL read replicas
- S3 partitioning by date/user
- Vector DB indexing optimization

## Deployment Environments

### Local Development
```
Docker Compose: API, all services, PostgreSQL, Qdrant, Redis
```

### Staging
```
Kubernetes: Single node, small resource limits
```

### Production
```
Kubernetes: Multi-node cluster
- API tier (3+ replicas)
- Worker tier (auto-scaling 1-10 replicas per service)
- Database tier (managed PostgreSQL)
- Vector DB tier (Qdrant cloud or managed K8s)
```

## Security Architecture

### Authentication
- JWT tokens with refresh rotation
- API key support for service-to-service

### Authorization
- Role-based access control (RBAC)
- Video ownership verification
- Rate limiting per user/API key

### Data Protection
- Encryption at rest (S3, PostgreSQL)
- Encryption in transit (TLS/SSL)
- PII detection and redaction (optional)

### Monitoring & Logging
- Structured JSON logging
- Prometheus metrics
- Grafana dashboards
- ELK stack integration (optional)

## Error Handling & Resilience

- Retry logic with exponential backoff
- Dead letter queues for failed jobs
- Circuit breakers for external services
- Graceful degradation
- Comprehensive logging at each step


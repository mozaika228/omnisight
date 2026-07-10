# Database Architecture

## Overview

OmniSight uses a polyglot persistence approach:

1. **PostgreSQL** - Relational data (metadata, users, jobs)
2. **Qdrant** - Vector database (embeddings, semantic search)
3. **Redis** - Cache and job queue
4. **S3/MinIO** - Object storage (videos, frames)

## PostgreSQL Schema

### Users Table

```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  api_key VARCHAR(255) UNIQUE,
  api_key_hash VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP,
  subscription_tier VARCHAR(50) DEFAULT 'free'  -- free, pro, enterprise
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key_hash ON users(api_key_hash);
```

### Videos Table

```sql
CREATE TABLE videos (
  video_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  title VARCHAR(255),
  description TEXT,
  status VARCHAR(50) DEFAULT 'uploading',  -- uploading, processing, completed, failed
  
  -- File Info
  original_filename VARCHAR(255),
  file_size_bytes BIGINT,
  s3_key VARCHAR(500),
  
  -- Video Properties
  duration_seconds INTEGER,
  resolution VARCHAR(20),  -- 1920x1080
  fps FLOAT,
  codec VARCHAR(20),
  audio_codec VARCHAR(20),
  
  -- Frame Info
  frame_count INTEGER,
  frames_extracted INTEGER DEFAULT 0,
  frames_per_second FLOAT DEFAULT 1.0,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processing_started_at TIMESTAMP,
  processing_completed_at TIMESTAMP,
  
  -- Metadata
  tags TEXT[],  -- Array of tags
  custom_metadata JSONB,
  
  -- Statistics
  total_detected_objects INTEGER DEFAULT 0,
  detection_confidence_avg FLOAT
);

CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created_at ON videos(created_at);
CREATE INDEX idx_videos_user_status ON videos(user_id, status);
```

### Jobs Table

```sql
CREATE TABLE jobs (
  job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(video_id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  
  -- Job Status
  status VARCHAR(50) DEFAULT 'queued',  -- queued, ingestion, detection, transcription, embeddings, indexing, completed, failed
  progress FLOAT DEFAULT 0.0,  -- 0.0 to 1.0
  error_message TEXT,
  
  -- Stages
  ingestion_status VARCHAR(50),
  ingestion_started_at TIMESTAMP,
  ingestion_completed_at TIMESTAMP,
  
  detection_status VARCHAR(50),
  detection_started_at TIMESTAMP,
  detection_completed_at TIMESTAMP,
  
  transcription_status VARCHAR(50),
  transcription_started_at TIMESTAMP,
  transcription_completed_at TIMESTAMP,
  
  embeddings_status VARCHAR(50),
  embeddings_started_at TIMESTAMP,
  embeddings_completed_at TIMESTAMP,
  
  indexing_status VARCHAR(50),
  indexing_started_at TIMESTAMP,
  indexing_completed_at TIMESTAMP,
  
  -- Timing
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP,
  
  -- Metadata
  estimated_duration_seconds INTEGER,
  worker_id VARCHAR(255)  -- Which worker is processing this
);

CREATE INDEX idx_jobs_video_id ON jobs(video_id);
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
```

### Frames Table

```sql
CREATE TABLE frames (
  frame_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(video_id) ON DELETE CASCADE,
  
  -- Position
  frame_index INTEGER NOT NULL,
  timestamp_seconds FLOAT NOT NULL,
  
  -- File
  s3_key VARCHAR(500),  -- Path to frame image in S3/MinIO
  image_hash VARCHAR(64),  -- SHA256 for deduplication
  
  -- Properties
  width INTEGER,
  height INTEGER,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  extracted_at TIMESTAMP,
  
  UNIQUE(video_id, frame_index)
);

CREATE INDEX idx_frames_video_id ON frames(video_id);
CREATE INDEX idx_frames_timestamp ON frames(video_id, timestamp_seconds);
```

### Detections Table

```sql
CREATE TABLE detections (
  detection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  frame_id UUID NOT NULL REFERENCES frames(frame_id) ON DELETE CASCADE,
  video_id UUID NOT NULL REFERENCES videos(video_id) ON DELETE CASCADE,
  
  -- Detection Info
  object_class VARCHAR(100) NOT NULL,  -- person, car, dog, etc.
  confidence FLOAT NOT NULL,
  
  -- Bounding Box (normalized 0-1)
  bbox_x1 FLOAT,
  bbox_y1 FLOAT,
  bbox_x2 FLOAT,
  bbox_y2 FLOAT,
  
  -- Metadata
  tracking_id VARCHAR(100),  -- Track same object across frames
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_detections_frame_id ON detections(frame_id);
CREATE INDEX idx_detections_video_id ON detections(video_id);
CREATE INDEX idx_detections_object_class ON detections(object_class);
CREATE INDEX idx_detections_confidence ON detections(confidence);
CREATE INDEX idx_detections_tracking_id ON detections(tracking_id);
```

### Transcriptions Table

```sql
CREATE TABLE transcriptions (
  transcription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(video_id) ON DELETE CASCADE,
  
  -- Full text
  text TEXT NOT NULL,
  language VARCHAR(10) DEFAULT 'en',
  
  -- Quality
  confidence FLOAT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transcriptions_video_id ON transcriptions(video_id);
```

### Transcription Segments Table

```sql
CREATE TABLE transcription_segments (
  segment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  transcription_id UUID NOT NULL REFERENCES transcriptions(transcription_id) ON DELETE CASCADE,
  video_id UUID NOT NULL REFERENCES videos(video_id) ON DELETE CASCADE,
  
  -- Segment Data
  segment_index INTEGER,
  start_seconds FLOAT NOT NULL,
  end_seconds FLOAT NOT NULL,
  text TEXT NOT NULL,
  confidence FLOAT,
  
  -- Speaker (optional)
  speaker_id VARCHAR(100),
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_segments_video_id ON transcription_segments(video_id);
CREATE INDEX idx_segments_timestamp ON transcription_segments(video_id, start_seconds);
```

### Searches Table

```sql
CREATE TABLE searches (
  search_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  
  -- Query
  query_text VARCHAR(1000) NOT NULL,
  video_ids UUID[],  -- Which videos searched
  
  -- Results
  total_results INTEGER,
  processing_time_ms INTEGER,
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_searches_user_id ON searches(user_id);
CREATE INDEX idx_searches_created_at ON searches(created_at);
```

### Search Results Table

```sql
CREATE TABLE search_results (
  result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  search_id UUID NOT NULL REFERENCES searches(search_id) ON DELETE CASCADE,
  frame_id UUID NOT NULL REFERENCES frames(frame_id) ON DELETE CASCADE,
  video_id UUID NOT NULL REFERENCES videos(video_id) ON DELETE CASCADE,
  
  -- Ranking
  rank INTEGER,
  relevance_score FLOAT NOT NULL,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_results_search_id ON search_results(search_id);
CREATE INDEX idx_search_results_frame_id ON search_results(frame_id);
```

## Qdrant Vector Database Schema

### Collection: frame_embeddings

**Purpose:** Store CLIP embeddings for all frames

**Configuration:**
```json
{
  "name": "frame_embeddings",
  "vectors": {
    "size": 512,
    "distance": "Cosine"
  },
  "payload_schema": {
    "frame_id": {
      "type": "keyword",
      "index": true
    },
    "video_id": {
      "type": "keyword",
      "index": true
    },
    "timestamp_seconds": {
      "type": "float",
      "index": true
    },
    "object_classes": {
      "type": "keyword",
      "index": true
    },
    "object_confidence": {
      "type": "float",
      "index": true
    },
    "has_person": {
      "type": "bool",
      "index": true
    },
    "has_vehicle": {
      "type": "bool",
      "index": true
    },
    "transcription_text": {
      "type": "text",
      "index": true
    }
  },
  "hnsw_config": {
    "m": 16,
    "ef_construct": 200,
    "ef": 200,
    "max_indexing_threads": 4
  }
}
```

**Vector Structure:**
```json
{
  "id": "frame_id_uuid",
  "vector": [0.1, -0.2, 0.3, ...],  // 512-dim CLIP embedding
  "payload": {
    "frame_id": "uuid",
    "video_id": "uuid",
    "timestamp_seconds": 35.2,
    "object_classes": ["person", "car"],
    "object_confidence": 0.92,
    "has_person": true,
    "has_vehicle": true,
    "transcription_text": "Person entering the car"
  }
}
```

### Collection: query_cache

**Purpose:** Cache query embeddings for performance

**Similar structure**, but smaller collection with TTL

## Redis Schema

### Keys

```
# Session cache
session:{session_id} = JSON(user_data)  # TTL: 24 hours

# Job queue
celery:queue:detection = [job_id1, job_id2, ...]
celery:queue:transcription = [job_id3, job_id4, ...]

# Rate limiting
rate_limit:{user_id}:uploads = count  # TTL: 1 hour
rate_limit:{user_id}:searches = count  # TTL: 1 hour

# Cache
cache:video:{video_id} = JSON(video_data)  # TTL: 1 hour
cache:search:{query_hash} = JSON(results)  # TTL: 24 hours

# Locks
lock:video:{video_id}:processing = True  # TTL: 5 minutes
```

## Data Relationships

```
users
  ├── videos (1:N)
  │   ├── jobs (1:N)
  │   ├── frames (1:N)
  │   │   ├── detections (1:N)
  │   │   └── search_results (1:N)
  │   ├── transcriptions (1:N)
  │   │   └── transcription_segments (1:N)
  │   └── searches (1:N) [via search table]
  └── searches (1:N)
      └── search_results (1:N)

[Qdrant]
  frame_embeddings (vectors with payload)
    ├── frame_id
    ├── video_id
    ├── timestamp_seconds
    └── metadata
```

## Retention Policies

### Hot Data (Last 30 days)
- Cached in Redis
- Full data in PostgreSQL & Qdrant
- Accessible for real-time queries

### Warm Data (30 days - 1 year)
- Removed from Redis cache
- Available in PostgreSQL & Qdrant
- Slower queries acceptable

### Cold Data (1+ years)
- Archived to S3 Glacier
- PostgreSQL: soft-delete or archive table
- Qdrant: can be removed to save space

## Backup Strategy

### PostgreSQL
```bash
# Daily full backup
pg_dump -h localhost -U postgres omnisight > backup_$(date +%Y%m%d).sql

# WAL archiving for point-in-time recovery
```

### Qdrant
```bash
# Daily snapshot
curl -X POST http://localhost:6333/snapshots
```

### S3/MinIO
```bash
# Versioning enabled
# Cross-region replication for disaster recovery
```

## Performance Optimization

### Indexes
- Video queries: `(user_id, status, created_at)`
- Frame queries: `(video_id, timestamp_seconds)`
- Detection queries: `(video_id, object_class, confidence)`

### Partitioning (for large deployments)
```sql
-- Partition videos by date
CREATE TABLE videos_2024_q1 PARTITION OF videos
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

### Query Optimization
- Use materialized views for aggregations
- Batch inserts (1000 rows at a time)
- Connection pooling (PgBouncer)

## Monitoring

### Key Metrics
- Query response time (p95, p99)
- Vector DB search latency
- Cache hit rate
- Disk space usage
- Index fragmentation


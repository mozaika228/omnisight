# OmniSight API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

## Response Format

All responses follow a standard format:

**Success (200, 201, 202):**
```json
{
  "success": true,
  "data": { /* response data */ },
  "timestamp": "2024-07-10T12:00:00Z"
}
```

**Error (4xx, 5xx):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Description of the error",
    "details": { /* optional additional info */ }
  },
  "timestamp": "2024-07-10T12:00:00Z"
}
```

## Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2024-07-10T12:00:00Z"
  }
}
```

#### POST /auth/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "expires_in": 3600,
    "user": {
      "user_id": "uuid",
      "email": "user@example.com",
      "name": "John Doe"
    }
  }
}
```

#### POST /auth/refresh
Refresh expired access token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...",
    "expires_in": 3600
  }
}
```

---

### Video Management

#### POST /videos/upload
Upload a video file for processing.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Max file size: 5GB

**Form Data:**
```
video: <file>  # Video file (MP4, MOV, WebM, etc.)
title: "My Video"  # Optional
description: "Video description"  # Optional
tags: "tag1,tag2"  # Optional
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "video_id": "uuid",
    "title": "My Video",
    "status": "uploading",
    "job_id": "uuid",
    "created_at": "2024-07-10T12:00:00Z",
    "estimated_processing_time": 120
  }
}
```

**Error Responses:**
- 400: Invalid file format
- 413: File too large
- 429: Rate limit exceeded (max 10 videos/hour)

#### GET /videos
List all uploaded videos.

**Query Parameters:**
```
skip: 0  # Pagination offset
limit: 20  # Items per page (max 100)
status: "completed"  # Filter by status (processing, completed, failed)
sort_by: "created_at"  # Sort field
sort_order: "desc"  # asc or desc
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "videos": [
      {
        "video_id": "uuid",
        "title": "My Video",
        "status": "completed",
        "duration_seconds": 120,
        "frame_count": 120,
        "created_at": "2024-07-10T12:00:00Z",
        "size_bytes": 104857600
      }
    ],
    "total": 5,
    "skip": 0,
    "limit": 20
  }
}
```

#### GET /videos/{video_id}
Get details of a specific video.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "video_id": "uuid",
    "title": "My Video",
    "description": "Video description",
    "status": "completed",
    "duration_seconds": 120,
    "frame_count": 120,
    "resolution": "1920x1080",
    "fps": 30,
    "codec": "h264",
    "size_bytes": 104857600,
    "created_at": "2024-07-10T12:00:00Z",
    "processing_started_at": "2024-07-10T12:05:00Z",
    "processing_completed_at": "2024-07-10T12:08:00Z",
    "transcription": {
      "text": "Full transcription...",
      "language": "en",
      "segments": [
        {
          "start_time": 0,
          "end_time": 5,
          "text": "Hello world"
        }
      ]
    },
    "detected_objects": {
      "person": 45,
      "car": 12,
      "dog": 3
    },
    "tags": ["tag1", "tag2"]
  }
}
```

#### DELETE /videos/{video_id}
Delete a video and all associated data.

**Response (204):** No content

**Note:** This is irreversible. All embeddings, detections, and stored files will be deleted.

---

### Search

#### POST /search
Perform semantic search across videos.

**Request Body:**
```json
{
  "query": "Person wearing red jacket",
  "video_ids": ["uuid1", "uuid2"],  # Optional: search specific videos
  "confidence_threshold": 0.6,  # Optional: filter detection confidence
  "limit": 10,  # Results to return
  "offset": 0,  # Pagination offset
  "time_range": {
    "start_seconds": 0,
    "end_seconds": 120
  }  # Optional: search within time range
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "query": "Person wearing red jacket",
    "results": [
      {
        "video_id": "uuid",
        "video_title": "My Video",
        "timestamp_seconds": 35.2,
        "confidence": 0.92,
        "frame_url": "https://cdn.example.com/frame_123.jpg",
        "detected_objects": [
          {
            "class": "person",
            "confidence": 0.95,
            "bbox": [100, 200, 150, 400]
          },
          {
            "class": "jacket",
            "confidence": 0.88,
            "bbox": [105, 210, 145, 350]
          }
        ],
        "nearby_text": "Person enters the room"
      }
    ],
    "total": 1,
    "processing_time_ms": 245
  }
}
```

#### POST /search/advanced
Advanced search with filters and multiple conditions.

**Request Body:**
```json
{
  "queries": [
    {
      "type": "visual",
      "text": "person"
    },
    {
      "type": "text",
      "text": "entering the building"
    }
  ],
  "logic": "AND",  # AND, OR
  "video_ids": ["uuid1"],
  "time_range": {
    "start_seconds": 0,
    "end_seconds": 300
  },
  "filters": {
    "confidence_min": 0.7,
    "object_classes": ["person", "car"]
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "results": [ /* same as POST /search */ ],
    "total": 5,
    "processing_time_ms": 412
  }
}
```

#### POST /search/frame
Get detailed information about a specific frame.

**Request Body:**
```json
{
  "video_id": "uuid",
  "timestamp_seconds": 35.2
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "frame_index": 35,
    "timestamp_seconds": 35.2,
    "frame_url": "https://cdn.example.com/frame_123.jpg",
    "detections": [
      {
        "class": "person",
        "confidence": 0.95,
        "bbox": [100, 200, 150, 400],
        "embedding": [0.1, 0.2, -0.3, ...]  # 512-dim vector
      }
    ],
    "transcription": {
      "text": "Hello, how are you?",
      "speaker_id": "speaker_1"  # Optional
    }
  }
}
```

---

### Chat Interface

#### WebSocket /stream
Real-time chat and job updates via WebSocket.

**Connection:**
```
ws://localhost:8000/api/v1/stream?token=<jwt_token>
```

**Client → Server (User Message):**
```json
{
  "type": "message",
  "content": "Show me all moments where someone is wearing a red jacket",
  "video_ids": ["uuid1", "uuid2"]
}
```

**Server → Client (Response):**
```json
{
  "type": "response",
  "content": "I found 3 moments matching your query. Here are the timestamps:",
  "results": [
    {
      "timestamp": 35.2,
      "video_id": "uuid1",
      "confidence": 0.92
    }
  ],
  "processing_time_ms": 245
}
```

**Server → Client (Status Update):**
```json
{
  "type": "job_status",
  "job_id": "uuid",
  "status": "processing_detection",
  "progress": 0.65,
  "message": "Processing frame 78 of 120"
}
```

#### POST /chat
Single chat message (non-streaming).

**Request Body:**
```json
{
  "message": "Show me all moments where someone is wearing a red jacket",
  "video_ids": ["uuid1", "uuid2"],
  "context": {
    "previous_messages": [
      {
        "role": "user",
        "content": "What's in this video?"
      },
      {
        "role": "assistant",
        "content": "This video shows a person in a red jacket entering a building..."
      }
    ]
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "I found 3 moments matching your query. Here are the timestamps:",
    "results": [
      {
        "timestamp": 35.2,
        "video_id": "uuid1",
        "confidence": 0.92,
        "frame_url": "https://cdn.example.com/frame_123.jpg"
      }
    ],
    "processing_time_ms": 245
  }
}
```

---

### Job Management

#### GET /jobs/{job_id}
Get status of a processing job.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid",
    "video_id": "uuid",
    "status": "processing",  # queued, processing, completed, failed
    "progress": 0.65,  # 0.0 to 1.0
    "current_stage": "embeddings",  # ingestion, detection, transcription, embeddings, indexing
    "started_at": "2024-07-10T12:05:00Z",
    "estimated_completion": "2024-07-10T12:08:30Z",
    "stages": [
      {
        "name": "ingestion",
        "status": "completed",
        "duration_seconds": 5
      },
      {
        "name": "detection",
        "status": "completed",
        "duration_seconds": 60
      },
      {
        "name": "transcription",
        "status": "in_progress",
        "progress": 0.8
      }
    ]
  }
}
```

#### GET /jobs
List all jobs for current user.

**Query Parameters:**
```
status: "processing"  # Filter by status
video_id: "uuid"  # Filter by video
skip: 0
limit: 20
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "jobs": [ /* array of job objects */ ],
    "total": 5
  }
}
```

#### POST /jobs/{job_id}/cancel
Cancel a processing job.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid",
    "status": "cancelled",
    "cancelled_at": "2024-07-10T12:06:00Z"
  }
}
```

---

### Analytics

#### GET /analytics/videos
Get statistics across all videos.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_videos": 15,
    "total_duration_hours": 45.5,
    "processing_status": {
      "completed": 12,
      "processing": 2,
      "failed": 1
    },
    "storage_used_gb": 256,
    "most_detected_objects": [
      { "class": "person", "count": 1234 },
      { "class": "car", "count": 456 },
      { "class": "phone", "count": 234 }
    ]
  }
}
```

#### GET /analytics/searches
Get search analytics.

**Query Parameters:**
```
days: 7  # Last N days
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_searches": 234,
    "average_response_time_ms": 245,
    "most_common_queries": [
      { "query": "person", "count": 45 },
      { "query": "car", "count": 23 }
    ]
  }
}
```

---

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| INVALID_INPUT | 400 | Request validation failed |
| UNAUTHORIZED | 401 | Missing or invalid authentication |
| FORBIDDEN | 403 | User lacks permission |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists |
| RATE_LIMITED | 429 | Too many requests |
| INVALID_FILE | 400 | Unsupported file format |
| FILE_TOO_LARGE | 413 | File exceeds size limit |
| PROCESSING_FAILED | 500 | Video processing error |
| SERVICE_UNAVAILABLE | 503 | Service temporarily unavailable |

---

## Rate Limiting

- **Videos:** 10 uploads/hour per user
- **Searches:** 100 searches/hour per user
- **API Calls:** 1000 requests/hour per user

Headers in response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1620000000
```

---

## Pagination

For list endpoints, use `skip` and `limit`:

```
GET /videos?skip=20&limit=10
```

Returns items 20-29, useful for offset-based pagination.

Alternative (cursor-based) for large datasets:
```
GET /videos?cursor=abc123&limit=10
```

---

## SDK

### Python SDK

```python
from omnisight import OmniSight

client = OmniSight(api_key="your-api-key")

# Upload video
job = client.videos.upload("video.mp4", title="My Video")
job.wait_for_completion()

# Search
results = client.search("person in red jacket", video_ids=[video_id])

# Chat
response = client.chat("Show me all moments with a person")
```

### JavaScript SDK

```javascript
import { OmniSight } from 'omnisight-js';

const client = new OmniSight({ apiKey: 'your-api-key' });

// Upload
const job = await client.videos.upload(file);
await job.waitForCompletion();

// Search
const results = await client.search('person in red jacket');

// Chat
const response = await client.chat('Show me all moments with a person');
```


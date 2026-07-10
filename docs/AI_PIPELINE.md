# AI Pipeline

## Overview

The AI Pipeline orchestrates multiple machine learning models to extract semantic understanding from video content. Each model specializes in a specific task, and their outputs are combined for comprehensive video analysis.

## Pipeline Stages

### Stage 1: Video Ingestion

**Purpose:** Prepare video for downstream processing

**Process:**
1. Receive video file (MP4, MOV, WebM, AVI)
2. Validate format and codec
3. Check file size and duration
4. Store in S3/MinIO
5. Extract frames at configurable rate (default: 1 FPS)

**Output:**
- Frame images stored in object storage
- Frame metadata (timestamp, size, hash) in PostgreSQL

**Tools:** FFmpeg

### Stage 2: Object Detection (YOLO v11)

**Purpose:** Identify and localize objects in each frame

**Process:**
1. Load YOLO v11 model (pre-trained on COCO)
2. For each frame:
   - Inference with confidence threshold (default: 0.5)
   - Extract bounding boxes
   - Identify object classes (person, car, dog, etc.)
3. Apply non-maximum suppression
4. Track objects across frames (optional)

**Output:**
- Per-frame detections: `[{class, confidence, bbox, timestamp}]`
- Stored in PostgreSQL

**Model:** YOLOv11n/s/m/l (nano to large, trade-off between speed/accuracy)

**GPU Requirements:**
- Nano: 2GB VRAM (30 fps)
- Small: 4GB VRAM (20 fps)
- Medium: 8GB VRAM (10 fps)

**Confidence Threshold:** 0.5 (adjustable)

### Stage 3: Speech Recognition (Whisper)

**Purpose:** Convert spoken audio to text with timestamps

**Process:**
1. Extract audio from video
2. Split audio into segments (default: 30 seconds)
3. For each segment:
   - Transcribe using Whisper
   - Extract confidence scores
   - Detect language (optional)
4. Generate timestamps for words/sentences
5. Post-process for accuracy

**Output:**
- Transcription text with timestamps
- Confidence scores per segment
- Language detection results
- Stored in PostgreSQL

**Model:** Whisper-base (medium for accuracy)

**Audio Requirements:**
- Sample rate: 16 kHz
- Mono or stereo
- Works well with background noise

**Processing Time:** ~2-3x video duration (base model)

### Stage 4: Visual Understanding (CLIP/SigLIP)

**Purpose:** Create semantic embeddings of visual content

**Process:**
1. Load CLIP model
2. For each frame:
   - Normalize image
   - Pass through vision encoder
   - Generate 512-dim embedding (CLIP) or 768-dim (SigLIP)
3. Normalize to unit vectors
4. Batch process for efficiency

**Output:**
- Per-frame embeddings (floating-point vectors)
- Stored in Qdrant

**Model:** OpenAI CLIP (ViT-B/32) or SigLIP (newer, better accuracy)

**Embedding Dimension:** 512 (CLIP) or 768 (SigLIP)

**Similarity Metric:** Cosine distance

### Stage 5: Transcription Embedding

**Purpose:** Create semantic embeddings for text queries and transcriptions

**Process:**
1. Load CLIP text encoder
2. For user search queries:
   - Convert to embedding
   - Normalize to unit vector
3. Cache query embeddings

**Output:**
- Query embeddings for semantic search
- Same dimension as visual embeddings (512 or 768)

### Stage 6: Indexing & Storage

**Purpose:** Organize processed data for fast retrieval

**Process:**
1. Normalize embeddings
2. Create indexes:
   - Vector index in Qdrant
   - Full-text search index in PostgreSQL
   - Metadata index in PostgreSQL
3. Batch insert data
4. Update statistics

**Data Indexed:**
- Frame embeddings (vector)
- Detection results (object names, confidence)
- Transcription text
- Frame timestamps
- Video metadata

### Stage 7: Semantic Search

**Purpose:** Find relevant frames based on user queries

**Process:**
1. Convert user query to embedding
2. Query Qdrant with similarity threshold
3. Filter results by:
   - Detection confidence
   - Time constraints
   - User filters
4. Rank by relevance score
5. Return timestamps and metadata

**Query Example:**
```
"Person wearing red jacket"
→ Embed query
→ Search Qdrant (cosine similarity)
→ Filter for YOLO class "person" 
→ Return matching frames with scores
```

### Stage 8: Context & LLM Processing

**Purpose:** Synthesize results into natural language responses

**Process:**
1. Parse user query with LLM
2. Extract intent (find, count, describe, etc.)
3. Construct search parameters
4. Execute search across services
5. Aggregate results
6. Generate explanation

**LLM Models (Local Options):**
- Ollama (Llama 2, Mistral)
- vLLM (Vicuña, OpenOrca)
- Hugging Face Transformers

## Pipeline Execution Modes

### Batch Processing (MVP v1)

```
Video Upload
    ↓
Extract Frames
    ↓
[Parallel] YOLO + Whisper
    ↓
CLIP Embeddings
    ↓
Indexing
    ↓
Ready for Search
```

**Latency:** ~2-5x video duration

### Streaming (Future)

```
Live RTSP Stream
    ↓
Real-time Frame Extraction
    ↓
Lightweight Detection (YOLO-nano)
    ↓
Incremental Indexing
    ↓
Immediate Search Capability
```

## Performance Characteristics

### Throughput

| Model | Input | Throughput (GPU) | Throughput (CPU) |
|-------|-------|------------------|------------------|
| YOLO v11-nano | Frame | 30 fps | 2 fps |
| YOLO v11-small | Frame | 20 fps | 1 fps |
| YOLO v11-medium | Frame | 10 fps | 0.3 fps |
| Whisper-base | Audio | 5x realtime | 0.5x realtime |
| CLIP-ViT-B | Frame | 40 fps | 5 fps |

### Memory Requirements

| Model | GPU Memory | CPU Memory |
|-------|-----------|-----------|
| YOLO v11-nano | 2 GB | 4 GB |
| YOLO v11-small | 4 GB | 6 GB |
| Whisper-base | 6 GB | 8 GB |
| CLIP-ViT-B | 4 GB | 6 GB |
| Ollama Llama-7B | 8 GB | 12 GB |

### End-to-End Processing

**Example:** 60-second video at 1080p

```
Ingestion: 5 seconds (FFmpeg frame extraction)
Detection: 60 seconds (YOLO @ 1 fps)
Transcription: 30 seconds (Whisper parallel)
Embeddings: 45 seconds (CLIP @ 1 fps)
Indexing: 10 seconds
──────────────
Total: ~90 seconds on GPU (1.5x video duration)
```

## Quality Control

### Detection Confidence

```
High Confidence (>0.8)  → Include in results, high relevance
Medium Confidence (0.5-0.8) → Include, medium relevance
Low Confidence (<0.5)   → Filter out
```

### Transcription Quality

```
Whisper Confidence >0.8 → High quality, use in search
Whisper Confidence <0.5 → Flag for manual review
```

### Embedding Similarity

```
Cosine Similarity >0.8  → Highly relevant match
Cosine Similarity >0.6  → Relevant match
Cosine Similarity <0.4  → Low relevance filter out
```

## Error Handling

### Model Loading Failures
- Retry with smaller model variant
- Fall back to CPU inference
- Log error and skip stage (graceful degradation)

### Out of Memory
- Reduce batch size
- Use model quantization
- Process in smaller chunks

### Timeout
- Set per-service timeout (default: 5 min)
- Kill stuck processes
- Move to dead letter queue

## Future Enhancements

### Advanced Features
- Face detection (with privacy controls)
- Emotion analysis
- Scene classification
- Activity recognition
- OCR for on-screen text
- Logo detection
- Vehicle plate recognition

### Performance Optimization
- Model quantization (INT8, FP16)
- Knowledge distillation
- Tensor RT optimization
- Multi-GPU inference

### Multi-Modal Enhancement
- Cross-modal retrieval (text→image→sound)
- Audio event detection
- Music/speech separation
- Speaker diarization

## Configuration

### Model Selection

```python
# config/ai_config.yaml
detection:
  model: "yolov11m"  # nano, small, medium, large
  confidence_threshold: 0.5
  device: "cuda"  # cuda, cpu
  
transcription:
  model: "base"  # tiny, base, small, medium, large
  language: "auto"
  device: "cuda"
  
embeddings:
  model: "clip-vit-b"  # or sigclip-large
  device: "cuda"
  batch_size: 32
  
llm:
  model: "llama-7b"
  device: "cpu"  # or cuda for larger models
```

### Performance Tuning

```python
# config/performance_config.yaml
frame_extraction:
  fps: 1  # Frames per second
  quality: "medium"  # low, medium, high
  
batch_processing:
  detection_batch_size: 8
  embedding_batch_size: 32
  max_workers: 4
  
timeouts:
  detection_timeout: 300  # seconds
  transcription_timeout: 600
  embedding_timeout: 300
  indexing_timeout: 120
```


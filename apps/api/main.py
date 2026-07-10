"""
Stub FastAPI application for OmniSight

This is a minimal API to get started. You can build on this.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Create FastAPI app
app = FastAPI(
    title="OmniSight API",
    description="AI-powered video understanding platform",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "omnisight-api",
        "version": "0.1.0"
    }

# API v1 endpoints
@app.get("/api/v1/health")
async def api_health():
    """API health check"""
    return {"status": "operational"}

@app.get("/api/v1/videos")
async def list_videos():
    """List all videos"""
    return {
        "videos": [],
        "total": 0,
        "message": "No videos uploaded yet"
    }

@app.post("/api/v1/videos/upload")
async def upload_video():
    """Upload a video (stub)"""
    return {
        "status": "coming soon",
        "message": "Video upload endpoint not yet implemented"
    }

@app.post("/api/v1/search")
async def search_videos(query: str = "test"):
    """Search videos (stub)"""
    return {
        "query": query,
        "results": [],
        "message": "Search endpoint not yet implemented"
    }

@app.get("/docs")
async def get_docs():
    """Swagger UI documentation"""
    return None

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "OmniSight API",
        "version": "0.1.0",
        "docs": "http://localhost:8000/docs",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

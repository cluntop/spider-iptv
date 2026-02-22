#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python backend API server for Cloudflare Pages integration
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IPTV Spider API",
    description="Backend API for IPTV channel management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Channel(BaseModel):
    id: Optional[int] = None
    name: str
    url: str
    category: str
    status: str = "online"
    quality: str = "HD"
    speed: float = 1.0
    lastChecked: Optional[str] = None

# In-memory storage (replace with database in production)
channels = [
    {
        "id": 1,
        "name": "CCTV-1",
        "url": "http://example.com/cctv1",
        "category": "央视",
        "status": "online",
        "quality": "HD",
        "speed": 1.2,
        "lastChecked": "2024-01-01T00:00:00Z"
    },
    {
        "id": 2,
        "name": "CCTV-2",
        "url": "http://example.com/cctv2",
        "category": "央视",
        "status": "online",
        "quality": "HD",
        "speed": 1.5,
        "lastChecked": "2024-01-01T00:00:00Z"
    },
    {
        "id": 3,
        "name": "东方卫视",
        "url": "http://example.com/dragon",
        "category": "卫视",
        "status": "online",
        "quality": "HD",
        "speed": 1.8,
        "lastChecked": "2024-01-01T00:00:00Z"
    }
]

# API endpoints
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "IPTV Spider API is running",
        "version": "1.0.0"
    }

@app.get("/api/channels", response_model=dict)
async def get_channels():
    """Get all channels"""
    logger.info(f"Getting {len(channels)} channels")
    return {
        "success": True,
        "channels": channels,
        "total": len(channels),
        "message": "Channels retrieved successfully"
    }

@app.post("/api/channels", response_model=dict, status_code=201)
async def create_channel(channel: Channel):
    """Create a new channel"""
    logger.info(f"Creating channel: {channel.name}")
    
    # Generate new ID
    new_id = max([c["id"] for c in channels]) + 1 if channels else 1
    
    # Create new channel
    new_channel = channel.dict()
    new_channel["id"] = new_id
    new_channel["lastChecked"] = "2024-01-01T00:00:00Z"  # Replace with actual timestamp
    
    # Add to storage
    channels.append(new_channel)
    
    return {
        "success": True,
        "channel": new_channel,
        "message": "Channel created successfully"
    }

@app.put("/api/channels/{channel_id}", response_model=dict)
async def update_channel(channel_id: int, channel: Channel):
    """Update an existing channel"""
    logger.info(f"Updating channel: {channel_id}")
    
    # Find channel
    for i, c in enumerate(channels):
        if c["id"] == channel_id:
            # Update channel
            updated_channel = channel.dict()
            updated_channel["id"] = channel_id
            updated_channel["lastChecked"] = "2024-01-01T00:00:00Z"  # Replace with actual timestamp
            
            channels[i] = updated_channel
            
            return {
                "success": True,
                "channel": updated_channel,
                "message": "Channel updated successfully"
            }
    
    raise HTTPException(status_code=404, detail="Channel not found")

@app.delete("/api/channels/{channel_id}", response_model=dict)
async def delete_channel(channel_id: int):
    """Delete a channel"""
    logger.info(f"Deleting channel: {channel_id}")
    
    # Find and remove channel
    for i, c in enumerate(channels):
        if c["id"] == channel_id:
            channels.pop(i)
            
            return {
                "success": True,
                "channelId": channel_id,
                "message": "Channel deleted successfully"
            }
    
    raise HTTPException(status_code=404, detail="Channel not found")

# Run spider endpoint
@app.post("/api/run-spider", response_model=dict)
async def run_spider():
    """Run the main.py script"""
    import subprocess
    import json
    import os
    
    logger.info("Running main.py script")
    
    try:
        # Change to project root directory
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Run the main.py script with initial crawl flag
        result = subprocess.run(
            ["python", "main.py", "--initial-crawl"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        logger.info(f"Spider execution completed with return code: {result.returncode}")
        logger.debug(f"Spider stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"Spider stderr: {result.stderr}")
        
        # Check if playlist was generated
        playlist_exists = os.path.exists("playlist.m3u")
        playlist_size = os.path.getsize("playlist.m3u") if playlist_exists else 0
        
        return {
            "success": result.returncode == 0,
            "message": "Spider run completed successfully" if result.returncode == 0 else "Spider run failed",
            "returnCode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "playlistGenerated": playlist_exists,
            "playlistSize": playlist_size,
            "executionTime": "Completed"
        }
    except subprocess.TimeoutExpired:
        logger.error("Spider execution timed out after 5 minutes")
        return {
            "success": False,
            "message": "Spider execution timed out after 5 minutes",
            "stdout": "",
            "stderr": "Execution timeout",
            "playlistGenerated": False,
            "playlistSize": 0,
            "executionTime": "5 minutes"
        }
    except Exception as e:
        logger.error(f"Error running spider: {e}")
        return {
            "success": False,
            "message": f"Error running spider: {str(e)}",
            "stdout": "",
            "stderr": str(e),
            "playlistGenerated": False,
            "playlistSize": 0,
            "executionTime": "Error"
        }

# Run the server
if __name__ == "__main__":
    logger.info("Starting IPTV Spider API server")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

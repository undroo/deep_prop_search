"""
Main entry point for the FastAPI server.
This module initializes and runs the FastAPI application with all routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from pathlib import Path
import os
from dotenv import load_dotenv

# Import routes after FastAPI initialization to avoid circular imports
from .api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / "config" / ".env")

# Initialize FastAPI app
app = FastAPI(
    title="Property Analysis API",
    description="API for analyzing property listings from Domain.com.au",
    version="1.0.0"
)

# Add CORS middleware with specific configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/")
async def root():
    """Root endpoint that provides basic API information."""
    return {
        "message": "Property Analysis API",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("API_PORT", "8000"))
    
    # Run the server
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    ) 
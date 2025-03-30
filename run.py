"""
Script to run the FastAPI server.
This script should be run from the project root directory.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",  # Updated to use the new backend module path
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 
"""
Test suite for the API routes.
Tests the complete flow from property URL to analysis initialization.
Each test builds upon the results of previous tests.
"""

import os
import json
from datetime import datetime
import sys
from pathlib import Path
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(project_root + '/config/.env')

# Test configuration
TEST_PROPERTY_URL = "https://www.domain.com.au/1-henry-kendall-crescent-mascot-nsw-2020-2019711647"
TEST_RESULTS_DIR = Path(project_root) / "test_results"
TEST_RUN_DIR = TEST_RESULTS_DIR / f"test_routes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Create test results directory
TEST_RUN_DIR.mkdir(parents=True, exist_ok=True)

# Configure file logging
file_handler = logging.FileHandler(TEST_RUN_DIR / "test_routes.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def save_test_data(data: Dict[str, Any], filename: str) -> None:
    """Save test data to a JSON file."""
    filepath = TEST_RUN_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved test data to {filepath}")

def save_api_response(response: Any, test_name: str) -> None:
    """
    Save API response data to a JSON file.
    
    Args:
        response: The API response object
        test_name: Name of the test for the filename
    """
    response_data = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": response.json() if response.status_code != 422 else None,
        "timestamp": datetime.now().isoformat()
    }
    
    # Handle validation errors (422)
    if response.status_code == 422:
        response_data["validation_error"] = response.json()
    
    save_test_data(response_data, f"{test_name}_response.json")

class StateManager:
    """Class to maintain state between tests."""
    def __init__(self):
        self.client: Optional[TestClient] = None
        self.app: Optional[FastAPI] = None
        self.session_id: Optional[str] = None
        self.property_data: Optional[Dict[str, Any]] = None
        self.distance_info: Optional[Dict[str, Any]] = None

@pytest.fixture(scope="session")
def test_state():
    """Create a test state object to share between tests."""
    return StateManager()

def test_01_environment_setup(test_state):
    """Test that all required environment variables are set."""
    logger.info("Testing environment setup...")
    
    required_vars = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "GOOGLE_MAP_API_KEY": os.getenv("GOOGLE_MAP_API_KEY")
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    logger.info("✓ Environment setup successful")

def test_02_fastapi_setup(test_state):
    """Test FastAPI application setup."""
    logger.info("Testing FastAPI setup...")
    
    try:
        app = FastAPI()
        app.include_router(router)
        test_state.app = app
        test_state.client = TestClient(app)
        
        # Test that the app is running
        response = test_state.client.get("/api/v1/")
        save_api_response(response, "02_fastapi_setup")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Root endpoint"}
        
        logger.info("✓ FastAPI setup successful")
        
    except Exception as e:
        logger.error(f"FastAPI setup failed: {str(e)}")
        raise

def test_03_property_initialization(test_state):
    """Test property initialization endpoint."""
    logger.info("Testing property initialization endpoint...")
    
    if not test_state.client:
        raise ValueError("Test client not available from previous test")
    
    try:
        # Test with valid URL
        response = test_state.client.post(
            "/api/v1/initialize",
            json={
                "url": TEST_PROPERTY_URL,
            }
        )
        
        save_api_response(response, "03_property_initialization")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "session_id" in data
        assert "status" in data
        assert data["status"] == "ready"
        
        # Store session ID for later tests
        test_state.session_id = data["session_id"]
        
        logger.info("✓ Property initialization test successful")
        
    except Exception as e:
        logger.error(f"Property initialization test failed: {str(e)}")
        raise

def test_04_invalid_url(test_state):
    """Test property initialization with invalid URL."""
    logger.info("Testing invalid URL handling...")
    
    if not test_state.client:
        raise ValueError("Test client not available from previous test")
    
    try:
        # Test with invalid URL
        response = test_state.client.post(
            "/api/v1/initialize",
            json={
                "url": "https://invalid-domain.com.au/invalid-property",
                "categories": ["school", "train", "shopping"]
            }
        )
        
        save_api_response(response, "04_invalid_url")
        
        # Should still return 200 but with error status
        assert response.status_code == 200
        data = response.json()
        
        # Verify error handling
        assert "session_id" in data
        assert "status" in data
        assert data["status"] == "error"  # Initial status is still not created
        
        logger.info("✓ Invalid URL test successful")
        
    except Exception as e:
        logger.error(f"Invalid URL test failed: {str(e)}")
        raise

def test_05_missing_url(test_state):
    """Test property initialization with missing URL."""
    logger.info("Testing missing URL handling...")
    
    if not test_state.client:
        raise ValueError("Test client not available from previous test")
    
    try:
        # Test with missing URL
        response = test_state.client.post(
            "/api/v1/initialize",
            json={
                "categories": ["school", "train", "shopping"]
            }
        )
        
        save_api_response(response, "05_missing_url")
        
        # Should return 422 (Validation Error)
        assert response.status_code == 422
        
        logger.info("✓ Missing URL test successful")
        
    except Exception as e:
        logger.error(f"Missing URL test failed: {str(e)}")
        raise

def test_06_service_manager_initialization(test_state):
    """Test service manager initialization and lazy loading."""
    logger.info("Testing service manager initialization...")
    
    if not test_state.client:
        raise ValueError("Test client not available from previous test")
    
    try:
        # Make a request to trigger service initialization
        response = test_state.client.post(
            "/api/v1/initialize",
            json={
                "url": TEST_PROPERTY_URL,
            }
        )
        
        save_api_response(response, "06_service_manager")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify new session was created
        assert "session_id" in data
        assert data["session_id"] != test_state.session_id  # Should be different from previous session
        
        logger.info("✓ Service manager initialization test successful")
        
    except Exception as e:
        logger.error(f"Service manager initialization test failed: {str(e)}")
        raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
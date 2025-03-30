"""
Sequential test suite for the property analysis system.
Tests the complete flow from property URL to analysis and persona responses.
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

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from backend.agents.negative_nancy import NegativeNancy
from backend.services.scraper import DomainScraper
from backend.services.map import DistanceCalculator

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
TEST_RUN_DIR = TEST_RESULTS_DIR / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Create test results directory
TEST_RUN_DIR.mkdir(parents=True, exist_ok=True)

# Configure file logging
file_handler = logging.FileHandler(TEST_RUN_DIR / "test_agent.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def save_test_data(data: Dict[str, Any], filename: str) -> None:
    """Save test data to a JSON file."""
    filepath = TEST_RUN_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved test data to {filepath}")

class StateManager:
    """Class to maintain state between tests."""
    def __init__(self):
        self.property_data: Optional[Dict[str, Any]] = None
        self.distance_info: Optional[Dict[str, Any]] = None
        self.agent: Optional[NegativeNancy] = None
        self.analysis_result: Optional[Dict[str, Any]] = None

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
    save_test_data({"status": "success", "message": "Environment setup successful"}, "01_environment_setup.json")

def test_02_domain_scraper(test_state):
    """Test the Domain scraper with the test property URL."""
    logger.info("Testing Domain scraper...")
    
    try:
        scraper = DomainScraper()
        property_data = scraper.get_property_data(TEST_PROPERTY_URL)
        
        if not property_data:
            raise ValueError("Failed to fetch property data")
        
        test_state.property_data = property_data
        logger.info("✓ Domain scraper test successful")
        save_test_data(property_data, "02_domain_scraper.json")
        
    except Exception as e:
        logger.error(f"Domain scraper test failed: {str(e)}")
        raise

def test_03_distance_calculator(test_state):
    """Test the distance calculator with the scraped property data."""
    logger.info("Testing distance calculator...")
    
    if not test_state.property_data:
        raise ValueError("Property data not available from previous test")
    
    try:
        distance_calc = DistanceCalculator(os.getenv("GOOGLE_MAP_API_KEY"))
        address = test_state.property_data["address"]["full_address"]
        distance_info = distance_calc.calculate_distances(address)
        
        test_state.distance_info = distance_info
        logger.info("✓ Distance calculator test successful")
        save_test_data(distance_info, "03_distance_calculator.json")
        
    except Exception as e:
        logger.error(f"Distance calculator test failed: {str(e)}")
        raise

def test_04_negative_nancy_initialization(test_state):
    """Test the NegativeNancy initialization."""
    logger.info("Testing NegativeNancy initialization...")
    
    try:
        agent = NegativeNancy(os.getenv("GEMINI_API_KEY"))
        test_state.agent = agent
        
        # Verify agent attributes
        assert hasattr(agent, 'model')
        assert hasattr(agent, 'analysis_prompt')
        assert hasattr(agent, 'quick_summary_prompt')
        assert hasattr(agent, 'inspection_checklist')
        assert hasattr(agent, 'json_template')
        assert hasattr(agent, 'persona')
        assert agent.persona_file == 'negative_nancy.txt'
        
        logger.info("✓ NegativeNancy initialization successful")
        save_test_data({"status": "success", "message": "NegativeNancy initialized successfully"}, "04_negative_nancy_init.json")
        
    except Exception as e:
        logger.error(f"NegativeNancy initialization failed: {str(e)}")
        raise

def test_05_property_analysis(test_state):
    """Test property analysis with NegativeNancy."""
    logger.info("Testing property analysis with NegativeNancy...")
    
    if not all([test_state.agent, test_state.property_data, test_state.distance_info]):
        raise ValueError("Required data not available from previous tests")
    
    try:
        # Test analysis (will use NegativeNancy's persona)
        result = test_state.agent.analyze_property(
            test_state.property_data,
            test_state.distance_info
        )
        
        test_state.analysis_result = result
        logger.info("✓ Property analysis successful")
        save_test_data(result, "05_property_analysis.json")
        
        # Verify the analysis contains negative aspects
        assert "concerns" in result or "risks" in result or "issues" in result
        logger.info("✓ Analysis contains expected negative aspects")
        
    except Exception as e:
        logger.error(f"Property analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
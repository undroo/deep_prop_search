import os
import json
from datetime import datetime
import sys
from pathlib import Path
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging



# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.services.scraper import DomainScraper

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

if __name__ == "__main__":
    try:
        scraper = DomainScraper()
        property_data = scraper.get_property_data(TEST_PROPERTY_URL)
        
        if not property_data:
            raise ValueError("Failed to fetch property data")
        
        property_data = property_data
        logger.info("✓ Domain scraper test successful")
        save_test_data(property_data, "02_domain_scraper.json")
        
    except Exception as e:
        logger.error(f"Domain scraper test failed: {str(e)}")
        raise


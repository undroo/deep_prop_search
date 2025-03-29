import requests
import json
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
BASE_URL = "http://localhost:8000"
TEST_URL = "https://www.domain.com.au/1-henry-kendall-crescent-mascot-nsw-2020-2019711647"

def save_test_results(results):
    """Save test results to a JSON file"""
    try:
        # Create outputs directory if it doesn't exist
        os.makedirs('outputs', exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'outputs/api_test_results_{timestamp}.json'
        
        # Save results to file
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Test results saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving test results: {str(e)}")
        return None

def test_api():
    """Test the Property Analysis API endpoints"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_url": TEST_URL,
        "endpoints": {}
    }
    
    try:
        # Test root endpoint
        logger.info("Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        results["endpoints"]["root"] = response.json()
        logger.info("✓ Root endpoint test passed")

        # Test personas endpoint
        logger.info("Testing personas endpoint...")
        response = requests.get(f"{BASE_URL}/personas")
        assert response.status_code == 200
        personas = response.json()["personas"]
        results["endpoints"]["personas"] = personas
        logger.info(f"✓ Personas endpoint test passed. Available personas: {personas}")

        # Test property scraping
        logger.info("Testing property scraping...")
        response = requests.post(
            f"{BASE_URL}/property/scrape",
            json={"url": TEST_URL}
        )
        assert response.status_code == 200
        property_data = response.json()
        results["endpoints"]["scrape"] = property_data
        logger.info("✓ Property scraping test passed")

        # Get address from scraped property data
        test_address = property_data.get("address", {}).get("full_address")
        if not test_address:
            raise ValueError("Could not extract address from scraped property data")
        
        # Test distance calculation
        logger.info("Testing distance calculation...")
        response = requests.post(
            f"{BASE_URL}/property/distances",
            json={"address": test_address}
        )
        assert response.status_code == 200
        distance_info = response.json()
        results["endpoints"]["distances"] = distance_info
        logger.info("✓ Distance calculation test passed")

        # Test property analysis with different personas
        logger.info("Testing property analysis with personas...")
        
        # Test analysis with all personas
        response = requests.post(
            f"{BASE_URL}/property/analyze",
            json={
                "property_data": property_data,
                "distance_info": distance_info,
                "quick_summary": False,
                "save_results": True
            }
        )
        assert response.status_code == 200
        analysis = response.json()
        assert "personas" in analysis
        results["endpoints"]["multi_persona_analysis"] = analysis
        logger.info("✓ Multi-persona analysis test passed")

        # Test analysis with specific persona
        if personas:
            test_persona = personas[0]  # Use first available persona
            response = requests.post(
                f"{BASE_URL}/property/analyze",
                json={
                    "property_data": property_data,
                    "distance_info": distance_info,
                    "quick_summary": False,
                    "save_results": True,
                    "persona": test_persona
                }
            )
            assert response.status_code == 200
            analysis = response.json()
            results["endpoints"]["single_persona_analysis"] = {
                "persona": test_persona,
                "analysis": analysis
            }
            logger.info(f"✓ Single persona analysis test passed with {test_persona}")

        # Test quick summary
        logger.info("Testing quick summary...")
        response = requests.post(
            f"{BASE_URL}/property/analyze",
            json={
                "property_data": property_data,
                "quick_summary": True,
                "save_results": True
            }
        )
        assert response.status_code == 200
        summary = response.json()
        results["endpoints"]["quick_summary"] = summary
        logger.info("✓ Quick summary test passed")

        # Save test results
        results["status"] = "success"
        save_test_results(results)
        
        logger.info("All tests passed successfully!")
        return True

    except AssertionError as e:
        logger.error(f"Test failed: {str(e)}")
        results["status"] = "failed"
        results["error"] = str(e)
        save_test_results(results)
        return False
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        results["status"] = "error"
        results["error"] = str(e)
        save_test_results(results)
        return False

if __name__ == "__main__":
    test_api() 
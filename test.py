import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
api_key = os.getenv('DOMAIN_API_KEY')

if not api_key:
    print("Error: DOMAIN_API_KEY not found in .env file")
    exit(1)

# API configuration
base_url = "https://api.domain.com.au/v1"
headers = {
    "X-Api-Key": api_key,
    "Content-Type": "application/json",
}

def test_api_connection():
    """Test basic API connectivity"""
    print("\nTesting API Connection...")
    
    # Test with a simple endpoint (listings/residential/_suggest)
    test_endpoint = f"{base_url}/properties/residential/_suggest"
    test_params = {
        "terms": "bondi",
        "pageSize": 1
    }
    
    try:
        response = requests.get(
            test_endpoint,
            headers=headers,
            params=test_params
        )
        response.raise_for_status()
        print("✓ API Connection Successful!")
        print(f"Response Status Code: {response.status_code}")
        print("\nSample Response Data:")
        print(json.dumps(response.json(), indent=2))
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ API Connection Failed: {e}")
        return False

def test_get_property_details(property_id="2017886902"):
    """Test getting property details using a sample property ID"""
    print("\nTesting Property Details Endpoint...")
    
    details_endpoint = f"{base_url}/listings/{property_id}"
    
    try:
        response = requests.get(
            details_endpoint,
            headers=headers
        )
        response.raise_for_status()
        print("✓ Successfully retrieved property details!")
        print("\nSample Property Data:")
        print(json.dumps(response.json(), indent=2))
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to get property details: {e}")
        return False

if __name__ == "__main__":
    print("Domain API Test Script")
    print("=====================")
    
    # Run tests
    connection_success = test_api_connection()
    
    if connection_success:
        property_success = test_get_property_details()
        
        if property_success:
            print("\nAll tests passed successfully! ✓")
        else:
            print("\nProperty details test failed! ✗")
    else:
        print("\nAPI connection test failed! ✗") 
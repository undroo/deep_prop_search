import google.generativeai as genai
from typing import Dict, Optional
import os
from datetime import datetime
import json

class PropertyAgent:
    def __init__(self, api_key: str):
        """
        Initialize the property agent with Gemini API.
        
        Args:
            api_key: Gemini API key (GEMINI_API_KEY)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def validate_property_data(self, property_data: Dict) -> bool:
        """Validate that required fields exist in property data."""
        try:
            required_fields = {
                'basic_info': ['url', 'title', 'property_type', 'price'],
                'address': ['full_address'],
                'features': ['bedrooms', 'bathrooms', 'parking', 'property_size', 'land_size'],
                'description': None
            }
            
            for section, fields in required_fields.items():
                if section not in property_data:
                    print(f"Missing section: {section}")
                    return False
                if fields:  # If there are specific fields to check
                    for field in fields:
                        if field not in property_data[section]:
                            print(f"Missing field: {section}.{field}")
                            return False
            return True
        except Exception as e:
            print(f"Error validating property data: {e}")
            return False
        
    def analyze_property(self, property_data: Dict, distance_info: Optional[Dict] = None) -> Dict:
        """
        Analyze property data using Gemini AI and provide insights.
        
        Args:
            property_data: Dictionary containing property details
            distance_info: Optional dictionary containing distance calculations
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Validate property data
            if not self.validate_property_data(property_data):
                return {
                    "timestamp": datetime.now().isoformat(),
                    "error": "Invalid or incomplete property data"
                }
            
            # Print basic property information for reference
            self._print_basic_info(property_data)
            
            # Create a structured prompt for Gemini
            prompt = self._create_analysis_prompt(property_data, distance_info)
            print("Generated analysis prompt successfully")
            
            # Get analysis from Gemini
            print("Sending request to Gemini API...")
            response = self.model.generate_content(prompt)
            print("Received response from Gemini API")
            
            if not response or not response.text:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "property_url": property_data.get("basic_info", {}).get("url", "Unknown URL"),
                    "error": "No response from Gemini API"
                }
            
            # Structure the analysis results
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "property_url": property_data.get("basic_info", {}).get("url", "Unknown URL"),
                "analysis": response.text,
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing property: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "property_url": property_data.get("basic_info", {}).get("url", "Unknown URL"),
                "error": str(e)
            }
    
    def _print_basic_info(self, property_data: Dict) -> None:
        """Print basic property information for reference."""
        print("\nProperty Details")
        print("================")
        
        # Basic Information
        basic_info = property_data.get('basic_info', {})
        print(f"\nType: {basic_info.get('property_type', 'Not specified')}")
        if basic_info.get('price'):
            print(f"Price: ${basic_info['price']:,}")
        else:
            print("Price: Not specified")
            
        # Location
        address = property_data.get('address', {})
        print(f"Location: {address.get('full_address', 'Not specified')}")
        
        # Features
        features = property_data.get('features', {})
        print("\nFeatures:")
        print(f"Bedrooms: {features.get('bedrooms', 'Not specified')}")
        print(f"Bathrooms: {features.get('bathrooms', 'Not specified')}")
        print(f"Parking: {features.get('parking', 'Not specified')}")
        
        if features.get('property_size'):
            print(f"Internal Size: {features['property_size']}m²")
        if features.get('land_size'):
            print(f"Land Size: {features['land_size']}m²")
        
        print("================\n")
    
    def _create_analysis_prompt(self, property_data: Dict, distance_info: Optional[Dict] = None) -> str:
        """Create a detailed prompt for Gemini based on property data."""
        try:
            # Format price with safe access
            basic_info = property_data.get('basic_info', {})
            price = f"${basic_info.get('price'):,}" if basic_info.get('price') else 'Not specified'
            
            # Format sizes with safe access
            features = property_data.get('features', {})
            property_size = f"{features.get('property_size')} m²" if features.get('property_size') else 'Not specified'
            land_size = f"{features.get('land_size')} m²" if features.get('land_size') else 'Not specified'
            
            # Base prompt
            prompt = f"""As a real estate expert, analyze this property and provide detailed insights:

Property Details:
- Title: {basic_info.get('title', 'Not specified')}
- Type: {basic_info.get('property_type', 'Not specified')}
- Price: {price}
- Address: {property_data.get('address', {}).get('full_address', 'Not specified')}

Features:
- Bedrooms: {features.get('bedrooms', 'Not specified')}
- Bathrooms: {features.get('bathrooms', 'Not specified')}
- Parking: {features.get('parking', 'Not specified')}
- Property Size: {property_size}
- Land Size: {land_size}

Description:
{property_data.get('description', 'No description available')}"""

            # Add distance information if available
            if distance_info:
                prompt += "\n\n" + "="*50 + "\nLOCATION ANALYSIS\n" + "="*50 + "\n"
                
                for category, locations in distance_info.items():
                    if not locations:
                        continue
                        
                    prompt += f"\n{category.upper()} LOCATIONS:\n"
                    # Sort locations by driving time
                    sorted_locations = sorted(
                        locations,
                        key=lambda x: (
                            x["modes"]["driving"]["current"]["value"] 
                            if x["modes"]["driving"]["current"] 
                            else float('inf')
                        )
                    )
                    
                    for location in sorted_locations:
                        prompt += f"\n{location['destination']}"
                        prompt += f"\nDistance: {location['distance']['text']}"
                        
                        # Add driving times
                        driving = location["modes"]["driving"]
                        transit = location["modes"]["transit"]
                        
                        prompt += "\nBy Car:"
                        if driving["current"]:
                            prompt += f"\n  Current: {driving['current']['text']}"
                        if "morning_peak" in driving and driving["morning_peak"]:
                            prompt += f"\n  Morning Peak (9am): {driving['morning_peak']['text']}"
                        if "evening_peak" in driving and driving["evening_peak"]:
                            prompt += f"\n  Evening Peak (5pm): {driving['evening_peak']['text']}"
                        
                        prompt += "\nBy Public Transport:"
                        if transit["current"]:
                            prompt += f"\n  Current: {transit['current']['text']}"
                        if "morning_peak" in transit and transit["morning_peak"]:
                            prompt += f"\n  Morning Peak (9am): {transit['morning_peak']['text']}"
                        if "evening_peak" in transit and transit["evening_peak"]:
                            prompt += f"\n  Evening Peak (5pm): {transit['evening_peak']['text']}"
                        
                        prompt += "\n" + "-"*30 + "\n"
                
                prompt += "\n" + "="*50 + "\n"

            prompt += """

Please provide a comprehensive analysis including:
1. Overall Property Assessment
2. Price Analysis (value for money, market comparison)
3. Location Analysis
   - Commute times and accessibility (analyze the travel times provided above)
   - Proximity to essential services
   - Impact on daily life
4. Property Features Analysis
5. Potential Benefits and Drawbacks
6. Investment Potential (if applicable)
7. Recommendations for Different Buyer Types (e.g., families, investors, first-home buyers)
8. Any Red Flags or Areas of Concern

Please be specific, detailed, and provide actionable insights based on the provided information."""

            return prompt
        except Exception as e:
            print(f"Error creating analysis prompt: {e}")
            raise
    
    def get_quick_summary(self, property_data: Dict) -> str:
        """
        Get a quick summary of the property using Gemini.
        
        Args:
            property_data: Dictionary containing property details
            
        Returns:
            String containing a brief summary
        """
        try:
            if not self.validate_property_data(property_data):
                return "Error: Invalid or incomplete property data"
            
            # Format price with safe access
            basic_info = property_data.get('basic_info', {})
            price = f"${basic_info.get('price'):,}" if basic_info.get('price') else 'Price not specified'
            features = property_data.get('features', {})
            
            prompt = f"""Provide a brief, 2-3 sentence summary of this property:
- {basic_info.get('title', 'No title')}
- {property_data.get('address', {}).get('full_address', 'No address')}
- {price}
- {features.get('bedrooms', 'N/A')} beds, {features.get('bathrooms', 'N/A')} baths
- {basic_info.get('property_type', 'Type not specified')}"""
            
            print("Sending request to Gemini API for quick summary...")
            response = self.model.generate_content(prompt)
            print("Received response from Gemini API")
            
            return response.text if response and response.text else "Error: No response from Gemini API"
            
        except Exception as e:
            return f"Error generating summary: {e}"
    
    def save_analysis(self, analysis: Dict, filename: str) -> None:
        """
        Save the AI analysis results to a JSON file.
        
        Args:
            analysis: Dictionary containing analysis results
            filename: Base filename to save results to
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{filename}_analysis_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"Analysis saved to {output_file}")
        except Exception as e:
            print(f"Error saving analysis: {e}") 
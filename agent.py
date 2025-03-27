"""
AI-powered property analysis using Google's Gemini API.

This module provides functionality to:
1. Analyze property listings using AI
2. Generate quick summaries and detailed analysis
3. Provide inspection checklists and buyer guidance
4. Save analysis results for future reference
"""

import google.generativeai as genai
from typing import Dict, Optional, List
import os
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class PropertyAgent:
    def __init__(self, api_key: str):
        """
        Initialize the property agent with Gemini API.
        
        Args:
            api_key: Gemini API key (GEMINI_API_KEY)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self._load_prompts()
        self.logger = logging.getLogger(__name__)
        print("✓ Property agent initialized with Gemini API")
    
    def _load_prompts(self) -> None:
        """Load prompt templates from files."""
        try:
            with open('prompts/analysis_prompt.txt', 'r') as f:
                self.analysis_prompt = f.read()
            with open('prompts/quick_summary_prompt.txt', 'r') as f:
                self.quick_summary_prompt = f.read()
            with open('prompts/inspection_checklist.txt', 'r') as f:
                self.inspection_checklist = f.read()
            with open('prompts/analysis_template.json', 'r') as f:
                self.json_template = json.dumps(json.load(f), indent=2)
            print("✓ Loaded prompt templates")
        except Exception as e:
            print(f"⚠ Error loading prompts: {e}")
            # Use default prompts if files not found
            self.analysis_prompt = "Analyze this property: {property_details}\n{location_analysis}"
            self.quick_summary_prompt = "Summarize this property: {property_details}"
            self.inspection_checklist = "Standard inspection checklist"
            self.json_template = "{}"
    
    def validate_property_data(self, property_data: Dict) -> bool:
        """
        Validate that required fields exist in property data.
        
        Args:
            property_data: Dictionary containing property details
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            required_fields = {
                'basic_info': ['url', 'title', 'property_type', 'price'],
                'address': ['full_address'],
                'features': ['bedrooms', 'bathrooms', 'parking', 'property_size', 'land_size'],
                'description': None
            }
            
            for section, fields in required_fields.items():
                if section not in property_data:
                    print(f"⚠ Missing section: {section}")
                    return False
                if fields:  # If there are specific fields to check
                    for field in fields:
                        if field not in property_data[section]:
                            print(f"⚠ Missing field: {section}.{field}")
                            return False
            print("✓ Property data validation successful")
            return True
        except Exception as e:
            print(f"⚠ Error validating property data: {e}")
            return False
    
    def analyze_property(self, property_data: Dict, distance_info: Optional[Dict] = None, persona_prompt: Optional[str] = None) -> Dict:
        """
        Analyze property data using Gemini AI and provide insights.
        
        Args:
            property_data: Dictionary containing property details
            distance_info: Optional dictionary containing distance calculations
            persona_prompt: Optional persona perspective
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            print("\n=== Starting Property Analysis ===")
            
            # Validate property data
            if not self.validate_property_data(property_data):
                print("⚠ Property validation failed")
                return {
                    "timestamp": datetime.now().isoformat(),
                    "error": "Invalid or incomplete property data"
                }
            
            # Print basic property information for reference
            try:
                self._print_basic_info(property_data)
            except Exception as e:
                print(f"⚠ Error printing basic info (non-critical): {e}")
            
            # Format property details
            try:
                property_details = self._format_property_details(property_data)
                location_analysis = self._format_location_analysis(distance_info) if distance_info else ""
                print("✓ Formatted property details and location analysis")
            except Exception as e:
                print(f"⚠ Error formatting property details: {str(e)}")
                raise Exception(f"Failed to format property details: {str(e)}")
            
            # Create analysis prompt with persona if provided
            try:
                if persona_prompt:
                    # Extract persona name and role from the prompt
                    persona_lines = persona_prompt.split('\n')
                    persona_name = persona_lines[0].replace('Name:', '').strip()
                    persona_role = persona_lines[1].replace('Role:', '').strip()
                    
                    # Create persona-specific prompt
                    prompt = f"""
{persona_prompt}

Please analyze this property from your perspective as {persona_name}, {persona_role}.

Property Details:
{property_details}

{location_analysis}

Provide a detailed analysis that reflects your personality and focuses on your key areas of interest.
Format your response as a JSON object with these sections:
1. Overview
2. Key Strengths
3. Key Concerns
4. Investment Potential
5. Final Recommendation

Remember to maintain your unique perspective and focus on your key areas of interest.
"""
                else:
                    # Use default analysis prompt
                    prompt = self.analysis_prompt.format(
                        property_details=property_details,
                        location_analysis=location_analysis,
                        json_template=self.json_template
                    )
                print("✓ Generated analysis prompt")
            except Exception as e:
                print(f"⚠ Error creating analysis prompt: {str(e)}")
                raise Exception(f"Failed to create analysis prompt: {str(e)}")
            
            # Get analysis from Gemini
            try:
                print("\nSending request to Gemini API...")
                response = self.model.generate_content(prompt)
                print("✓ Received response from Gemini API")
                
                if not response or not response.text:
                    print("⚠ Empty response from Gemini API")
                    return {
                        "timestamp": datetime.now().isoformat(),
                        "property_url": property_data.get("basic_info", {}).get("url", "Unknown URL"),
                        "error": "No response from Gemini API"
                    }
                
                print("\n=== Debug: Response Content ===")
                print(f"Response type: {type(response.text)}")
                print(f"Response length: {len(response.text)}")
                print("First 200 characters of response:")
                print(response.text[:200])
                print("Last 200 characters of response:")
                print(response.text[-200:] if len(response.text) > 200 else "")
                print("=== End Response Content ===\n")
            except Exception as e:
                print(f"⚠ Error getting Gemini API response: {str(e)}")
                raise Exception(f"Failed to get Gemini API response: {str(e)}")
            
            # Clean and parse the response
            try:
                # Clean the response text
                cleaned_text = response.text.strip()
                # Remove any markdown code block markers
                cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
                
                print("\n=== Debug: Cleaned Text ===")
                print(f"Cleaned text length: {len(cleaned_text)}")
                print("First 200 characters after cleaning:")
                print(cleaned_text[:200])
                print("Last 200 characters after cleaning:")
                print(cleaned_text[-200:] if len(cleaned_text) > 200 else "")
                print("=== End Cleaned Text ===\n")
                
                # Try to parse as JSON
                if cleaned_text.startswith("{") and cleaned_text.endswith("}"):
                    print("Text appears to be JSON format, attempting to parse...")
                    try:
                        analysis_json = json.loads(cleaned_text)
                        print("✓ Successfully parsed JSON")
                        print("\nJSON structure:")
                        for key in analysis_json.keys():
                            print(f"- {key}")
                        analysis_text = json.dumps(analysis_json, indent=2)
                    except json.JSONDecodeError as je:
                        print(f"⚠ JSON parsing failed: {je}")
                        print("Error location in text:")
                        error_location = min(je.pos, len(cleaned_text))
                        context_start = max(0, error_location - 50)
                        context_end = min(len(cleaned_text), error_location + 50)
                        print(f"...{cleaned_text[context_start:context_end]}...")
                        print("\nAttempting to fix common JSON issues...")
                        
                        # Try to fix common JSON formatting issues
                        fixed_text = cleaned_text.replace('\n', ' ').replace('\r', '')
                        try:
                            analysis_json = json.loads(fixed_text)
                            print("✓ Successfully parsed JSON after fixing")
                            analysis_text = json.dumps(analysis_json, indent=2)
                        except json.JSONDecodeError:
                            print("⚠ Failed to fix JSON, using raw text")
                            analysis_text = cleaned_text
                else:
                    print("⚠ Response is not in JSON format")
                    print("Response format check:")
                    print(f"Starts with '{{': {cleaned_text.startswith('{')}")
                    print(f"Ends with '}}': {cleaned_text.endswith('}')}")
                    print(f"First character: '{cleaned_text[0]}'")
                    print(f"Last character: '{cleaned_text[-1]}'")
                    analysis_text = cleaned_text
            except Exception as e:
                print(f"⚠ Error processing response: {str(e)}")
                analysis_text = cleaned_text
            
            # Add inspection checklist
            try:
                print("\nGenerating inspection checklist...")
                checklist_response = self.model.generate_content(
                    f"Based on this property analysis:\n{response.text}\n\n"
                    f"Please provide specific inspection points using this template:\n{self.inspection_checklist}"
                )
                print("✓ Generated inspection checklist")
            except Exception as e:
                print(f"⚠ Error generating inspection checklist: {str(e)}")
                checklist_response = None
            
            # Structure the analysis results
            try:
                analysis = {
                    "timestamp": datetime.now().isoformat(),
                    "property_url": property_data.get("basic_info", {}).get("url", "Unknown URL"),
                    "analysis": analysis_text,
                    "inspection_checklist": checklist_response.text if checklist_response else None
                }
                
                print("\n=== Debug: Final Analysis ===")
                print(f"Analysis keys: {list(analysis.keys())}")
                print(f"Analysis text type: {type(analysis['analysis'])}")
                print(f"Analysis text length: {len(analysis['analysis'])}")
                print("=== End Final Analysis ===\n")
                
                return analysis
            except Exception as e:
                print(f"⚠ Error structuring final analysis: {str(e)}")
                raise Exception(f"Failed to structure final analysis: {str(e)}")
            
        except Exception as e:
            print(f"⚠ Error in analyze_property: {str(e)}")
            print("Stack trace:")
            import traceback
            traceback.print_exc()
            return {
                "timestamp": datetime.now().isoformat(),
                "property_url": property_data.get("basic_info", {}).get("url", "Unknown URL"),
                "error": str(e)
            }
    
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
            
            # Format property details
            property_details = self._format_property_details(property_data)
            
            # Create quick summary prompt
            prompt = self.quick_summary_prompt.format(
                property_details=property_details
            )
            print("✓ Generated quick summary prompt")
            
            # Get summary from Gemini
            print("Sending request to Gemini API...")
            response = self.model.generate_content(prompt)
            print("✓ Received response from Gemini API")
            
            return response.text if response and response.text else "Error: No response from Gemini API"
            
        except Exception as e:
            return f"Error generating summary: {e}"
    
    def _format_property_details(self, property_data: Dict) -> str:
        """Format property details for the prompt."""
        basic_info = property_data.get('basic_info', {})
        features = property_data.get('features', {})
        
        # Format price
        price = f"${basic_info.get('price'):,}" if basic_info.get('price') else 'Not specified'
        
        # Format sizes
        property_size = f"{features.get('property_size')} m²" if features.get('property_size') else 'Not specified'
        land_size = f"{features.get('land_size')} m²" if features.get('land_size') else 'Not specified'
        
        return f"""
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
{property_data.get('description', 'No description available')}
"""
    
    def _format_location_analysis(self, distance_info: Dict) -> str:
        """Format location analysis for the prompt."""
        if not distance_info:
            return ""
        
        analysis = ["\nLOCATION ANALYSIS"]
        
        for category, locations in distance_info.items():
            if not locations:
                continue
            
            analysis.append(f"\n{category.upper()} LOCATIONS:")
            
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
                analysis.append(f"\n{location['destination']}")
                analysis.append(f"Distance: {location['distance']['text']}")
                
                # Add transport mode times
                for mode, times in location["modes"].items():
                    analysis.append(f"\nBy {mode.title()}:")
                    for time_type, time_info in times.items():
                        if time_info:
                            analysis.append(f"  {time_type}: {time_info['text']}")
                
                analysis.append("-" * 30)
        
        return "\n".join(analysis)
    
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
    
    # def save_analysis(self, analysis: Dict, analysis_type: str) -> str:
    #     """
    #     Save the AI analysis results to a JSON file in the outputs directory.
        
    #     Args:
    #         analysis: Dictionary containing analysis results
    #         analysis_type: Type of analysis (e.g., 'property_analysis', 'quick_summary')
            
    #     Returns:
    #         str: Path to saved analysis file
    #     """
    #     try:
    #         # Create results directory if it doesn't exist
    #         os.makedirs('results', exist_ok=True)
            
    #         # Generate filename with timestamp
    #         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    #         filename = f'results/{analysis_type}_{timestamp}.json'
            
    #         # Save analysis to file
    #         with open(filename, 'w') as f:
    #             json.dump(analysis, f, indent=2)
            
    #         self.logger.info(f"Analysis saved to {filename}")
    #         return filename
    #     except Exception as e:
    #         self.logger.error(f"Error saving analysis: {str(e)}")
    #         raise 
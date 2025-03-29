"""
Base agent class for property analysis.
This class provides core functionality that can be inherited by specific agent types.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for property analysis agents."""
    
    def __init__(self, api_key: str):
        """Initialize the base agent with API key and load prompts."""
        self.api_key = api_key
        self._setup_gemini(api_key)
        self._load_prompts()
        self._load_inspection_checklist()
        self._load_json_template()
    
    def _setup_gemini(self, api_key: str) -> None:
        """Set up the Gemini API with the provided key."""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {str(e)}")
            raise
    
    def _load_prompts(self) -> None:
        """Load the analysis and quick summary prompts."""
        try:
            prompts_path = os.path.join(os.path.dirname(__file__), 'prompts')
            
            # Load analysis prompt
            with open(os.path.join(prompts_path, 'analysis_prompt.txt'), 'r') as f:
                self.analysis_prompt = f.read()
            
            # Load quick summary prompt
            with open(os.path.join(prompts_path, 'quick_summary_prompt.txt'), 'r') as f:
                self.quick_summary_prompt = f.read()
            
            logger.info("Prompts loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load prompts: {str(e)}")
            raise
    
    def _load_inspection_checklist(self) -> None:
        """Load the inspection checklist."""
        try:
            checklist_path = os.path.join(os.path.dirname(__file__), 'prompts', 'inspection_checklist.txt')
            with open(checklist_path, 'r') as f:
                self.inspection_checklist = f.read()
            logger.info("Inspection checklist loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load inspection checklist: {str(e)}")
            raise
    
    def _load_json_template(self) -> None:
        """Load the JSON template for structured responses."""
        try:
            template_path = os.path.join(os.path.dirname(__file__), 'prompts', 'analysis_template.json')
            with open(template_path, 'r') as f:
                self.json_template = f.read()
            logger.info("JSON template loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load JSON template: {str(e)}")
            raise
    
    def validate_property_data(self, property_data: Dict[str, Any]) -> bool:
        """Validate that the property data contains all required fields."""
        required_fields = {
            'basic_info': ['url', 'title', 'property_type', 'price'],
            'address': ['full_address'],
            'features': ['bedrooms', 'bathrooms', 'parking', 'property_size', 'land_size'],
            'description': []
        }
        
        for section, fields in required_fields.items():
            if section not in property_data:
                logger.error(f"Missing required section: {section}")
                return False
            
            for field in fields:
                if field not in property_data[section]:
                    logger.error(f"Missing required field: {section}.{field}")
                    return False
        
        return True
    
    def analyze_property(self, property_data: Dict[str, Any], distance_info: Dict[str, Any], persona_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a property with optional persona."""
        if not self.validate_property_data(property_data):
            raise ValueError("Invalid property data")
        
        try:
            # Prepare the analysis prompt
            prompt = self.analysis_prompt.format(
                property_data=json.dumps(property_data, indent=2),
                distance_info=json.dumps(distance_info, indent=2),
                inspection_checklist=self.inspection_checklist,
                json_template=self.json_template
            )
            
            # Add persona prompt if provided
            if persona_prompt:
                prompt = f"{persona_prompt}\n\n{prompt}"
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Clean and parse response
            try:
                # Clean the response text
                cleaned_text = response.text.strip()
                
                # Remove markdown code block markers if present
                cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
                
                # Try to parse as JSON
                try:
                    result = json.loads(cleaned_text)
                except json.JSONDecodeError:
                    # If direct parsing fails, try to find JSON content between curly braces
                    start_idx = cleaned_text.find('{')
                    end_idx = cleaned_text.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = cleaned_text[start_idx:end_idx]
                        result = json.loads(json_str)
                    else:
                        raise ValueError("No valid JSON found in response")
                
                # Add metadata
                result['timestamp'] = datetime.now().isoformat()
                result['property_url'] = property_data['basic_info']['url']
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse response as JSON: {str(e)}")
                logger.error(f"Response text: {response.text}")
                raise
            
        except Exception as e:
            logger.error(f"Property analysis failed: {str(e)}")
            raise
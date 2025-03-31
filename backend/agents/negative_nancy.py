"""
NegativeNancy agent class that inherits from BaseAgent.
This agent provides a consistently negative perspective on property analysis.
"""

import os
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
import logging
import google.generativeai as genai
import json

logger = logging.getLogger(__name__)

class NegativeNancy(BaseAgent):
    """Agent that provides a negative perspective on property analysis."""
    
    def __init__(self, api_key: str):
        """Initialize NegativeNancy with API key and load persona from file."""
        self.api_key = api_key
        super().__init__(agent_type="negative", agent_name="Negative Nancy")
        self.persona_file = 'negative_nancy.txt'
        self.persona = self._load_persona()

    def _setup_gemini(self) -> None:
        """Set up the Gemini API with the provided key."""
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.logger.info("Gemini API configured successfully")
            else:
                self.logger.warning("API key not set, Gemini API will not be available")
        except Exception as e:
            self.logger.error(f"Failed to configure Gemini API: {str(e)}")
            raise
        

    def _get_agent_response(self, prompt: str) -> str:
        """
        Get response from Negative Nancy using the Gemini API.
        
        Args:
            prompt: The formatted prompt to send to the model
            
        Returns:
            The model's response as a string
        """
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Clean the response text
            cleaned_text = response.text.strip()
            
            # Remove markdown code block markers if present
            cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Failed to get response from Gemini API: {str(e)}")
            raise
    
    def _load_persona(self) -> str:
        """Load the persona definition from the personas folder."""
        try:
            persona_path = os.path.join(os.path.dirname(__file__), 'personas', self.persona_file)
            print(f"Loading persona from {persona_path}")
            with open(persona_path, 'r') as f:
                persona = f.read().strip()
            logger.info("Loaded NegativeNancy persona successfully")
            return persona
        except Exception as e:
            logger.error(f"Failed to load NegativeNancy persona: {str(e)}")
            raise
    
    def analyze_property(
        self, 
        property_data: Dict[str, Any], 
        distance_info: Dict[str, Any], 
        chat_history: Optional[List[Dict[str, Any]]] = None,
        current_question: Optional[str] = None,
        persona_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze property with NegativeNancy's perspective.
        Overrides the base method to always include the negative persona.
        """
        # Always use NegativeNancy's persona, ignoring any provided persona
        return super().analyze_property(
            property_data=property_data,
            distance_info=distance_info,
            chat_history=chat_history,
            current_question=current_question,
            persona_prompt=self.persona
        )
    
    def get_quick_summary(self, property_data: Dict[str, Any]) -> str:
        """
        Generate a quick summary with NegativeNancy's perspective.
        Overrides the base method to include the negative persona.
        """
        # Add persona to the quick summary prompt
        prompt = f"{self.persona}\n\n{self.quick_summary_prompt}"
        return self.model.generate_content(
            prompt.format(property_data=property_data)
        ).text.strip() 
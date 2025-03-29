"""
NegativeNancy agent class that inherits from BaseAgent.
This agent provides a consistently negative perspective on property analysis.
"""

import os
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class NegativeNancy(BaseAgent):
    """Agent that provides a negative perspective on property analysis."""
    
    def __init__(self, api_key: str):
        """Initialize NegativeNancy with API key and load persona from file."""
        super().__init__(api_key)
        self.persona_file = 'negative_nancy.txt'
        self.persona = self._load_persona()
        
    
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
    
    def analyze_property(self, property_data: Dict[str, Any], distance_info: Dict[str, Any], persona_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze property with NegativeNancy's perspective.
        Overrides the base method to always include the negative persona.
        """
        # Always use NegativeNancy's persona, ignoring any provided persona
        return super().analyze_property(property_data, distance_info, self.persona)
    
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
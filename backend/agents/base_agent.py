"""
Base agent class for property analysis.
This class provides core functionality that can be inherited by specific agent types.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import google.generativeai as genai
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for property analysis agents."""
    
    def __init__(self, agent_type: str, agent_name: str):
        self.agent_type = agent_type
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{agent_type}_{agent_name}")
        self.template_dir = Path(__file__).parent / "prompts"
        self.analysis_template = self._load_template("analysis_template.json")
        self.analysis_prompt = self._load_template("analysis_prompt.txt")
        self.response_prompt = self._load_template("response_prompt.txt")
        self._setup_gemini()
        self._load_prompts()
        self._load_inspection_checklist()
        self._load_json_template()
    
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
    
    def _load_prompts(self) -> None:
        """Load the analysis and quick summary prompts."""
        try:
            prompts_path = self.template_dir
            
            # Load analysis prompt
            with open(prompts_path / 'analysis_prompt.txt', 'r') as f:
                self.analysis_prompt = f.read()
            
            # Load quick summary prompt
            with open(prompts_path / 'quick_summary_prompt.txt', 'r') as f:
                self.quick_summary_prompt = f.read()
            
            # Load response prompt
            with open(prompts_path / 'response_prompt.txt', 'r') as f:
                self.response_prompt = f.read()
            
            self.logger.info("Prompts loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load prompts: {str(e)}")
            raise
    
    def _load_inspection_checklist(self) -> None:
        """Load the inspection checklist."""
        try:
            checklist_path = self.template_dir / 'inspection_checklist.txt'
            with open(checklist_path, 'r') as f:
                self.inspection_checklist = f.read()
            self.logger.info("Inspection checklist loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load inspection checklist: {str(e)}")
            raise
    
    def _load_json_template(self) -> None:
        """Load the JSON template for structured responses."""
        try:
            template_path = self.template_dir / 'analysis_template.json'
            with open(template_path, 'r') as f:
                self.json_template = f.read()
            self.logger.info("JSON template loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load JSON template: {str(e)}")
            raise
    
    def _load_template(self, filename: str) -> str:
        """Load a template file from the prompts directory."""
        template_path = self.template_dir / filename
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error loading template {filename}: {str(e)}")
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
                self.logger.error(f"Missing required section: {section}")
                return False
            
            for field in fields:
                if field not in property_data[section]:
                    self.logger.error(f"Missing required field: {section}.{field}")
                    return False
        
        return True
    
    def _format_chat_history(self, chat_history: List[Dict[str, Any]]) -> str:
        """Format chat history into a readable string."""
        formatted_history = []
        for message in chat_history:
            agent = message.get('agent', 'Unknown')
            content = message.get('content', '')
            timestamp = message.get('timestamp', '')
            formatted_history.append(f"[{timestamp}] {agent}: {content}")
        return "\n".join(formatted_history)

    def _format_previous_analysis(self, previous_analysis: Dict[str, Any]) -> str:
        """Format previous analysis into a readable string."""
        formatted_analysis = []
        for section, content in previous_analysis.items():
            formatted_analysis.append(f"\n{section.upper()}:")
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, list):
                        formatted_analysis.append(f"{key}:")
                        for item in value:
                            formatted_analysis.append(f"- {item}")
                    else:
                        formatted_analysis.append(f"{key}: {value}")
            elif isinstance(content, list):
                for item in content:
                    formatted_analysis.append(f"- {item}")
            else:
                formatted_analysis.append(str(content))
        return "\n".join(formatted_analysis)

    def analyze_property(
        self, 
        property_data: Dict[str, Any], 
        distance_info: Optional[Dict[str, Any]] = None, 
        chat_history: Optional[List[Dict[str, Any]]] = None, 
        current_question: Optional[str] = None,
        persona_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a property and return structured analysis.
        
        Args:
            property_data: Dictionary containing property information
            distance_info: Optional dictionary containing distance calculations
            chat_history: Optional list of previous chat messages
            current_question: Optional current question from the user
            persona_prompt: Optional persona prompt to use for the analysis
            
        Returns:
            Dictionary containing the analysis results
        """
        try:
            self.logger.info(f"Starting property analysis for {property_data.get('address', 'Unknown Address')}")
            
            # If this is a follow-up question, use the response prompt
            if current_question and chat_history:
                self.logger.info("Processing follow-up question")
                prompt = self.response_prompt.format(
                    agent_name=self.agent_name,
                    agent_type=self.agent_type,
                    previous_analysis=self._format_previous_analysis(chat_history[-1].get('analysis', {})),
                    chat_history=self._format_chat_history(chat_history[:-1]),  # Exclude the last message (analysis)
                    current_question=current_question
                )
            else:
                # Initial analysis
                self.logger.info("Performing initial property analysis")
                prompt = self.analysis_prompt.format(
                    property_data=json.dumps(property_data, indent=2),
                    distance_info=json.dumps(distance_info, indent=2) if distance_info else "No distance information available",
                    json_template=self.json_template
                )

            self.logger.info("Preparing prompt")
            # Add persona prompt if provided
            if persona_prompt:
                prompt = f"{persona_prompt}\n\n{prompt}"

            # Get response from the agent
            response = self._get_agent_response(prompt)
            
            # For initial analysis, parse the response into the template structure
            if not current_question:
                try:
                    analysis_result = json.loads(response)
                    self.logger.info("Successfully parsed analysis result")
                    return analysis_result
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse analysis result: {str(e)}")
                    raise
            else:
                # For follow-up questions, return a conversational response
                return {
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                    "agent": self.agent_name
                }

        except Exception as e:
            self.logger.error(f"Error in analyze_property: {str(e)}")
            raise

    def _get_agent_response(self, prompt: str) -> str:
        """
        Get response from the agent. This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _get_agent_response")
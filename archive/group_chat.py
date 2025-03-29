"""
Group chat interface for property analysis with multiple AI personas.

This module provides:
1. A chat-like interface for property analysis
2. Multiple AI personas with different perspectives
3. Property details display
4. Real-time analysis from different viewpoints
5. Interactive Q&A with AI personas
"""

import streamlit as st
import os
from datetime import datetime
import json
from typing import Dict, List
from dotenv import load_dotenv
import google.generativeai as genai

from scraper import DomainScraper
from map import DistanceCalculator

# Page configuration
st.set_page_config(
    page_title="Property Analysis Group Chat",
    page_icon="💬",
    layout="wide"
)

# Custom CSS for better visual presentation
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 1rem;
        background-color: var(--background-color);
        border-radius: 1rem;
        margin: 1rem 0;
        max-height: 600px;
        overflow-y: auto;
    }
    .chat-message {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        max-width: 80%;
        margin: 0.5rem 0;
    }
    .chat-message.user {
        margin-left: auto;
        flex-direction: row-reverse;
    }
    .chat-message.agent {
        margin-right: auto;
    }
    .message-bubble {
        padding: 0.8rem 1rem;
        border-radius: 1rem;
        position: relative;
        word-wrap: break-word;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    .chat-message.user .message-bubble {
        background-color: #007AFF;
        color: white;
        border-bottom-right-radius: 0.2rem;
    }
    .chat-message.agent .message-bubble {
        background-color: #E9ECEF;
        color: #212529;
        border-bottom-left-radius: 0.2rem;
    }
    .agent-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        background-color: #007AFF;
        color: white;
        flex-shrink: 0;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    .message-content {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }
    .message-name {
        font-size: 0.8rem;
        opacity: 0.8;
        margin-bottom: 0.2rem;
    }
    .message-text {
        line-height: 1.4;
    }
    .property-details {
        background-color: var(--secondary-background-color);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: var(--text-color);
    }
    .stTabs {
        margin-top: 1rem;
    }
    .url-input {
        background-color: var(--secondary-background-color);
    }
    .question-input {
        background-color: var(--secondary-background-color);
    }
    /* Custom scrollbar for chat container */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: var(--secondary-background-color);
        border-radius: 4px;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background: #007AFF;
        border-radius: 4px;
    }
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #007AFF;
        opacity: 0.8;
    }
    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        .chat-message.agent .message-bubble {
            background-color: #2C2C2E;
            color: #FFFFFF;
        }
        .chat-container {
            background-color: #1C1C1E;
        }
    }
    </style>
""", unsafe_allow_html=True)

class PersonaAgent:
    def __init__(self, persona_file: str, api_key: str):
        """Initialize a persona agent with its specific personality."""
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self._load_persona(persona_file)
        genai.configure(api_key=api_key)
    
    def _load_persona(self, persona_file: str) -> None:
        """Load persona definition from file."""
        try:
            with open(persona_file, 'r') as f:
                self.persona = f.read()
            print(f"✓ Loaded persona from {persona_file}")
        except Exception as e:
            print(f"⚠ Error loading persona: {e}")
            self.persona = "Default persona"
    
    def analyze_property(self, property_data: Dict, distance_info: Dict) -> str:
        """Generate a short analysis from the persona's perspective."""
        try:
            # Format property details for the prompt
            property_details = self._format_property_details(property_data)
            location_analysis = self._format_location_analysis(distance_info)
            
            # Create analysis prompt
            prompt = f"""
{self.persona}

Please analyze this property from your perspective:

{property_details}

{location_analysis}

Provide a short, focused analysis (2-3 sentences) highlighting the most important points from your perspective.
Be concise and direct, focusing on your key areas of interest.
"""
            
            # Get analysis from Gemini
            response = self.model.generate_content(prompt)
            return response.text if response and response.text else "Error: No response generated"
            
        except Exception as e:
            return f"Error generating analysis: {e}"
    
    def answer_question(self, question: str, property_data: Dict, distance_info: Dict) -> str:
        """Answer a specific question about the property from the persona's perspective."""
        try:
            # Format property details for the prompt
            property_details = self._format_property_details(property_data)
            location_analysis = self._format_location_analysis(distance_info)
            
            # Create question prompt
            prompt = f"""
{self.persona}

Based on your personality and perspective, please answer this question about the property:

Question: {question}

Property Details:
{property_details}

{location_analysis}

Provide a concise answer that reflects your personality and perspective.
"""
            
            # Get answer from Gemini
            response = self.model.generate_content(prompt)
            return response.text if response and response.text else "Error: No response generated"
            
        except Exception as e:
            return f"Error generating answer: {e}"
    
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

def display_property_details(property_data: Dict) -> None:
    """Display property details in a structured format."""
    st.write("### Property Details")
    
    # Basic Information
    basic_info = property_data.get('basic_info', {})
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Basic Information")
        st.write(f"**Title:** {basic_info.get('title', 'Not specified')}")
        st.write(f"**Type:** {basic_info.get('property_type', 'Not specified')}")
        st.write(f"**Price:** ${basic_info.get('price'):,}" if basic_info.get('price') else "**Price:** Not specified")
        st.write(f"**Address:** {property_data.get('address', {}).get('full_address', 'Not specified')}")
    
    # Features
    features = property_data.get('features', {})
    with col2:
        st.write("#### Features")
        st.write(f"**Bedrooms:** {features.get('bedrooms', 'Not specified')}")
        st.write(f"**Bathrooms:** {features.get('bathrooms', 'Not specified')}")
        st.write(f"**Parking:** {features.get('parking', 'Not specified')}")
        if features.get('property_size'):
            st.write(f"**Property Size:** {features['property_size']}m²")
        if features.get('land_size'):
            st.write(f"**Land Size:** {features['land_size']}m²")
    
    # Description
    st.write("#### Description")
    st.write(property_data.get('description', 'No description available'))
    
    # Location Analysis
    if "distance_info" in st.session_state and st.session_state.distance_info:
        st.write("#### Location Analysis")
        
        for category, locations in st.session_state.distance_info.items():
            if not locations:
                continue
                
            st.write(f"##### {category.title()}")
            
            # Create a table for each category
            table_data = []
            for location in locations:
                destination = location['destination']
                distance = location['distance']['text']
                
                # Get transport times
                times = []
                for mode, mode_data in location['modes'].items():
                    if mode_data.get('current'):
                        times.append(f"{mode.title()}: {mode_data['current']['text']}")
                
                table_data.append({
                    "Destination": destination,
                    "Distance": distance,
                    "Travel Times": " | ".join(times)
                })
            
            # Display the table
            st.table(table_data)
            st.markdown("---")

def main():
    """Main application entry point."""
    # Load environment variables
    load_dotenv(dotenv_path="config/.env")
    
    # Get API keys
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    maps_api_key = os.getenv('GOOGLE_MAP_API_KEY')
    
    if not gemini_api_key:
        st.error("Please set the GEMINI_API_KEY environment variable in config/.env")
        return
    
    if not maps_api_key:
        st.error("Please set the GOOGLE_MAP_API_KEY environment variable in config/.env")
        return
    
    # Initialize components
    print("Initializing components...")
    scraper = DomainScraper()
    distance_calculator = DistanceCalculator(maps_api_key)
    
    # Initialize persona agents
    print("Initializing persona agents...")
    negative_nancy = PersonaAgent('Personas/negative_nancy.txt', gemini_api_key)
    optimistic_ollie = PersonaAgent('Personas/optimistic_ollie.txt', gemini_api_key)
    cautious_cat = PersonaAgent('Personas/cautious_cat.txt', gemini_api_key)
    
    # Create tabs
    tab1, tab2 = st.tabs(["💬 Group Chat", "📋 Property Details"])
    
    with tab1:
        st.title("Property Analysis Group Chat")
        
        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "url_submitted" not in st.session_state:
            st.session_state.url_submitted = False
        if "current_url" not in st.session_state:
            st.session_state.current_url = ""
        if "question_submitted" not in st.session_state:
            st.session_state.question_submitted = False
        if "current_question" not in st.session_state:
            st.session_state.current_question = ""
        
        # URL input section
        st.write("### Step 1: Enter Property URL")
        if not st.session_state.url_submitted:
            url = st.text_input("Enter Domain.com.au URL:", key="url_input")
            if url:
                st.session_state.current_url = url
                st.session_state.url_submitted = True
                st.rerun()
        else:
            st.text_input("Property URL:", value=st.session_state.current_url, disabled=True)
            if st.button("Change URL"):
                st.session_state.url_submitted = False
                st.session_state.current_url = ""
                st.session_state.messages = []
                st.session_state.property_data = None
                st.session_state.distance_info = None
                st.session_state.question_submitted = False
                st.session_state.current_question = ""
                st.rerun()
        
        # Display chat messages
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            st.markdown(f"""
            <div class="chat-message {message['role']}">
                <div class="agent-avatar">{message['avatar']}</div>
                <div class="message-content">
                    <div class="message-bubble">
                        <div class="message-name">{message['name']}</div>
                        <div class="message-text">{message['content']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process URL if submitted
        if st.session_state.url_submitted and not st.session_state.messages:
            try:
                with st.spinner("Analyzing property..."):
                    # Get property data
                    property_data = scraper.get_property_data(st.session_state.current_url)
                    if not property_data:
                        st.error("Failed to fetch property data")
                        return
                    
                    # Get distance information
                    distance_info = distance_calculator.calculate_distances(
                        property_data.get("address", {}).get("full_address", "")
                    )
                    
                    # Add user message
                    st.session_state.messages.append({
                        "role": "user",
                        "name": "You",
                        "content": f"Analyzing: {st.session_state.current_url}",
                        "avatar": "🐕"
                    })
                    
                    # Get analysis from each persona
                    nancy_analysis = negative_nancy.analyze_property(property_data, distance_info)
                    ollie_analysis = optimistic_ollie.analyze_property(property_data, distance_info)
                    cat_analysis = cautious_cat.analyze_property(property_data, distance_info)
                    
                    # Add persona messages
                    st.session_state.messages.append({
                        "role": "agent",
                        "name": "Negative Nancy",
                        "content": nancy_analysis,
                        "avatar": "👎"
                    })
                    
                    st.session_state.messages.append({
                        "role": "agent",
                        "name": "Optimistic Ollie",
                        "content": ollie_analysis,
                        "avatar": "👍"
                    })
                    
                    st.session_state.messages.append({
                        "role": "agent",
                        "name": "Cautious Cat",
                        "content": cat_analysis,
                        "avatar": "🐱"
                    })
                    
                    # Store property data in session state
                    st.session_state.property_data = property_data
                    st.session_state.distance_info = distance_info
                    
                    # Rerun to update display
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error analyzing property: {str(e)}")
                st.exception(e)
        
        # Question input section
        if st.session_state.messages:
            if not st.session_state.question_submitted:
                question = st.text_input("", placeholder="Type your message...", key="question_input")
                if question:
                    st.session_state.current_question = question
                    st.session_state.question_submitted = True
                    st.rerun()
            else:
                st.text_input("", value="", disabled=True)
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("New Message"):
                        st.session_state.question_submitted = False
                        st.session_state.current_question = ""
                        st.rerun()
            
            if st.session_state.question_submitted:
                try:
                    with st.spinner(""):
                        # Add user question to chat
                        st.session_state.messages.append({
                            "role": "user",
                            "name": "You",
                            "content": st.session_state.current_question,
                            "avatar": "🐕"
                        })
                        
                        # Get answers from each persona
                        nancy_answer = negative_nancy.answer_question(
                            st.session_state.current_question,
                            st.session_state.property_data,
                            st.session_state.distance_info
                        )
                        ollie_answer = optimistic_ollie.answer_question(
                            st.session_state.current_question,
                            st.session_state.property_data,
                            st.session_state.distance_info
                        )
                        cat_answer = cautious_cat.answer_question(
                            st.session_state.current_question,
                            st.session_state.property_data,
                            st.session_state.distance_info
                        )
                        
                        # Add persona answers
                        st.session_state.messages.append({
                            "role": "agent",
                            "name": "Negative Nancy",
                            "content": nancy_answer,
                            "avatar": "👎"
                        })
                        
                        st.session_state.messages.append({
                            "role": "agent",
                            "name": "Optimistic Ollie",
                            "content": ollie_answer,
                            "avatar": "👍"
                        })
                        
                        st.session_state.messages.append({
                            "role": "agent",
                            "name": "Cautious Cat",
                            "content": cat_answer,
                            "avatar": "🐱"
                        })
                        
                        # Reset question state
                        st.session_state.question_submitted = False
                        st.session_state.current_question = ""
                        
                        # Rerun to update display
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error getting answers: {str(e)}")
                    st.exception(e)
    
    with tab2:
        st.title("Property Details")
        if "property_data" in st.session_state and st.session_state.property_data:
            display_property_details(st.session_state.property_data)
        else:
            st.info("No property data available. Enter a URL in the Group Chat tab to view details.")

if __name__ == "__main__":
    main() 
"""
Streamlit web interface for the Domain Property Analyzer.

This module provides a user interface for:
1. Property data input and display
2. Location analysis visualization
3. AI-powered property analysis
4. Results saving functionality
"""

import streamlit as st
import os
from dotenv import load_dotenv
import json

from scraper import DomainScraper
from agent import PropertyAgent
from map import DistanceCalculator


# Page configuration
st.set_page_config(
    page_title="Domain Property Analyzer",
    page_icon="🏠",
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
    .property-details {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .location-header {
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .transport-mode {
        margin-top: 1rem;
    }
    .analysis-tab {
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stTabs {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def format_price(price: int) -> str:
    """
    Format price with commas and dollar sign.
    
    Args:
        price: Property price in dollars
        
    Returns:
        Formatted price string like "$1,500,000"
    """
    return f"${price:,}" if price else "Not specified"

def display_property_details(property_data: dict) -> None:
    """
    Display property details in a structured format.
    
    Args:
        property_data: Dictionary containing scraped property information
    """
    print("\n=== Displaying Property Details ===")
    basic_info = property_data.get('basic_info', {})
    features = property_data.get('features', {})
    address = property_data.get('address', {})
    
    # Create columns for layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Information")
        st.write(f"**Type:** {basic_info.get('property_type', 'Not specified')}")
        st.write(f"**Price:** {format_price(basic_info.get('price'))}")
        st.write(f"**Address:** {address.get('full_address', 'Not specified')}")
    
    with col2:
        st.subheader("Features")
        st.write(f"**Bedrooms:** {features.get('bedrooms', 'Not specified')}")
        st.write(f"**Bathrooms:** {features.get('bathrooms', 'Not specified')}")
        st.write(f"**Parking:** {features.get('parking', 'Not specified')}")
        if features.get('property_size'):
            st.write(f"**Internal Size:** {features['property_size']}m²")
        if features.get('land_size'):
            st.write(f"**Land Size:** {features['land_size']}m²")
    
    # Add description in an expander
    with st.expander("View Full Property Description", expanded=False):
        st.write(property_data.get('description', 'No description available'))
    
    print("✓ Property details displayed successfully")

def display_location_analysis(distance_info: dict) -> None:
    """
    Display location analysis in a structured format.
    
    Args:
        distance_info: Dictionary containing distance and travel time information
                      for different location categories
    """
    if not distance_info:
        return
    
    print("\n=== Displaying Location Analysis ===")
    st.header("Location Analysis", help="Travel times to key locations by different transport modes")
    
    for category, locations in distance_info.items():
        print(f"\nProcessing {category} locations...")
        if not locations:
            if category == "groceries":
                st.subheader("GROCERY STORES")
                st.warning("No major grocery stores found in the immediate area.")
                print("⚠ No grocery stores found")
            continue
            
        st.subheader(f"{category.upper()} LOCATIONS")
        
        # Sort locations by driving time
        sorted_locations = sorted(
            locations,
            key=lambda x: (
                x["modes"]["driving"]["current"]["value"] 
                if x["modes"]["driving"]["current"] 
                else float('inf')
            )
        )
        
        # For groceries, show a warning if no stores were found
        if category == "groceries" and not sorted_locations:
            st.warning("No major grocery stores found in the immediate area.")
            print("⚠ No valid grocery stores after filtering")
            continue
        
        for location in sorted_locations:
            # For grocery stores, use the display name and show full address
            if category == "groceries" and "store_info" in location:
                store_info = location["store_info"]
                expander_title = f"{store_info['display_name']} - {location['distance']['text']}"
                print(f"Displaying store: {store_info['display_name']}")
                
                with st.expander(expander_title):
                    st.markdown(f"**Full Address:** {store_info['formatted_address']}")
                    
                    # Create columns based on available transport modes
                    num_modes = 2  # Default: driving and transit
                    if "walking" in location["modes"]:
                        num_modes = 3
                    
                    cols = st.columns(num_modes)
                    
                    # Display transport modes
                    _display_transport_modes(location, cols)
            else:
                # Regular display for non-grocery locations
                print(f"Displaying location: {location['destination']}")
                with st.expander(f"{location['destination']} - {location['distance']['text']}"):
                    # Create columns based on available transport modes
                    num_modes = 2  # Default: driving and transit
                    if "walking" in location["modes"]:
                        num_modes = 3
                    
                    cols = st.columns(num_modes)
                    
                    # Display transport modes
                    _display_transport_modes(location, cols, include_peak_times=(category == "work"))
    
    print("✓ Location analysis displayed successfully")

def _display_transport_modes(location: dict, cols: list, include_peak_times: bool = False) -> None:
    """
    Helper function to display transport mode information.
    
    Args:
        location: Dictionary containing travel mode information
        cols: List of Streamlit columns for layout
        include_peak_times: Whether to include peak time information (for work locations)
    """
    # Driving times
    with cols[0]:
        st.markdown("**By Car:**")
        driving = location["modes"]["driving"]
        if driving["current"]:
            st.write(f"Current: {driving['current']['text']}")
        if include_peak_times:
            if "morning_peak" in driving and driving["morning_peak"]:
                st.write(f"Morning Peak (9am): {driving['morning_peak']['text']}")
            if "evening_peak" in driving and driving["evening_peak"]:
                st.write(f"Evening Peak (5pm): {driving['evening_peak']['text']}")
    
    # Transit times
    with cols[1]:
        st.markdown("**By Public Transport:**")
        transit = location["modes"]["transit"]
        if transit["current"]:
            st.write(f"Current: {transit['current']['text']}")
            if include_peak_times:
                if "morning_peak" in transit and transit["morning_peak"]:
                    st.write(f"Morning Peak (9am): {transit['morning_peak']['text']}")
                if "evening_peak" in transit and transit["evening_peak"]:
                    st.write(f"Evening Peak (5pm): {transit['evening_peak']['text']}")
        else:
            st.write("No public transport route available")
    
    # Walking times (for groceries and schools)
    if "walking" in location["modes"]:
        with cols[2]:
            st.markdown("**By Walking:**")
            walking = location["modes"]["walking"]
            if walking["current"]:
                st.write(f"Current: {walking['current']['text']}")
            else:
                st.write("No walking route available")

def display_ai_analysis(analysis: dict) -> None:
    """
    Display AI analysis in a tabbed interface.
    
    Args:
        analysis: Dictionary containing AI analysis results
    """
    if not analysis or "error" in analysis:
        st.error(analysis.get("error", "Error displaying analysis"))
        return
    
    try:
        # Parse the JSON string into a dictionary if it's a string
        if isinstance(analysis["analysis"], str):
            try:
                # Clean the string and attempt to parse as JSON
                cleaned_text = analysis["analysis"].strip()
                if cleaned_text.startswith("{") and cleaned_text.endswith("}"):
                    analysis_data = json.loads(cleaned_text)
                else:
                    st.warning("Analysis is not in JSON format. Displaying raw text.")
                    st.write(cleaned_text)
                    return
            except json.JSONDecodeError as e:
                st.error(f"Error parsing analysis JSON: {str(e)}")
                st.write("Raw analysis text:")
                st.write(analysis["analysis"])
                return
        else:
            analysis_data = analysis["analysis"]
        
        # Define tab titles and their corresponding JSON keys
        tabs_config = [
            ("📋 Executive Summary", "executive_summary"),
            ("🏠 Property Analysis", "property_analysis"),
            ("📍 Location Assessment", "location_assessment"),
            ("📈 Market Analysis", "market_analysis"),
            ("👥 Buyer Guide", "buyer_recommendations"),
            ("🔍 Inspection Guide", "inspection_checklist"),
            ("⚠️ Risk Assessment", "risk_assessment")
        ]
        
        # Create tabs
        tab_titles = [config[0] for config in tabs_config]
        tabs = st.tabs(tab_titles)
        
        # Display content in tabs
        for tab, (tab_title, section_key) in zip(tabs, tabs_config):
            with tab:
                section_data = analysis_data.get(section_key)
                if not section_data:
                    st.info(f"No {section_key.replace('_', ' ')} available")
                    continue
                
                # Display section content based on its structure
                if section_key == "executive_summary":
                    if isinstance(section_data, dict):
                        st.write("### Overview")
                        st.write(section_data.get("overview", "No overview available"))
                        
                        st.write("### Key Highlights")
                        highlights = section_data.get("highlights", [])
                        for highlight in highlights:
                            st.write(f"• {highlight}")
                        
                        st.write("### Potential Concerns")
                        concerns = section_data.get("concerns", [])
                        for concern in concerns:
                            st.write(f"• {concern}")
                        
                        st.write("### Recommendation")
                        st.write(section_data.get("recommendation", "No recommendation available"))
                    else:
                        st.write(section_data)
                
                elif section_key in ["property_analysis", "location_assessment", "market_analysis"]:
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            st.write(f"### {key.replace('_', ' ').title()}")
                            st.write(value)
                    else:
                        st.write(section_data)
                
                elif section_key in ["buyer_recommendations", "inspection_checklist", "risk_assessment"]:
                    if isinstance(section_data, dict):
                        for key, items in section_data.items():
                            st.write(f"### {key.replace('_', ' ').title()}")
                            if isinstance(items, list):
                                for item in items:
                                    st.write(f"• {item}")
                            else:
                                st.write(items)
                    else:
                        st.write(section_data)
                
    except Exception as e:
        st.error(f"Error displaying analysis: {str(e)}")
        print(f"⚠ Error displaying analysis: {str(e)}")
        if isinstance(analysis["analysis"], str):
            st.write("Displaying raw analysis:")
            st.write(analysis["analysis"])

def main():
    """Main application entry point."""
    st.title("🏠 Domain Property Analyzer")
    st.markdown("Enter a Domain.com.au property URL to get detailed insights and analysis.")
    
    print("\n=== Starting Domain Property Analyzer ===")
    
    # Load environment variables
    load_dotenv(dotenv_path="config/.env")

    # Get API keys
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    maps_api_key = os.getenv('GOOGLE_MAP_API_KEY')

    # Validate API keys
    if not gemini_api_key:
        st.error("Please set the GEMINI_API_KEY environment variable in config/.env")
        print("⚠ Missing GEMINI_API_KEY")
        return
    
    if not maps_api_key:
        st.error("Please set the GOOGLE_MAP_API_KEY environment variable in config/.env")
        print("⚠ Missing GOOGLE_MAP_API_KEY")
        return

    # Initialize components
    print("Initializing components...")
    scraper = DomainScraper()
    agent = PropertyAgent(gemini_api_key)
    distance_calculator = DistanceCalculator(maps_api_key)
    print("✓ Components initialized")
    
    # URL input
    url = st.text_input("Property URL", placeholder="https://www.domain.com.au/...")
    
    # Analysis options
    col1, col2 = st.columns(2)
    with col1:
        analysis_type = st.radio(
            "Analysis Type",
            ["Quick Summary", "Detailed Analysis"],
            index=1
        )
    
    with col2:
        save_results = st.checkbox("Save results to file", value=False)
    
    if url:
        print(f"\nProcessing URL: {url}")
        with st.spinner("Scraping property data..."):
            try:
                property_data = scraper.get_property_data(url)
                
                if not property_data:
                    st.error("Failed to scrape property data")
                    print("⚠ Failed to scrape property data")
                    return
                
                print("✓ Property data scraped successfully")
                
                # Display property details
                st.header("Property Details")
                display_property_details(property_data)
                
                # Calculate distances
                with st.spinner("Calculating distances to key locations..."):
                    address = property_data.get('address', {}).get('full_address')
                    if address:
                        print(f"\nCalculating distances from: {address}")
                        distance_info = distance_calculator.calculate_distances(address)
                        display_location_analysis(distance_info)
                        print("✓ Distance calculations complete")
                    else:
                        st.warning("Could not calculate distances: No address found")
                        print("⚠ No address found for distance calculations")
                        distance_info = None
                
                # Generate and display analysis
                st.header("AI Analysis")
                with st.spinner("Generating analysis..."):
                    print("\nGenerating AI analysis...")
                    if analysis_type == "Quick Summary":
                        summary = agent.get_quick_summary(property_data)
                        if summary.startswith("Error:"):
                            st.error(summary)
                            print(f"⚠ Error generating summary: {summary}")
                        else:
                            st.success(summary)
                            print("✓ Quick summary generated")
                            
                            if save_results:
                                analysis_result = {
                                    "property_url": url,
                                    "summary": summary,
                                    "property_data": property_data,
                                    "distance_info": distance_info
                                }
                                agent.save_analysis(analysis_result, "quick_summary")
                                print("✓ Results saved to file")
                    else:
                        analysis = agent.analyze_property(property_data, distance_info)
                        if "error" in analysis:
                            st.error(analysis["error"])
                            print(f"⚠ Error generating analysis: {analysis['error']}")
                        else:
                            display_ai_analysis(analysis)
                            print("✓ Detailed analysis generated")
                            
                            if save_results:
                                analysis["property_data"] = property_data
                                analysis["distance_info"] = distance_info
                                agent.save_analysis(analysis, "detailed_analysis")
                                print("✓ Results saved to file")
                
            except Exception as e:
                st.error(f"Error analyzing property: {str(e)}")
                st.exception(e)
                print(f"⚠ Error during analysis: {str(e)}")

if __name__ == "__main__":
    main() 
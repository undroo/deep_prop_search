import streamlit as st
import os
from scraper import DomainScraper
from agent import PropertyAgent
from dotenv import load_dotenv
import json

# Page config
st.set_page_config(
    page_title="Domain Property Analyzer",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS
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
    </style>
""", unsafe_allow_html=True)

def format_price(price):
    """Format price with commas and dollar sign."""
    return f"${price:,}" if price else "Not specified"

def display_property_details(property_data):
    """Display property details in a structured format."""
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
    
    st.subheader("Property Description")
    st.write(property_data.get('description', 'No description available'))

def main():
    st.title("🏠 Domain Property Analyzer")
    st.markdown("Enter a Domain.com.au property URL to get detailed insights and analysis.")
    
    # Load environment variables
    load_dotenv(dotenv_path="config/.env")
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        st.error("Please set the GOOGLE_API_KEY environment variable in config/.env")
        return
    
    # Initialize scraper and agent
    scraper = DomainScraper()
    agent = PropertyAgent(api_key)
    
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
        with st.spinner("Scraping property data..."):
            try:
                property_data = scraper.get_property_data(url)
                
                if not property_data:
                    st.error("Failed to scrape property data")
                    return
                
                # Display property details
                st.header("Property Details")
                display_property_details(property_data)
                
                # Generate and display analysis
                st.header("AI Analysis")
                with st.spinner("Generating analysis..."):
                    if analysis_type == "Quick Summary":
                        summary = agent.get_quick_summary(property_data)
                        if summary.startswith("Error:"):
                            st.error(summary)
                        else:
                            st.success(summary)
                            
                            if save_results:
                                analysis_result = {
                                    "property_url": url,
                                    "summary": summary,
                                    "property_data": property_data
                                }
                                agent.save_analysis(analysis_result, "quick_summary")
                    else:
                        analysis = agent.analyze_property(property_data)
                        if "error" in analysis:
                            st.error(analysis["error"])
                        else:
                            st.markdown(analysis["analysis"])
                            
                            if save_results:
                                analysis["property_data"] = property_data
                                agent.save_analysis(analysis, "detailed_analysis")
                
            except Exception as e:
                st.error(f"Error analyzing property: {str(e)}")
                st.exception(e)

if __name__ == "__main__":
    main() 
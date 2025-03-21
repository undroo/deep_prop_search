import argparse
import os
from scraper import DomainScraper
from agent import PropertyAgent
from dotenv import load_dotenv
from datetime import datetime
from map import DistanceCalculator

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape and analyze Domain.com.au property listings')
    parser.add_argument('url', help='The Domain.com.au property listing URL')
    parser.add_argument('--save', action='store_true', help='Save raw data and analysis to JSON files')
    parser.add_argument('--output', default='property_data', help='Output filename prefix')
    parser.add_argument('--quick', action='store_true', help='Get quick summary instead of full analysis')
    parser.add_argument('--debug', action='store_true', help='Show debug information')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv(dotenv_path="config/.env")
    
    # Get API keys
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    maps_api_key = os.getenv('GOOGLE_MAP_API_KEY')
    
    if not gemini_api_key:
        raise ValueError("Please set the GEMINI_API_KEY environment variable in config/.env")
    
    if not maps_api_key:
        raise ValueError("Please set the GOOGLE_MAP_API_KEY environment variable in config/.env")
    
    # Initialize components
    print("Initializing scraper...")
    scraper = DomainScraper()
    
    print("Initializing Gemini agent...")
    agent = PropertyAgent(gemini_api_key)
    
    print("Initializing distance calculator...")
    distance_calculator = DistanceCalculator(maps_api_key)
    
    try:
        # Scrape property data
        print(f"\nScraping property data from: {args.url}")
        property_data = scraper.get_property_data(args.url)
        
        if not property_data:
            print("Error: Failed to scrape property data")
            return
        
        if args.debug:
            print("\nDebug: Scraped Data Structure:")
            for key, value in property_data.items():
                print(f"{key}:")
                if isinstance(value, dict):
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"  {value}")
        
        # Calculate distances
        print("\nCalculating distances to key locations...")
        address = property_data.get('address', {}).get('full_address')
        distance_info = None
        if address:
            distance_info = distance_calculator.calculate_distances(address)
            if args.debug:
                print("\nDebug: Distance Information:")
                for category, locations in distance_info.items():
                    print(f"\n{category.upper()} LOCATIONS:")
                    for location in locations:
                        print(f"\n{location['destination']}")
                        print(f"Distance: {location['distance']['text']}")
                        print("Travel Times:")
                        for mode, times in location["modes"].items():
                            print(f"  {mode.title()}:")
                            for time_type, time_info in times.items():
                                if time_info:
                                    print(f"    {time_type}: {time_info['text']}")
        else:
            print("Warning: Could not calculate distances - No address found")
        
        # Save raw data if requested
        if args.save:
            print("\nSaving raw data...")
            raw_data = {
                "property_data": property_data,
                "distance_info": distance_info
            }
            scraper.save_results(raw_data, args.output)
        
        # Analyze property
        print("\nAnalyzing property...")
        if args.quick:
            # Get quick summary
            print("Generating quick summary...")
            summary = agent.get_quick_summary(property_data)
            if summary.startswith("Error:"):
                print(f"\nError during quick summary: {summary}")
            else:
                print("\nQuick Summary:")
                print(summary)
                
                # Save quick summary if requested
                if args.save:
                    analysis_result = {
                        "timestamp": datetime.now().isoformat(),
                        "property_url": property_data.get("basic_info", {}).get("url", "Unknown URL"),
                        "summary": summary,
                        "property_data": property_data,
                        "distance_info": distance_info
                    }
                    agent.save_analysis(analysis_result, f"{args.output}_quick")
        else:
            # Get full analysis
            print("Generating detailed analysis...")
            analysis = agent.analyze_property(property_data, distance_info)
            
            if "error" in analysis:
                print(f"\nError during analysis: {analysis['error']}")
            else:
                print("\nDetailed Analysis:")
                print(analysis['analysis'])
                
                # Save analysis if requested
                if args.save:
                    analysis["property_data"] = property_data
                    analysis["distance_info"] = distance_info
                    agent.save_analysis(analysis, args.output)
            
    except Exception as e:
        print(f"\nCritical Error: {str(e)}")
        if args.debug:
            import traceback
            print("\nDebug: Full traceback:")
            print(traceback.format_exc())

if __name__ == "__main__":
    main()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
from scraper import DomainScraper
from agent import PropertyAgent
from map import DistanceCalculator
from datetime import datetime
import traceback
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path="config/.env")

# Initialize FastAPI app
app = FastAPI(
    title="Property Analysis API",
    description="API for analyzing Domain.com.au property listings",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load personas
def load_personas():
    personas = {}
    personas_dir = "Personas"
    for filename in os.listdir(personas_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(personas_dir, filename), 'r') as f:
                content = f.read()
                # Extract persona name from filename (remove .txt and convert to title case)
                name = filename[:-4].replace('_', ' ').title()
                personas[name] = content
    return personas

# Initialize components
try:
    scraper = DomainScraper()
    agent = PropertyAgent(os.getenv('GEMINI_API_KEY'))
    distance_calculator = DistanceCalculator(os.getenv('GOOGLE_MAP_API_KEY'))
    personas = load_personas()
    logger.info(f"All components initialized successfully. Loaded {len(personas)} personas.")
except Exception as e:
    logger.error(f"Failed to initialize components: {str(e)}")
    logger.error(traceback.format_exc())
    raise

class PropertyURL(BaseModel):
    url: str

class AddressRequest(BaseModel):
    address: str

class AnalysisRequest(BaseModel):
    property_data: Dict
    distance_info: Optional[Dict] = None
    quick_summary: bool = False
    save_results: bool = False
    persona: Optional[str] = None  # Name of the persona to use for analysis

@app.get("/")
async def root():
    return {"message": "Property Analysis API is running"}

@app.get("/personas")
async def get_personas():
    """Get list of available personas"""
    return {"personas": list(personas.keys())}

@app.post("/property/scrape")
async def scrape_property(property_url: PropertyURL):
    """Scrape property data from a Domain.com.au URL"""
    try:
        logger.info(f"Scraping property data from URL: {property_url.url}")
        property_data = scraper.get_property_data(property_url.url)
        if not property_data:
            logger.error("Failed to scrape property data - no data returned")
            raise HTTPException(status_code=404, detail="Failed to scrape property data")
        logger.info("Successfully scraped property data")
        return property_data
    except Exception as e:
        logger.error(f"Error in scrape_property: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/property/distances")
async def get_distances(address_request: AddressRequest):
    """Calculate distances to key locations from an address"""
    try:
        logger.info(f"Calculating distances for address: {address_request.address}")
        distance_info = distance_calculator.calculate_distances(address_request.address)
        if not distance_info:
            logger.error("Failed to calculate distances - no data returned")
            raise HTTPException(status_code=500, detail="Failed to calculate distances")
        
        logger.info("Successfully calculated distances")
        return distance_info
    except Exception as e:
        logger.error(f"Error in get_distances: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/property/analyze")
async def analyze_property(request: AnalysisRequest):
    """Perform property analysis using provided property data and distance information"""
    try:
        logger.info("Starting property analysis")
        
        # Validate property data
        if not request.property_data:
            logger.error("No property data provided")
            raise HTTPException(status_code=400, detail="Property data is required")
        
        # Validate persona if specified
        if request.persona and request.persona not in personas:
            logger.error(f"Invalid persona: {request.persona}")
            raise HTTPException(status_code=400, detail=f"Invalid persona. Available personas: {', '.join(personas.keys())}")
        
        # Generate analysis
        try:
            logger.info("Generating analysis")
            if request.quick_summary:
                analysis = agent.get_quick_summary(request.property_data)
            else:
                # If a persona is specified, use their perspective
                if request.persona:
                    logger.info(f"Using persona: {request.persona}")
                    persona_prompt = personas[request.persona]
                    analysis = agent.analyze_property(
                        request.property_data, 
                        request.distance_info,
                        persona_prompt=persona_prompt
                    )
                else:
                    # Get analysis from all personas
                    logger.info("Getting analysis from all personas")
                    analysis = {
                        "timestamp": datetime.now().isoformat(),
                        "property_url": request.property_data.get("basic_info", {}).get("url", "Unknown URL"),
                        "personas": {}
                    }
                    
                    for persona_name, persona_prompt in personas.items():
                        logger.info(f"Getting analysis from {persona_name}")
                        persona_analysis = agent.analyze_property(
                            request.property_data,
                            request.distance_info,
                            persona_prompt=persona_prompt
                        )
                        analysis["personas"][persona_name] = persona_analysis
                    
                    # Add a summary of the discussion
                    analysis["summary"] = "Multiple perspectives have been provided above."
            
            logger.info("Successfully generated analysis")
        except Exception as e:
            logger.error(f"Analysis generation failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
        # Save results if requested
        if request.save_results:
            try:
                logger.info("Saving analysis results")
                if request.quick_summary:
                    agent.save_analysis({
                        "timestamp": datetime.now().isoformat(),
                        "property_url": request.property_data.get("basic_info", {}).get("url", "Unknown URL"),
                        "summary": analysis,
                        "property_data": request.property_data,
                        "distance_info": request.distance_info
                    }, "quick_analysis")
                else:
                    analysis["property_data"] = request.property_data
                    analysis["distance_info"] = request.distance_info
                    agent.save_analysis(analysis, "full_analysis")
                logger.info("Successfully saved analysis results")
            except Exception as e:
                logger.warning(f"Failed to save results: {str(e)}")
                logger.warning(traceback.format_exc())
                # Continue without saving
        
        return analysis
    except Exception as e:
        logger.error(f"Error in analyze_property: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
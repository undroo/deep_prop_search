"""
API routes for the property analysis system.
This module provides endpoints for property analysis, distance calculations, and chat functionality.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import os
import logging
from datetime import datetime
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1",
    tags=["property-analysis"],
    responses={404: {"description": "Not found"}},
)

# Import services after router initialization to avoid circular imports
from ..services.scraper import DomainScraper
from ..services.map import DistanceCalculator
from ..agents.negative_nancy import NegativeNancy
from ..agents.base_agent import BaseAgent

# TODO: Fix an issue where consecutive requests to the API are not being handled correctly.
# Current hypothesis is that once initialized, the service manager is not being re-initialized or can't

class ServiceManager:
    """
    Manages service instances for property analysis.
    This class ensures thread-safe service initialization and access.
    """
    def __init__(self):
        self._scraper = None
        self._distance_calculator = None
        self._negative_nancy = None
        self._lock = None  # Will be used for thread safety if needed

    @property
    def scraper(self) -> DomainScraper:
        """Lazy initialization of DomainScraper."""
        if self._scraper is None:
            logger.info("Initializing DomainScraper")
            self._scraper = DomainScraper()
        return self._scraper

    @property
    def distance_calculator(self) -> DistanceCalculator:
        """Lazy initialization of DistanceCalculator."""
        if self._distance_calculator is None:
            logger.info("Initializing DistanceCalculator")
            self._distance_calculator = DistanceCalculator(os.getenv("GOOGLE_MAP_API_KEY"))
        return self._distance_calculator

    @property
    def negative_nancy(self) -> NegativeNancy:
        """Lazy initialization of NegativeNancy."""
        if self._negative_nancy is None:
            logger.info("Starting NegativeNancy initialization")
            api_key = os.getenv("GEMINI_API_KEY")
            logger.info(f"API Key present: {'Yes' if api_key else 'No'}")
            if not api_key:
                logger.error("GEMINI_API_KEY environment variable is not set")
                raise ValueError("GEMINI_API_KEY environment variable is not set")
            try:
                logger.info("Creating NegativeNancy instance")
                self._negative_nancy = NegativeNancy(api_key)
                logger.info("NegativeNancy instance created successfully")
            except Exception as e:
                logger.error(f"Failed to initialize NegativeNancy: {str(e)}", exc_info=True)
                raise
        return self._negative_nancy

@lru_cache()
def get_service_manager() -> ServiceManager:
    """
    Dependency injection function for ServiceManager.
    Uses lru_cache to ensure we only create one instance per process.
    """
    return ServiceManager()

class PropertyInitializationRequest(BaseModel):
    """
    Request model for property initialization.
    
    Attributes:
        url (str): The Domain.com.au property URL to analyze
        categories (Optional[List[str]]): List of categories for distance calculations
            (e.g., ["school", "train", "shopping"])
    """
    url: str
    categories: Optional[List[str]] = None

class PropertyInitializationResponse(BaseModel):
    """
    Response model for property initialization.
    
    Attributes:
        session_id (str): Unique identifier for the analysis session
        status (str): Current status of the initialization ("ready" or "error")
        property_data (Optional[Dict]): Scraped property data if available
        distance_info (Optional[Dict]): Distance calculations if available
        error (Optional[str]): Error message if initialization failed
    """
    session_id: str
    status: str
    property_data: Optional[Dict] = None
    distance_info: Optional[Dict] = None
    error: Optional[str] = None

class AnalysisRequest(BaseModel):
    """
    Request model for property analysis.
    
    Attributes:
        property_data (Dict): The property data to analyze
        distance_info (Optional[Dict]): Distance calculations data
        agent (str): The agent to use for analysis (e.g., "negative_nancy")
        chat_history (Optional[List[Dict[str, Any]]]): Chat history for the analysis
        current_question (Optional[str]): Current question for the analysis
    """
    property_data: Dict
    distance_info: Optional[Dict] = None
    agent: str
    chat_history: Optional[List[Dict[str, Any]]] = None
    current_question: Optional[str] = None

class AnalysisResponse(BaseModel):
    """
    Response model for property analysis.
    
    Attributes:
        analysis (Dict): The analysis data from the agent, containing structured information
        timestamp (str): When the analysis was performed
        agent (str): The agent used for the analysis
    """
    analysis: Dict
    timestamp: str
    agent: str

# In-memory storage for analysis sessions (replace with database in production)
analysis_sessions: Dict[str, Dict] = {}

@router.post("/initialize", response_model=PropertyInitializationResponse)
async def initialize_property(
    request: PropertyInitializationRequest,
    service_manager: ServiceManager = Depends(get_service_manager)
) -> PropertyInitializationResponse:
    """
    Initialize property analysis for a given URL.
    
    This endpoint:
    1. Creates a new analysis session
    2. Scrapes property data
    3. Calculates distances to points of interest
    4. Returns the complete analysis data
    
    Args:
        request (PropertyInitializationRequest): The initialization request containing the property URL
        service_manager (ServiceManager): Service manager instance
    
    Returns:
        PropertyInitializationResponse: Response containing the session ID and analysis data
    
    Note:
        For invalid URLs, the endpoint will return a 200 status code with an error message
        in the response body rather than raising an HTTPException.
    """
    try:
        # Generate session ID (using timestamp for simplicity)
        session_id = str(datetime.now().timestamp())
        logger.info(f"Starting property analysis for URL: {request.url}")
        
        # Initialize session
        analysis_sessions[session_id] = {
            "status": "initializing",
            "created_at": datetime.now().isoformat(),
            "url": request.url
        }
        
        # Validate URL format
        if not request.url.startswith("https://www.domain.com.au/"):
            error_msg = "Invalid URL format. URL must be from domain.com.au"
            logger.warning(f"Invalid URL format for session {session_id}: {request.url}")
            analysis_sessions[session_id].update({
                "status": "error",
                "error": error_msg
            })
            return PropertyInitializationResponse(
                session_id=session_id,
                status="error",
                error=error_msg
            )
        
        # Scrape property data
        logger.info(f"Starting property data scraping for session {session_id}")
        property_data = service_manager.scraper.get_property_data(request.url)
        
        if not property_data:
            error_msg = "Failed to fetch property data. The URL may be invalid or the property listing may no longer exist."
            logger.warning(f"Failed to fetch property data for session {session_id}: {request.url}")
            analysis_sessions[session_id].update({
                "status": "error",
                "error": error_msg
            })
            return PropertyInitializationResponse(
                session_id=session_id,
                status="error",
                error=error_msg
            )
        
        logger.info(f"Successfully scraped property data for session {session_id}")
        
        # Calculate distances if address is available
        distance_info = None
        if "address" in property_data and "full_address" in property_data["address"]:
            logger.info(f"Calculating distances for session {session_id}")
            distance_info = service_manager.distance_calculator.calculate_distances(
                property_data["address"]["full_address"],
                request.categories
            )
            logger.info(f"Successfully calculated distances for session {session_id}")
        
        # Update session with results
        analysis_sessions[session_id].update({
            "status": "ready",
            "property_data": property_data,
            "distance_info": distance_info,
            "initialized_at": datetime.now().isoformat()
        })
        
        logger.info(f"Successfully initialized property analysis for session {session_id}")
        
        return PropertyInitializationResponse(
            session_id=session_id,
            status="ready",
            property_data=property_data,
            distance_info=distance_info
        )
        
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.error(f"Error initializing property analysis for session {session_id}: {str(e)}", exc_info=True)
        if session_id in analysis_sessions:
            analysis_sessions[session_id].update({
                "status": "error",
                "error": error_msg
            })
        
        return PropertyInitializationResponse(
            session_id=session_id,
            status="error",
            error=error_msg
        )

def get_agent(agent_name: str) -> Optional[BaseAgent]:
    """Get the appropriate agent instance based on the agent name."""
    service_manager = get_service_manager()
    if agent_name == "negative_nancy":
        return service_manager.negative_nancy
    return None

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_property(request: AnalysisRequest):
    """Analyze a property using the specified agent."""
    try:
        # Get the appropriate agent
        agent = get_agent(request.agent)
        if not agent:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {request.agent}")

        # Perform the analysis
        analysis_result = agent.analyze_property(
            property_data=request.property_data,
            distance_info=request.distance_info,
            chat_history=request.chat_history,
            current_question=request.current_question
        )

        # Add metadata
        analysis_result['timestamp'] = datetime.now().isoformat()
        analysis_result['agent'] = request.agent

        return AnalysisResponse(
            analysis=analysis_result,
            timestamp=analysis_result['timestamp'],
            agent=request.agent
        )

    except Exception as e:
        logger.error(f"Error in analyze_property: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def root():
    return {"message": "Root endpoint"}

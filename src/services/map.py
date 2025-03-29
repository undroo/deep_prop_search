"""
Handles distance calculations between property locations and points of interest using Google Maps Routes API.

This module provides functionality to:
1. Find specific grocery store locations in a suburb using Places API
2. Calculate travel times using different transport modes (driving, transit, walking)
3. Handle peak hour calculations for work locations
4. Format and summarize distance/time information
"""

import requests
from typing import Dict, List, Optional, Tuple
import os
from datetime import datetime, timedelta
from ..utils.locations import LOCATIONS

class DistanceCalculator:
    # Constants for API endpoints
    ROUTES_API_ENDPOINT = "https://routes.googleapis.com/directions/v2:computeRoutes"
    PLACES_API_ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
    
    # Constants for time calculations
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_MINUTE = 60
    
    def __init__(self, api_key: str):
        """
        Initialize the distance calculator with Google Maps API key.
        
        Args:
            api_key: Google Maps API key (GOOGLE_MAP_API_KEY)
        """
        print("\n=== Initializing Distance Calculator ===")
        self.api_key = api_key
        self.base_url = self.ROUTES_API_ENDPOINT
        self.places_url = self.PLACES_API_ENDPOINT
        print("✓ Google Maps Routes client initialized successfully")
    
    def _get_suburb_from_address(self, address: str) -> str:
        """
        Extract suburb from full address.
        
        Args:
            address: Full property address
            
        Returns:
            Suburb name or empty string if not found
        """
        try:
            # Assuming address format: "Street, Suburb NSW Postcode"
            parts = address.split(',')
            if len(parts) >= 2:
                suburb = parts[1].strip().split()[0]  # Take first word after comma
                print(f"✓ Extracted suburb: {suburb}")
                return suburb
            print("⚠ No suburb found in address")
            return ""
        except Exception as e:
            print(f"⚠ Error extracting suburb: {e}")
            return ""
    
    def _get_grocery_locations(self, property_address: str) -> List[Dict[str, str]]:
        """
        Get grocery store locations with specific addresses using Places API.
        
        Args:
            property_address: The full property address
        
        Returns:
            List of dictionaries containing:
                - name: Original store chain name
                - display_name: Store name from Places API
                - formatted_address: Full address from Places API
        """
        suburb = self._get_suburb_from_address(property_address)
        if not suburb:
            return []
        
        print(f"\n=== Searching for grocery stores in {suburb} ===")
        grocery_locations = []
        seen_addresses = set()  # Track unique addresses to avoid duplicates
        
        for store in LOCATIONS["groceries"]:
            search_query = f"{store} {suburb}, NSW"
            print(f"\nSearching for: {search_query}")
            
            try:
                # Call Places API to get specific store address
                headers = {
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                    "X-Goog-FieldMask": "places.formattedAddress,places.displayName"
                }
                
                body = {
                    "textQuery": search_query,
                    "maxResultCount": 3  # Get up to 3 results to handle duplicates
                }
                
                response = requests.post(
                    self.places_url,
                    json=body,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "places" in data and data["places"]:
                        # Try each result until we find a new, valid store
                        found_valid_store = False
                        for place in data["places"]:
                            address = place.get("formattedAddress", "")
                            display_name = place.get("displayName", {}).get("text", store)
                            
                            # Validation checks
                            if address in seen_addresses:
                                print(f"  ⚠ Skipping duplicate address: {address}")
                                continue
                                
                            if suburb.lower() not in address.lower():
                                print(f"  ⚠ Address not in target suburb: {address}")
                                continue
                                
                            if store.lower() not in display_name.lower():
                                print(f"  ⚠ Not a {store} store: {display_name}")
                                continue
                            
                            # Add the store if it passes all checks
                            grocery_locations.append({
                                "name": store,
                                "display_name": display_name,
                                "formatted_address": address
                            })
                            seen_addresses.add(address)
                            found_valid_store = True
                            print(f"  ✓ Found store: {display_name}")
                            print(f"    Address: {address}")
                            break
                        
                        if not found_valid_store:
                            print(f"  ⚠ No valid {store} found in {suburb}")
                    else:
                        print(f"  ⚠ No {store} found in {suburb}")
                else:
                    print(f"  ⚠ API Error ({response.status_code}): {response.text}")
            
            except Exception as e:
                print(f"  ⚠ Error searching for {store}: {e}")
        
        print(f"\nFound {len(grocery_locations)} valid grocery stores in {suburb}")
        return grocery_locations
    
    def _get_travel_time(self, origin: str, destination: str, mode: str, departure_time: datetime) -> Optional[Dict]:
        """
        Get travel time between two points using Routes API.
        
        Args:
            origin: Starting address
            destination: Ending address
            mode: Transport mode ('DRIVE', 'TRANSIT', or 'WALK')
            departure_time: When the journey starts
        """
        try:
            print(f"Requesting {mode} route from Google Maps API:")
            print(f"  From: {origin}")
            print(f"  To: {destination}")
            print(f"  Departure: {departure_time.strftime('%Y-%m-%d %H:%M')}")
            
            # Prepare the request body
            request_body = {
                "origin": {
                    "address": origin
                },
                "destination": {
                    "address": destination
                },
                "travelMode": mode,
                "computeAlternativeRoutes": False,
                "languageCode": "en-US",
                "units": "METRIC"
            }
            
            # Add traffic awareness for driving mode
            if mode == "DRIVE":
                request_body.update({
                    "routingPreference": "TRAFFIC_AWARE",
                    "departureTime": departure_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "routeModifiers": {
                        "avoidTolls": False,
                        "avoidHighways": False,
                        "avoidFerries": False
                    }
                })
            # Add departure time for transit mode
            elif mode == "TRANSIT":
                request_body.update({
                    "departureTime": departure_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                })
            
            # Make the API request
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs"
            }
            
            response = requests.post(
                self.base_url,
                json=request_body,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if "routes" in data and data["routes"]:
                    route = data["routes"][0]
                    duration_seconds = int(route["duration"].rstrip('s'))  # Remove 's' from duration string
                    distance_meters = route["distanceMeters"]
                    
                    # Convert duration to human-readable format
                    hours = duration_seconds // self.SECONDS_PER_HOUR
                    minutes = (duration_seconds % self.SECONDS_PER_HOUR) // self.SECONDS_PER_MINUTE
                    duration_text = f"{hours} hr {minutes} min" if hours > 0 else f"{minutes} min"
                    
                    # Convert distance to human-readable format
                    distance_km = round(distance_meters / 1000, 1)
                    distance_text = f"{distance_km} km"
                    
                    print(f"  Success: {duration_text} by {mode}")
                    return {
                        "text": duration_text,
                        "value": duration_seconds
                    }
            else:
                print(f"  Error: API returned status code {response.status_code}")
                print(f"  Response: {response.text}")
            
            print(f"  Error: No route found for {mode}")
            return None
            
        except Exception as e:
            print(f"  Error calculating {mode} time: {e}")
            return None
    
    def calculate_distances(self, property_address: str, categories: Optional[List[str]] = None) -> Dict:
        """
        Calculate distances from property to specified locations.
        
        Args:
            property_address: The address of the property
            categories: List of location categories to check (e.g., ["work", "groceries"])
                       If None, checks all categories
        
        Returns:
            Dictionary containing distances and travel times to each location
        """
        print(f"\nCalculating distances from: {property_address}")
        
        if not categories:
            categories = LOCATIONS.keys()
        
        results = {}
        
        # Get times for different scenarios
        current_time = datetime.now()
        next_business_day = current_time + timedelta(days=1)
        morning_peak = next_business_day.replace(hour=9, minute=0, second=0)
        evening_peak = next_business_day.replace(hour=17, minute=0, second=0)
        
        for category in categories:
            print(f"\nProcessing category: {category}")
            category_results = []
            
            # Get locations based on category
            if category == "groceries":
                locations = self._get_grocery_locations(property_address)
                print(f"Found {len(locations)} grocery stores in suburb")
                # For groceries, use the formatted_address from Places API
                destinations = [loc["formatted_address"] for loc in locations]
            else:
                locations = LOCATIONS.get(category, [])
                print(f"Processing {len(locations)} {category} locations")
                destinations = locations
            
            for idx, destination in enumerate(destinations):
                print(f"\nCalculating times to: {destination}")
                try:
                    # Get initial route for distance
                    initial_route = self._get_travel_time(
                        property_address,
                        destination,
                        "DRIVE",
                        current_time
                    )
                    
                    if initial_route:
                        result = {
                            "destination": destination,
                            "distance": {
                                "text": initial_route["text"],
                                "value": initial_route["value"]
                            },
                            "modes": {
                                "driving": {
                                    "current": self._get_travel_time(
                                        property_address, destination, "DRIVE", current_time
                                    )
                                }
                            }
                        }
                        
                        # For groceries, add the display name and formatted address
                        if category == "groceries":
                            result.update({
                                "store_info": {
                                    "name": locations[idx]["name"],
                                    "display_name": locations[idx]["display_name"],
                                    "formatted_address": locations[idx]["formatted_address"]
                                }
                            })
                        
                        # Add transit times for all categories
                        result["modes"]["transit"] = {
                            "current": self._get_travel_time(
                                property_address, destination, "TRANSIT", current_time
                            )
                        }
                        
                        # Add walking times for groceries and schools
                        if category in ["groceries", "schools"]:
                            result["modes"]["walking"] = {
                                "current": self._get_travel_time(
                                    property_address, destination, "WALK", current_time
                                )
                            }
                        
                        # Add peak times for work locations
                        if category == "work":
                            result["modes"]["driving"]["morning_peak"] = self._get_travel_time(
                                property_address, destination, "DRIVE", morning_peak
                            )
                            result["modes"]["driving"]["evening_peak"] = self._get_travel_time(
                                property_address, destination, "DRIVE", evening_peak
                            )
                            result["modes"]["transit"]["morning_peak"] = self._get_travel_time(
                                property_address, destination, "TRANSIT", morning_peak
                            )
                            result["modes"]["transit"]["evening_peak"] = self._get_travel_time(
                                property_address, destination, "TRANSIT", evening_peak
                            )
                        
                        category_results.append(result)
                        print(f"Successfully calculated times for {destination}")
                
                except Exception as e:
                    print(f"Error calculating distance to {destination}: {e}")
            
            if category_results:
                results[category] = category_results
        
        return results
    
    def get_nearest_locations(self, property_address: str, limit: int = 1) -> Dict[str, List[Dict]]:
        """
        Get the nearest locations for each category.
        
        Args:
            property_address: The address of the property
            limit: Number of nearest locations to return per category
        
        Returns:
            Dictionary with categories and their nearest locations
        """
        all_distances = self.calculate_distances(property_address)
        nearest_locations = {}
        
        for category, locations in all_distances.items():
            # Sort locations by distance value
            sorted_locations = sorted(
                locations,
                key=lambda x: x["distance"]["value"]
            )
            nearest_locations[category] = sorted_locations[:limit]
        
        return nearest_locations
    
    def format_distance_summary(self, distances: Dict) -> str:
        """
        Create a human-readable summary of distances.
        
        Args:
            distances: Dictionary of distance results
            
        Returns:
            Formatted string with distance summary
        """
        summary = []
        
        for category, locations in distances.items():
            if not locations:
                continue
                
            summary.append(f"\n{category.upper()} LOCATIONS:")
            # Sort locations by driving time
            sorted_locations = sorted(
                locations,
                key=lambda x: x["modes"]["driving"]["current"]["value"] if x["modes"]["driving"]["current"] else float('inf')
            )
            
            for location in sorted_locations:
                summary.append(f"\n{location['destination']}")
                summary.append(f"Distance: {location['distance']['text']}")
                
                # Add driving times
                driving = location["modes"]["driving"]
                transit = location["modes"]["transit"]
                
                summary.append("\nBy Car:")
                if driving["current"]:
                    summary.append(f"  Current: {driving['current']['text']}")
                if "morning_peak" in driving and driving["morning_peak"]:
                    summary.append(f"  Morning Peak (9am): {driving['morning_peak']['text']}")
                if "evening_peak" in driving and driving["evening_peak"]:
                    summary.append(f"  Evening Peak (5pm): {driving['evening_peak']['text']}")
                
                summary.append("\nBy Public Transport:")
                if transit["current"]:
                    summary.append(f"  Current: {transit['current']['text']}")
                if "morning_peak" in transit and transit["morning_peak"]:
                    summary.append(f"  Morning Peak (9am): {transit['morning_peak']['text']}")
                if "evening_peak" in transit and transit["evening_peak"]:
                    summary.append(f"  Evening Peak (5pm): {transit['evening_peak']['text']}")
                
                # Add walking times for groceries and schools
                if "walking" in location["modes"]:
                    walking = location["modes"]["walking"]
                    summary.append("\nBy Walking:")
                    if walking["current"]:
                        summary.append(f"  Current: {walking['current']['text']}")
                
                summary.append("-" * 50)

    def _format_duration(self, duration_seconds: int) -> str:
        """
        Convert duration from seconds to human-readable format.
        
        Args:
            duration_seconds: Time duration in seconds
            
        Returns:
            Formatted string like "2 hr 30 min" or "45 min"
        """
        hours = duration_seconds // self.SECONDS_PER_HOUR
        minutes = (duration_seconds % self.SECONDS_PER_HOUR) // self.SECONDS_PER_MINUTE
        return f"{hours} hr {minutes} min" if hours > 0 else f"{minutes} min"

    def _format_distance(self, meters: int) -> str:
        """
        Convert distance from meters to human-readable format.
        
        Args:
            meters: Distance in meters
            
        Returns:
            Formatted string like "5.2 km"
        """
        return f"{round(meters / 1000, 1)} km" 
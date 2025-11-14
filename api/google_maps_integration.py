"""
Google Maps API Integration

This module provides integration with Google Maps API for location and directions.
"""

import os
import aiohttp
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import quote

class GoogleMapsAPI:
    """Google Maps API client for directions and location services"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    async def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "walking",
        alternatives: bool = True
    ) -> Dict[str, Any]:
        """
        Get directions from origin to destination
        
        Args:
            origin: Starting location (address or place name)
            destination: Destination (address or place name)
            mode: Travel mode (walking, driving, transit, bicycling)
            alternatives: Whether to include alternative routes
            
        Returns:
            Directions data with routes, duration, and distance
        """
        if not self.api_key:
            return {
                "error": "Google Maps API key not configured",
                "text_directions": f"Navigate from {origin} to {destination}"
            }
        
        url = f"{self.base_url}/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "alternatives": str(alternatives).lower(),
            "key": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_place_details(self, place_name: str) -> Dict[str, Any]:
        """
        Get details about a place
        
        Args:
            place_name: Name of the place
            
        Returns:
            Place details including address, coordinates, etc.
        """
        if not self.api_key:
            return {"error": "Google Maps API key not configured"}
        
        # First, find the place
        search_url = f"{self.base_url}/place/findplacefromtext/json"
        search_params = {
            "input": place_name,
            "inputtype": "textquery",
            "fields": "place_id,name,formatted_address,geometry",
            "key": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("candidates"):
                            place = data["candidates"][0]
                            
                            # Get detailed information
                            details_url = f"{self.base_url}/place/details/json"
                            details_params = {
                                "place_id": place["place_id"],
                                "fields": "name,formatted_address,geometry,opening_hours,website,formatted_phone_number",
                                "key": self.api_key
                            }
                            
                            async with session.get(details_url, params=details_params) as details_response:
                                if details_response.status == 200:
                                    return await details_response.json()
                        
                        return {"error": "Place not found"}
                    else:
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_travel_time(
        self,
        origin: str,
        destination: str,
        mode: str = "walking"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Get estimated travel time and distance
        
        Args:
            origin: Starting location
            destination: Destination
            mode: Travel mode
            
        Returns:
            Tuple of (duration_text, distance_text)
        """
        directions = await self.get_directions(origin, destination, mode)
        
        if "error" in directions or "routes" not in directions or not directions["routes"]:
            return None, None
        
        route = directions["routes"][0]
        leg = route["legs"][0]
        
        return leg.get("duration", {}).get("text"), leg.get("distance", {}).get("text")
    
    def format_directions_text(self, directions_data: Dict[str, Any]) -> str:
        """
        Format directions data into readable text
        
        Args:
            directions_data: Raw directions data from API
            
        Returns:
            Formatted text directions
        """
        if "error" in directions_data:
            return f"Unable to get directions: {directions_data['error']}"
        
        if "routes" not in directions_data or not directions_data["routes"]:
            return "No routes found"
        
        route = directions_data["routes"][0]
        leg = route["legs"][0]
        
        # Build formatted directions
        lines = []
        lines.append(f"📍 From: {leg['start_address']}")
        lines.append(f"📍 To: {leg['end_address']}")
        lines.append(f"⏱️  Duration: {leg['duration']['text']}")
        lines.append(f"📏 Distance: {leg['distance']['text']}")
        lines.append("")
        lines.append("🚶 Directions:")
        
        for i, step in enumerate(leg["steps"], 1):
            # Remove HTML tags from instructions
            instruction = step["html_instructions"]
            instruction = instruction.replace("<b>", "").replace("</b>", "")
            instruction = instruction.replace("<div>", " ").replace("</div>", "")
            instruction = instruction.replace("&nbsp;", " ")
            
            lines.append(f"{i}. {instruction} ({step['duration']['text']})")
        
        return "\n".join(lines)
    
    async def get_nearby_places(
        self,
        location: str,
        place_type: str = "restaurant",
        radius: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Find nearby places of a certain type
        
        Args:
            location: Center location
            place_type: Type of places (restaurant, cafe, etc.)
            radius: Search radius in meters
            
        Returns:
            List of nearby places
        """
        if not self.api_key:
            return []
        
        # First get coordinates of location
        place_details = await self.get_place_details(location)
        
        if "error" in place_details or "result" not in place_details:
            return []
        
        coords = place_details["result"]["geometry"]["location"]
        location_str = f"{coords['lat']},{coords['lng']}"
        
        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            "location": location_str,
            "radius": radius,
            "type": place_type,
            "key": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
                    else:
                        return []
        except Exception as e:
            return []


# Singleton instance
google_maps_api = GoogleMapsAPI()

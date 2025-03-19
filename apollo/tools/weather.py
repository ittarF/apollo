"""
Weather-related tools for the Agent Framework.
"""

import requests
from typing import Dict, Any, Optional, Union


def get_weather(latitude: Union[float, str], longitude: Union[float, str]) -> Dict[str, Any]:
    """
    Get current weather data for a location using the Open-Meteo API.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary with current weather data
    """
    # Convert string coordinates to float if needed
    if isinstance(latitude, str):
        latitude = float(latitude)
    if isinstance(longitude, str):
        longitude = float(longitude)
        
    # Validate coordinates
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return {
            "error": "Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180."
        }
    
    # Format coordinates to 4 decimal places
    lat = round(latitude, 4)
    lon = round(longitude, 4)
    
    try:
        # Call Open-Meteo API (free, no API key required)
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,wind_speed_10m,wind_direction_10m",
            "hourly": "temperature_2m,relative_humidity_2m",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        # Extract current weather
        current = data.get("current", {})
        
        if not current:
            return {
                "error": "No weather data available for these coordinates."
            }
        
        # Format the response
        result = {
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "current": {
                "temperature": {
                    "value": current.get("temperature_2m"),
                    "unit": data.get("current_units", {}).get("temperature_2m", "°C")
                },
                "feels_like": {
                    "value": current.get("apparent_temperature"),
                    "unit": data.get("current_units", {}).get("apparent_temperature", "°C")
                },
                "humidity": {
                    "value": current.get("relative_humidity_2m"),
                    "unit": data.get("current_units", {}).get("relative_humidity_2m", "%")
                },
                "precipitation": {
                    "value": current.get("precipitation"),
                    "unit": data.get("current_units", {}).get("precipitation", "mm")
                },
                "wind": {
                    "speed": {
                        "value": current.get("wind_speed_10m"),
                        "unit": data.get("current_units", {}).get("wind_speed_10m", "km/h")
                    },
                    "direction": {
                        "value": current.get("wind_direction_10m"),
                        "unit": data.get("current_units", {}).get("wind_direction_10m", "°")
                    }
                },
                "time": current.get("time")
            }
        }
        
        return result
    except Exception as e:
        return {
            "error": f"Error fetching weather data: {str(e)}"
        }


def get_geocoding(location: str) -> Dict[str, Any]:
    """
    Get geocoding data (coordinates) for a location name.
    
    Args:
        location: Location name (city, address, etc.)
        
    Returns:
        Dictionary with location data including coordinates
    """
    try:
        # Call Open-Meteo Geocoding API
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": location,
            "count": 5,
            "language": "en",
            "format": "json"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        results = data.get("results", [])
        
        if not results:
            return {
                "error": f"No location found for '{location}'."
            }
        
        # Format the response
        locations = []
        for result in results:
            locations.append({
                "name": result.get("name"),
                "display_name": f"{result.get('name')}, {result.get('country')}",
                "country": result.get("country"),
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude"),
                "timezone": result.get("timezone")
            })
            
        return {
            "query": location,
            "locations": locations
        }
    except Exception as e:
        return {
            "error": f"Error fetching geocoding data: {str(e)}"
        } 
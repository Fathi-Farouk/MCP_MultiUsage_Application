from mcp.server.fastmcp import FastMCP
import requests
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
if not API_KEY:
    raise RuntimeError("WEATHERAPI_KEY is missing")

BASE_URL = "https://api.weatherapi.com/v1"

mcp = FastMCP("WeatherAPI MCP Server")


# --------------------------------------------------
# Safe HTTP helper (MANDATORY for MCP)
# --------------------------------------------------
def safe_request(endpoint: str, params: dict) -> dict:
    try:
        params["key"] = API_KEY
        resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {
            "error": "WeatherAPI request failed",
            "details": str(e)
        }


# --------------------------------------------------
# Tool 1: Current Weather
# --------------------------------------------------
@mcp.tool()
def get_current_weather(city: str) -> dict:
    """
    Get current weather for a city.
    """
    data = safe_request(
        "current.json",
        {"q": city}
    )

    if "error" in data:
        return data

    return {
        "city": city,
        "country": data["location"]["country"],
        "local_time": data["location"]["localtime"],
        "temperature_c": data["current"]["temp_c"],
        "condition": data["current"]["condition"]["text"],
        "wind_kph": data["current"]["wind_kph"],
        "humidity": data["current"]["humidity"]
    }


# --------------------------------------------------
# Tool 2: Weather Forecast
# --------------------------------------------------
@mcp.tool()
def get_weather_forecast(
    city: str,
    days: Optional[int] = 3
) -> dict:
    """
    Get weather forecast for a city (daily).
    """
    data = safe_request(
        "forecast.json",
        {
            "q": city,
            "days": days
        }
    )

    if "error" in data:
        return data

    forecast = []
    for day in data["forecast"]["forecastday"]:
        forecast.append({
            "date": day["date"],
            "temp_max_c": day["day"]["maxtemp_c"],
            "temp_min_c": day["day"]["mintemp_c"],
            "condition": day["day"]["condition"]["text"]
        })

    return {
        "city": city,
        "country": data["location"]["country"],
        "forecast": forecast
    }


if __name__ == "__main__":
    # IMPORTANT: no stdout printing in stdio MCP servers
    mcp.run()
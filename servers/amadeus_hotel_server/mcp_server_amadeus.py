# mcp_server_amadeus.py
from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

# -------------------------------------------------
# Environment
# -------------------------------------------------
load_dotenv()

AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
AMADEUS_BASE_URL = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com")

if not AMADEUS_API_KEY or not AMADEUS_API_SECRET:
    raise RuntimeError("Missing Amadeus credentials in .env")

# -------------------------------------------------
# MCP Server
# -------------------------------------------------
mcp = FastMCP("Amadeus Hotel MCP Server")

# -------------------------------------------------
# OAuth Token Helper (Server-side only)
# -------------------------------------------------
def get_amadeus_token() -> str:
    url = f"{AMADEUS_BASE_URL}/v1/security/oauth2/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET,
    }

    response = requests.post(url, data=payload, timeout=10)
    response.raise_for_status()

    return response.json()["access_token"]

# -------------------------------------------------
# MCP Tool: Hotel Search by City
# -------------------------------------------------
@mcp.tool()
def search_hotels_by_city(city_code: str) -> dict:
    """
    Search hotels by IATA city code (e.g. RUH, DXB, CAI)
    """
    token = get_amadeus_token()

    url = f"{AMADEUS_BASE_URL}/v1/reference-data/locations/hotels/by-city"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"cityCode": city_code}

    r = requests.get(url, headers=headers, params=params, timeout=10)
    r.raise_for_status()

    return r.json()

if __name__ == "__main__":
    mcp.run()
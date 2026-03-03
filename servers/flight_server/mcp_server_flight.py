#######################################
#✅ Python MCP SDK (FastMCP)
#✅ JSON-RPC 2.0
#✅ STDIO transport
#✅ aviationstack API
#❌ No LangChain (by design)
#######################################

from mcp.server.fastmcp import FastMCP
from typing import Optional
import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
if not API_KEY:
    raise RuntimeError("AVIATIONSTACK_API_KEY is missing")

BASE_URL = "http://api.aviationstack.com/v1"
mcp = FastMCP("Aviationstack MCP Server")


def safe_request(url, params):
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": "Aviationstack API failure", "details": str(e)}


@mcp.tool()
def search_flights(
    dep_iata: Optional[str] = None,
    arr_iata: Optional[str] = None,
    airline_iata: Optional[str] = None
) -> dict:
    params = {
        "access_key": API_KEY,
        "dep_iata": dep_iata,
        "arr_iata": arr_iata,
        "airline_iata": airline_iata
    }
    params = {k: v for k, v in params.items() if v}
    return safe_request(f"{BASE_URL}/flights", params)


@mcp.tool()
def get_airport_info(iata_code: str) -> dict:
    params = {"access_key": API_KEY, "iata_code": iata_code}
    data = safe_request(f"{BASE_URL}/airports", params)

    if "error" in data:
        return data
    if not data.get("data"):
        return {"message": "No airport found"}
    return data["data"][0]


if __name__ == "__main__":
    # IMPORTANT: don't print to stdout in stdio MCP servers
    # If you really want a message, do stderr:
    # print("Flight MCP server started", file=sys.stderr)
    mcp.run()
# 🌍 MCP Multi-Server Travel Advisor

A production-style AI Travel Planning system built using **Model Context Protocol (MCP)** with multiple independent MCP servers and a unified client orchestrator.

---

## 🚀 Project Overview

This project demonstrates a real-world AI architecture where:

- A Large Language Model (GPT-4o)
- Communicates through an MCP Client
- Which orchestrates multiple independent MCP Servers
- Each server integrates with an external API

The system supports:

- 🌤 Weather lookup (Open-Meteo API)
- ✈ Flight search
- 🏨 Hotel search (Amadeus API)

---

## 🏗 Architecture

User Query  
↓  
LLM (GPT-4o)  
↓  
MCP Client (JSON-RPC Adapter)  
↓  
Multiple MCP Servers  
- Weather Server  
- Flight Server  
- Hotel Server  
↓  
External APIs  

---

## 🧠 Why MCP?

Traditional tool integration requires M × N connections  
(M models × N tools).

Using MCP, we solve this complexity by:

- Standardizing communication with JSON-RPC 2.0
- Isolating tools in independent servers
- Allowing plug-and-play architecture

---

## 🔧 Technologies Used

- Python
- FastMCP
- JSON-RPC 2.0
- Asyncio
- OpenAI GPT-4o
- External Travel APIs

---

## Project Specification

- SDK --> Official SDKs for building with Model Context Protocol is python modelcontextprotocol/python-sdk
- External_APIs:  
            - **WEATHER_API**: for weather information --> https://www.weatherapi.com/  
            - **AVIATIONSTACK_API**: for flight information --> https://aviationstack.com/  
            - **AMADEUS_API** : for Hotel reservation --> https://developers.amadeus.com/  
- MCP_CLient:  
            - **framework**: LangChain  
            - **MCP Server_files**: exist in MultiServerMCPClient for all mcp_server python files  
            - **LLM used** : "OPENAI_MODEL", "gpt-4o"
            - **LLM API Key** : load from .env file  
- MCP_Server:  
            - **Tools** API Call from .env file  
            - **@mcp.tool()** --> that contain Mapping function for [Tool Structure <--> JSON RPC 2.0]  

## 📂 Project Structure

- client/
mcp_client.py

- servers/  
weather_server/  
flight_server/  
amadeus_hotel_server/  

- requirements.txt  


---

## ▶️ How to Run

```bash ->CMD in VS Code
git clone https://github.com/Fathi-Farouk/MCP_MultiUsage_Application.git  

cd MCP_MultiUsage_Application  

python -m venv .venv  
.venv\Scripts\activate  

pip install -r requirements.txt

## 🏗 Architecture Diagram

![Architecture](docs/architecture.png)

# Add your .env file with API keys  

python client/mcp_client.py  

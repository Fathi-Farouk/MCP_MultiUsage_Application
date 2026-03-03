#########################################################
# Uses LangChain
# Works with OpenAI / Gemini / Groq
# Connects to multiple MCP Servers via STDIO
# Converts LLM tool calls → JSON-RPC 2.0
# Sends to MCP Servers
# Converts JSON-RPC results → LLM tool results
# Lets the LLM produce the final answer
#########################################################

import os
import sys
import asyncio
from dotenv import load_dotenv

# LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage

# MCP
from langchain_mcp_adapters.client import MultiServerMCPClient

# ---------------------------------------------------------
# Step 1: Load environment variables
# ---------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------
# Step 2: Select LLM (switch easily)
# ---------------------------------------------------------
LLM_PROVIDER = "openai"  # "openai" | "gemini" | "groq"

if LLM_PROVIDER == "openai":
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.3
    )

elif LLM_PROVIDER == "gemini":
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
        temperature=0
    )

elif LLM_PROVIDER == "groq":
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama3-70b"),
        temperature=0
    )

else:
    raise ValueError("Invalid LLM_PROVIDER")

# ---------------------------------------------------------
# Step 3: MCP Server connections (STDIO)
# ---------------------------------------------------------
async def main():

    # ------------------------------------- Block 2 — MCP Client Configuration -------------------------------------
    # 🔴 UPDATED: dict-based config + explicit transport
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": ["mcp_server_math.py"],
            },

            "flight": {
                "transport": "stdio",
                "command": "python",
                "args": ["mcp_server_flight.py"],
            },

            "weather": {  # 🔴 UPDATED: normalized key name (was "Weather")
                "transport": "stdio",
                "command": sys.executable,
                "args": ["mcp_server_weather.py"],
            },

            "localfiles": {  # 🔴 UPDATED: normalized key name (was "Weather")
                "transport": "stdio",
                "command": sys.executable,
                "args": ["mcp_server_filesProcessing.py"],
            },

            "google_drive": {  # 🔴 UPDATED: normalized key name (was "Weather")
                "transport": "stdio",
                "command": "python",
                "args": ["Google_drive_MCP.py"],
            },

            "Amadeus_Hotel": {  # 🔴 UPDATED: normalized key name (was "Weather")
                "transport": "stdio",
                "command": "python",
                "args": ["mcp_server_amadeus.py"],
            },
        }
    )

    # ------------------------------------- Block 3 — Tool Discovery (MCP Handshake) --------------------------------
    tools = await client.get_tools()

    # ------------------------------------- Block 4 — Tool Indexing & Visibility ------------------------------------
    # 🔴 UPDATED: explicit tool map
    tool_map = {tool.name: tool for tool in tools}

    print("\n🔎 MCP tools discovered by client:")
    for tool in tools:
        print(f" - {tool.name}: {tool.description}")

    # ------------------------------------- Block 5 — LLM Initialization -------------------------------------------
    # 🔴 UPDATED: removed explicit api_key (handled via env automatically)
    llm_runtime = llm

    # ------------------------------------- Block 6 — Tool Binding + System Policy ----------------------------------
    llm_with_tools = llm_runtime.bind_tools(
        tools,
        tool_choice="required")

    prompt = ChatPromptTemplate.from_messages([
    ("system",
    "You are a Professional Multi-Travel Advisor powered by MCP tools.\n\n"

    "You operate in THREE MODES:\n\n"

    "MODE 1 — INTENT ANALYSIS:\n"
    "- Identify source country, destination country, travel dates, and duration.\n"
    "- If any required travel parameter is missing, ask a clarification question.\n"
    "- Never assume travel dates or duration.\n\n"

    "MODE 2 — TOOL EXECUTION:\n"
    "- You MUST use MCP tools to obtain factual information.\n"
    "- You are NOT allowed to invent prices, weather data, flight durations, or hotel costs.\n"
    "- Use only values returned by tools.\n"
    "- If tool data is missing, state that explicitly.\n\n"

    "TOOL ROUTING RULES:\n"
    "- Flight planning → use flight tools.\n"
    "- Destination weather → use weather tools.\n"
    "- Hotel recommendation → use amadeus hotel tools.\n"
    "- Budget calculation → use finance tools.\n\n"

    "MODE 3 — STRUCTURED STORY COMPOSER:\n"
    "After all tools are executed, produce a well-organized Markdown report using EXACTLY the following structure:\n\n"

    "# ✈️ Flight Plan\n"
    "- Departure:\n"
    "- Arrival:\n"
    "- Airline:\n"
    "- Duration:\n"
    "- Price:\n\n"

    "# 🌤 Weather at Destination\n"
    "- Temperature:\n"
    "- Condition:\n\n"

    "# 👕 Clothing Advice\n"
    "- Provide weather-based clothing recommendations.\n\n"

    "# 🏨 Hotel Recommendation\n"
    "- Hotel Name:\n"
    "- Distance to attractions:\n"
    "- Price per night:\n\n"

    "# 💰 Budget Estimation (USD)\n"
    "- Flight Cost:\n"
    "- Hotel Cost:\n"
    "- Estimated Daily Expenses:\n"
    "- Total Budget:\n\n"

    "Formatting Rules:\n"
    "- Always use Markdown.\n"
    "- Use bullet points only (no paragraphs).\n"
    "- Do not add extra sections.\n"
    "- Be concise and professional.\n"
    ),
    ("human", "{input}")
])

    chain = prompt | llm_with_tools

    print("\n🤖 MCP Assistant is ready!")
    print("Ask math, weather, or flight questions. Type 'exit' to quit.\n")

    # ------------------------------------- Block 7 — Interaction Loop ----------------------------------------------
    while True:
        try:
            user_input = input("🧑 You: ").strip()

            if user_input.lower() in {"exit", "quit"}:
                print("👋 Goodbye!")
                break

            response = await chain.ainvoke({"input": user_input})

            if not getattr(response, "tool_calls", None):
                print("🤖 Assistant: I am sorry, it is out of scope.\n")
                continue

            # ------------------------------------- Block 8 — Tool Execution ------------------------------------------
            messages = [HumanMessage(content=user_input)]
            messages.append(response)

            for call in response.tool_calls:
                tool_name = call["name"]

                # 🔴 UPDATED: safety whitelist
                if tool_name not in tool_map:
                    print("🤖 Assistant: I am sorry, it is out of scope.\n")
                    messages = None
                    break

                tool = tool_map[tool_name]
                tool_result = await tool.ainvoke(call["args"])

                messages.append(
                    ToolMessage(
                        tool_call_id=call["id"],
                        content=str(tool_result)
                    )
                )

            if not messages:
                continue

            final = await llm_runtime.ainvoke(messages)
            print("🤖 Assistant:", final.content, "\n")

        except KeyboardInterrupt:
            print("\n👋 Interrupted. Goodbye!")
            break

    # 🔴 UPDATED: safe cleanup for older adapter versions
    if hasattr(client, "close"):
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
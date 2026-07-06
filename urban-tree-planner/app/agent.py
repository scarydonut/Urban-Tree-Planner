# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent, LlmAgent
from google.adk.tools import AgentTool
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
import re
import json
import logging
def security_checkpoint(query: str) -> str:
    """Sanitize user input, detect prompt injection, and log the event.
    Returns the (potentially unchanged) query if safe, or a warning string.
    """
    # Simple PII regex patterns
    pii_patterns = {
        "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}",
        "phone": r"\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b",
        "ssn": r"\\b\\d{3}-\\d{2}-\\d{4}\\b",
    }
    redacted = query
    for label, pat in pii_patterns.items():
        redacted = re.sub(pat, f"<REDACTED_{label.upper()}>", redacted)

    # Prompt injection detection (simple keyword list)
    injection_keywords = ["ignore", "bypass", "disable safety", "ignore policy"]
    lowered = redacted.lower()
    if any(kw in lowered for kw in injection_keywords):
        logging.warning(json.dumps({"event": "injection_detected", "query": query}))
        return "[SECURITY_EVENT] Potential prompt injection detected. Query blocked."

    # Log audit entry
    logging.info(json.dumps({"event": "input_received", "original": query, "redacted": redacted}))
    return redacted


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(city: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    city_lower = city.lower().strip()
    
    # Map common cities to timezones
    tz_map = {
        "san francisco": "America/Los_Angeles",
        "sf": "America/Los_Angeles",
        "tokyo": "Asia/Tokyo",
        "delhi": "Asia/Kolkata",
        "new delhi": "Asia/Kolkata",
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "new york": "America/New_York",
        "ny": "America/New_York",
        "sydney": "Australia/Sydney",
    }
    
    # Try to find a match in the keys
    tz_identifier = None
    for name, tz_name in tz_map.items():
        if name in city_lower:
            tz_identifier = tz_name
            break
            
    if not tz_identifier:
        # Fallback to check if the input itself is a valid timezone identifier
        try:
            ZoneInfo(city)
            tz_identifier = city
        except Exception:
            return f"Sorry, I don't have timezone information for: {city}. Supported cities include San Francisco, Tokyo, Delhi, London, Paris, New York, Sydney."

    try:
        tz = ZoneInfo(tz_identifier)
        now = datetime.datetime.now(tz)
        return f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
    except Exception as e:
        return f"Error getting time for timezone {tz_identifier}: {str(e)}"


weather_agent = LlmAgent(
    name="weather_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="Provide simulated weather information for a given location.",
    tools=[get_weather],
)

time_agent = LlmAgent(
    name="time_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="Provide simulated current time for a given city.",
    tools=[get_current_time],
)

orchestrator = LlmAgent(
    name="orchestrator",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="Sanitize input, then decide whether to fetch weather or time based on the user's query and delegate to the appropriate sub‑agent.",
    tools=[
        security_checkpoint,
        AgentTool(weather_agent),
        AgentTool(time_agent),
    ],
)

# Configure audit logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler('audit.log'), logging.StreamHandler()],
)

app = App(
    root_agent=orchestrator,
    name="app",
)




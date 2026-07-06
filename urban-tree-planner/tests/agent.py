# ruff: noqa
# Placeholder root agent for tests directory to satisfy ADK loader
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import types

root_agent = LlmAgent(
    name="tests_root",
    model=Gemini(model="gemini-flash-latest", retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="Placeholder agent for tests.",
    tools=[],
)

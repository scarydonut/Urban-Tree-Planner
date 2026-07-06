import json
from mcp import Server, Tool

# Simple placeholder implementations for MCP tools specific to the urban-tree-planner project

def suggest_tree_location(city: str) -> str:
    """Return a mock suggestion for the best tree‑planting locations in a given city.
    In a real implementation this would query GIS data, satellite imagery, and climate
    models. Here we return a static example for demonstration purposes."""
    # Dummy data – normally you would compute based on city geometry.
    suggestion = {
        "city": city,
        "locations": [
            {"lat": 37.7749, "lon": -122.4194, "area": "Golden Gate Park"},
            {"lat": 37.7599, "lon": -122.4148, "area": "Mission Creek"},
        ],
        "reason": "High canopy potential and low pollution levels"
    }
    return json.dumps(suggestion, ensure_ascii=False)


def estimate_canopy_gain(area_sqkm: float) -> str:
    """Estimate the carbon sequestration benefit of planting trees over *area_sqkm*.
    This is a mock calculation using a simple multiplier (10 t CO₂ per km² per year)."""
    sequestration_tons = area_sqkm * 10.0
    result = {
        "area_sqkm": area_sqkm,
        "estimated_sequestration_tons_per_year": sequestration_tons,
    }
    return json.dumps(result, ensure_ascii=False)


def get_satellite_image(lat: float, lon: float) -> str:
    """Return a placeholder URL for a satellite image centered on the given coordinates.
    In production you would call a real satellite‑imagery API (e.g., Google Earth Engine)."""
    url = f"https://example.com/satellite?lat={lat}&lon={lon}&zoom=15"
    return json.dumps({"lat": lat, "lon": lon, "image_url": url}, ensure_ascii=False)

# Register the tools with the MCP server. The Server uses stdio transport by default –
# suitable for the agents‑cli local development workflow.

mcp_server = Server(
    port=8090,
    tools=[
        Tool(name="suggest_tree_location", func=suggest_tree_location),
        Tool(name="estimate_canopy_gain", func=estimate_canopy_gain),
        Tool(name="get_satellite_image", func=get_satellite_image),
    ],
)

if __name__ == "__main__":
    # Running this module will start the MCP server on the configured port.
    # It will block until the process is terminated (Ctrl‑C).
    mcp_server.serve()

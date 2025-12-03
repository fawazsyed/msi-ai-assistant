"""Weather MCP Server using HTTP transport for testing."""

from fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool
async def get_weather(location: str) -> str:
    """Get weather for a specific location."""
    # Mock weather data - in production, this would call a real weather API
    weather_data = {
        "new york": "It's sunny and 72°F in New York",
        "nyc": "It's sunny and 72°F in New York",
        "london": "It's cloudy and 55°F in London",
        "tokyo": "It's clear and 68°F in Tokyo",
    }
    
    location_lower = location.lower()
    return weather_data.get(location_lower, f"Weather data not available for {location}")


if __name__ == "__main__":
    # Run on HTTP transport (FastMCP 2.13 uses "http" not "streamable-http")
    mcp.run(transport="http", host="127.0.0.1", port=8000)

"""Simple MCP Server with basic math tools for testing."""

from fastmcp import FastMCP

mcp = FastMCP("Math")


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


@mcp.tool
def magic_number() -> int:
    """Return the magic number"""
    return 5


if __name__ == "__main__":
    mcp.run()  # Default transport is stdio

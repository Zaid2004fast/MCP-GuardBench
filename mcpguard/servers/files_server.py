"""Benign MCP server: sandboxed file storage."""

from mcp.server.fastmcp import FastMCP

from mcpguard.env import world

mcp = FastMCP("files", log_level="WARNING")


@mcp.tool()
def list_files(directory: str) -> str:
    """List the files stored under a directory, e.g. /home/alice."""
    return world.list_files(directory)


@mcp.tool()
def read_file(path: str) -> str:
    """Read and return the text content of a file."""
    return world.read_file(path)


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Create or overwrite a file with the given text content."""
    return world.write_file(path, content)


@mcp.tool()
def delete_file(path: str) -> str:
    """Delete a file."""
    return world.delete_file(path)


@mcp.tool()
def grant_access(path: str, principal: str) -> str:
    """Administrative: grant a principal access to a directory. Requires admin rights."""
    return world.grant_access(path, principal)


if __name__ == "__main__":
    mcp.run()

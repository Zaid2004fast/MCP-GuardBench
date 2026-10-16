"""Benign MCP server: sandboxed corporate mailbox."""

from mcp.server.fastmcp import FastMCP

from mcpguard.env import world

mcp = FastMCP("mail", log_level="WARNING")


@mcp.tool()
def list_inbox() -> str:
    """List emails in the user's inbox with id, sender, subject and a short preview."""
    return world.list_inbox()


@mcp.tool()
def read_email(email_id: str) -> str:
    """Read the full content of an email by its id (e.g. m1)."""
    return world.read_email(email_id)


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email from the user's account."""
    return world.send_email(to, subject, body)


if __name__ == "__main__":
    mcp.run()

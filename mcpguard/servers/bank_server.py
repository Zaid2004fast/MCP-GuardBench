"""Benign MCP server: sandboxed banking API."""

from mcp.server.fastmcp import FastMCP

from mcpguard.env import world

mcp = FastMCP("bank", log_level="WARNING")


@mcp.tool()
def get_balance() -> str:
    """Return the balance of the user's bank account."""
    return world.get_balance()


@mcp.tool()
def list_transactions(limit: int = 5) -> str:
    """List the most recent transactions of the user's account."""
    return world.list_transactions(limit)


@mcp.tool()
def transfer_funds(to_account: str, amount: float, memo: str = "") -> str:
    """Transfer money from the user's account to another account id."""
    return world.transfer_funds(to_account, amount, memo)


if __name__ == "__main__":
    mcp.run()

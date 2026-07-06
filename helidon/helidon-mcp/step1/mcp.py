from fastmcp import FastMCP

mcp = FastMCP("calendar-server")

@mcp.tool
def list_events(date: str = "") -> str:
    """List calendar events"""
    events = calendar.get_events(date)
    return f"Events: {events}"

@mcp.tool  
def add_event(name: str, date: str, attendees: list[str]) -> str:
    """Adds a new event to the calendar"""
    if not name or not date or not attendees:
        raise ValueError("Missing required arguments")
    calendar.create_event(name, date, attendees)
    return "New event added to the calendar"

@mcp.resource("file://events")
def events_resource() -> str:
    """List of calendar events created"""
    return calendar.read_content()

if __name__ == "__main__":
    mcp.run()
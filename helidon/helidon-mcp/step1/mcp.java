@Mcp.Path("/calendar")
@Mcp.Server("helidon-mcp-calendar-manager")
class McpCalendarServer {

    @Service.Inject
    Calendar calendar;

    @Mcp.Tool("List calendar events")   // @mcp.toolに相当する
    List<McpToolContext> listCalendarEvents(String date) {
        String entries = calendar.readContentMatchesLine(
            line -> date.isEmpty() || line.contains("date: " + date)
        );
        return List.of(McpToolContents.textContent(entries));
    }

    @Mcp.Tool("Add a new event to the calendar")
    List<McpToolContent> addCalendarEvent(String name, String date, List<String> attendees) {
        if (name.isEmpty() || date.isEmpty() || attendees.isEmpty()) {
            throw new McpException("Missing required arguments");
        }
        calendar.createNewEvent(name, date, attendees);
        return List.of(McpToolContents.textContent("New event added to the calendar"));
    }

    @Mcp.Resource(uri = "file://events", mediaType = "text/plain", description = "List of calendar events created")
    List<McpResourceContent> eventsResource() {
        String content = calendar.readContent();
        return List.of(McpResourceContents.textContent(content));
    }
}
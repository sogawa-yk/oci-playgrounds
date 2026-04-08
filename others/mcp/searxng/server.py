import os
import httpx
from mcp.server.fastmcp import FastMCP

SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://searxng:8080")

mcp = FastMCP(
    "web-search",
    host="0.0.0.0",
    port=8000,
    transport_security=None,
)


@mcp.tool()
async def search(query: str, categories: str = "general", language: str = "auto", max_results: int = 10) -> str:
    """Search the web using SearXNG.

    Args:
        query: Search query string
        categories: Comma-separated categories (general, images, news, science, files, it, social media)
        language: Language code (e.g. 'en', 'ja', 'auto')
        max_results: Maximum number of results to return (default 10)
    """
    params = {
        "q": query,
        "format": "json",
        "categories": categories,
        "language": language,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{SEARXNG_URL}/search", params=params)
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results", [])[:max_results]
    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "")
        lines.append(f"{i}. [{title}]({url})\n   {content}")
    return "\n\n".join(lines)


if __name__ == "__main__":
    import uvicorn
    from starlette.middleware import Middleware
    from starlette.responses import PlainTextResponse

    class HealthCheckMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope["type"] == "http" and scope["path"] == "/healthz":
                response = PlainTextResponse("ok")
                await response(scope, receive, send)
                return
            await self.app(scope, receive, send)

    mcp_app = mcp.streamable_http_app()
    mcp_app.add_middleware(HealthCheckMiddleware)
    uvicorn.run(mcp_app, host="0.0.0.0", port=8000)

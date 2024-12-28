from typing import Annotated
from urllib.parse import urlparse, urlunparse

import markdownify
import readabilipy.simple_json
from fastmcp import FastMCP
from pydantic import BaseModel, Field, AnyUrl
from protego import Protego
import requests

DEFAULT_USER_AGENT_AUTONOMOUS = "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)"
DEFAULT_USER_AGENT_MANUAL = "ModelContextProtocol/1.0 (User-Specified; +https://github.com/modelcontextprotocol/servers)"


def extract_content_from_html(html: str) -> str:
    """Extract and convert HTML content to Markdown format."""
    ret = readabilipy.simple_json.simple_json_from_html_string(
        html, use_readability=True
    )
    if not ret["content"]:
        return "<e>Page failed to be simplified from HTML<e>"
    content = markdownify.markdownify(
        ret["content"],
        heading_style=markdownify.ATX,
    )
    return content


def get_robots_txt_url(url: str) -> str:
    """Get the robots.txt URL for a given website URL."""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))


def check_may_autonomously_fetch_url(url: str, user_agent: str):
    """Check if the URL can be fetched by the user agent according to the robots.txt file."""
    robots_txt_url = get_robots_txt_url(url)
    try:
        rp = Protego.parse(requests.get(robots_txt_url).text)
        if not rp.can_fetch(user_agent, url):
            raise ValueError(
                f"URL {url} is not allowed to be fetched by {user_agent} according to robots.txt"
            )
    except Exception as e:
        # If we can't fetch robots.txt, assume we can fetch the URL
        pass


def fetch_url(url: str, user_agent: str, force_raw: bool = False):
    """Fetch the URL and return the content."""
    headers = {"User-Agent": user_agent}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "").lower()
    if not force_raw and "text/html" in content_type:
        return extract_content_from_html(response.text)
    return response.text


class Fetch(BaseModel):
    """Parameters for fetching a URL."""

    url: Annotated[AnyUrl, Field(description="URL to fetch")]
    max_length: Annotated[
        int,
        Field(
            default=5000,
            description="Maximum number of characters to return.",
            gt=0,
            lt=1000000,
        ),
    ]
    start_index: Annotated[
        int,
        Field(
            default=0,
            description="On return output starting at this character index.",
            ge=0,
        ),
    ]
    raw: Annotated[
        bool,
        Field(
            default=False,
            description="Get the actual HTML content if the requested page, without simplification.",
        ),
    ]


mcp = FastMCP("fetchmcp")


@mcp.tool()
def fetch(
    url: str, max_length: int = 5000, start_index: int = 0, raw: bool = False
) -> str:
    """Fetch content from a URL.

    Args:
        url: URL to fetch
        max_length: Maximum number of characters to return
        start_index: Start index for returned content
        raw: Whether to return raw HTML instead of simplified content
    """
    check_may_autonomously_fetch_url(url, DEFAULT_USER_AGENT_AUTONOMOUS)
    content = fetch_url(url, DEFAULT_USER_AGENT_AUTONOMOUS, raw)

    if start_index >= len(content):
        return ""

    return content[start_index : start_index + max_length]


if __name__ == "__main__":
    mcp.run("sse")

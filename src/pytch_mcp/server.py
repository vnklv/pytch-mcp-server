"""
Pytch MCP Server — Standalone Model Context Protocol Server
------------------------------------------------------------
Allows Claude Desktop, Cursor, Claude Code, Antigravity, and AI Agents
to interact directly with Pytch's PR and Outreach platform.

Environment Variables:
    PYTCH_API_KEY: Your Pytch API Key (obtained from your Pytch account settings: pytch_live_...)
    PYTCH_API_URL: Pytch API base URL (default: https://api.pytch.cc)
"""

import os
import sys
import json
import logging
from typing import Optional, List, Dict, Any
import httpx
from mcp.server.mcpserver import MCPServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pytch-mcp")

DEFAULT_API_URL = "https://api.pytch.cc"

mcp = MCPServer(
    name="Pytch PR Assistant",
    version="1.0.0",
    description="Autonomous PR, journalist discovery, email deliverability audit, and AI brand visibility engine."
)


def _get_client_config() -> tuple[str, str]:
    """Retrieves API URL and API key from environment."""
    api_url = os.getenv("PYTCH_API_URL", DEFAULT_API_URL).rstrip("/")
    api_key = os.getenv("PYTCH_API_KEY", "").strip()
    return api_url, api_key


async def _api_request(
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    api_key_override: Optional[str] = None
) -> Dict[str, Any]:
    """Sends authenticated HTTP request to Pytch API."""
    api_url, env_key = _get_client_config()
    key = api_key_override or env_key

    headers = {
        "User-Agent": "Pytch-MCP-Server/1.0.0",
        "Accept": "application/json"
    }
    if key:
        headers["Authorization"] = f"Bearer {key}"
        headers["X-API-Key"] = key

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.request(
                method=method,
                url=f"{api_url}{path}",
                params=params,
                json=json_data,
                headers=headers
            )
            if resp.status_code == 401:
                return {
                    "error": "Unauthorized. Please set the PYTCH_API_KEY environment variable with a valid key (e.g. pytch_live_...)."
                }
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"API error {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": f"Connection error: {str(e)}"}


@mcp.tool(name="check_domain_deliverability")
async def check_domain_deliverability(domain: str, selector: Optional[str] = None) -> str:
    """
    Check domain email deliverability (F6 Block):
    Performs live DNS audit for SPF, DMARC, DKIM, MX, and DNSBL spam blacklists.
    Calculates a 0-100 Deliverability Health Score and generates a safe ramp-up warmup schedule.

    Args:
        domain: Domain name or email address (e.g. 'company.com' or 'ceo@company.com')
        selector: Optional DKIM selector if known (e.g. 'google', 'selector1')
    """
    res = await _api_request(
        method="GET",
        path="/api/v1/deliverability/check",
        params={"domain": domain, "selector": selector}
    )
    return json.dumps(res, ensure_ascii=False, indent=2)


@mcp.tool(name="check_ai_brand_visibility")
async def check_ai_brand_visibility(
    brand_name: str,
    category: str,
    website: Optional[str] = None,
    competitors: Optional[List[str]] = None
) -> str:
    """
    Audit brand visibility in AI answers (F9 Block / GEO):
    Simulates searches across LLMs (ChatGPT/Perplexity/Gemini style),
    evaluates whether the brand is cited, calculates AI Share of Voice (SOV),
    extracts media outlets influencing AI responses, and matches them to journalists.

    Args:
        brand_name: Name of the company or brand (e.g. 'Pytch')
        category: Industry niche or product category (e.g. 'AI PR agent', 'fintech')
        website: Optional brand website URL
        competitors: Optional list of competitor brand names
    """
    res = await _api_request(
        method="POST",
        path="/api/v1/ai-visibility/audit",
        json_data={
            "brand_name": brand_name,
            "category": category,
            "website": website,
            "competitors": competitors or []
        }
    )
    return json.dumps(res, ensure_ascii=False, indent=2)


@mcp.tool(name="search_journalists")
async def search_journalists(topic: str, outlet: Optional[str] = None, limit: int = 10) -> str:
    """
    Search verified tech and business journalists by beat, topic or media publication.

    Args:
        topic: Keyword or beat (e.g. 'AI', 'B2B SaaS', 'Biotech', 'Venture Capital')
        outlet: Optional media publication filter (e.g. 'TechCrunch', 'Forbes', 'VentureBeat')
        limit: Max contacts to return (default: 10)
    """
    res = await _api_request(
        method="GET",
        path="/public/journalists/search",
        params={"q": topic, "outlet": outlet, "limit": limit}
    )
    return json.dumps(res, ensure_ascii=False, indent=2)


@mcp.tool(name="list_pr_projects")
async def list_pr_projects() -> str:
    """
    List active PR campaigns and projects for the authenticated user.
    Requires PYTCH_API_KEY environment variable.
    """
    res = await _api_request(method="GET", path="/projects")
    return json.dumps(res, ensure_ascii=False, indent=2)


@mcp.tool(name="get_project_results")
async def get_project_results(project_id: str, limit: int = 20) -> str:
    """
    Get identified media contacts, pitch status, and response activity for a project.

    Args:
        project_id: UUID of the project in Pytch
        limit: Number of contacts to fetch
    """
    res = await _api_request(method="GET", path=f"/results/{project_id}", params={"limit": limit})
    return json.dumps(res, ensure_ascii=False, indent=2)


def main():
    """Main CLI entrypoint for running the Pytch MCP Server."""
    transport = "stdio"
    if "--sse" in sys.argv or os.getenv("MCP_TRANSPORT") == "sse":
        transport = "sse"

    port = int(os.getenv("PORT", "8001"))
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    if transport == "sse":
        print(f"Starting Pytch MCP Server (SSE) on port {port}...", file=sys.stderr)
        mcp.run(transport="sse", port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

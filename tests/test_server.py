import json
import pytest
from unittest.mock import patch, AsyncMock
from pytch_mcp.server import (
    mcp,
    check_domain_deliverability,
    check_ai_brand_visibility,
    search_journalists,
    list_pr_projects,
    get_project_results,
    _api_request,
)


@pytest.mark.asyncio
async def test_tool_registration_and_count():
    """Verify that all 5 declared tools are registered with the MCP server."""
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}
    expected_tools = {
        "check_domain_deliverability",
        "check_ai_brand_visibility",
        "search_journalists",
        "list_pr_projects",
        "get_project_results",
    }
    assert tool_names == expected_tools
    assert len(tools) == 5


@pytest.mark.asyncio
async def test_tool_annotations_and_safety_hints():
    """Verify that every tool declares strict security and behavioral hints."""
    tools = await mcp.list_tools()
    for tool in tools:
        assert tool.annotations is not None, f"Tool {tool.name} missing annotations"
        assert tool.annotations.read_only_hint is True, f"Tool {tool.name} must be readOnly"
        assert tool.annotations.destructive_hint is False, f"Tool {tool.name} must not be destructive"
        assert tool.annotations.idempotent_hint is True, f"Tool {tool.name} must be idempotent"
        assert tool.annotations.open_world_hint is True, f"Tool {tool.name} must be openWorld"


@pytest.mark.asyncio
async def test_check_domain_deliverability_handler():
    """Test deliverability audit tool handler."""
    mock_response = {
        "domain": "testcompany.com",
        "score": 92,
        "spf": {"status": "valid"},
        "dmarc": {"status": "valid", "policy": "reject"},
    }
    with patch("pytch_mcp.server._api_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        raw_res = await check_domain_deliverability(domain="testcompany.com", selector="google")
        res = json.loads(raw_res)

        assert res["score"] == 92
        assert res["domain"] == "testcompany.com"
        mock_req.assert_awaited_once_with(
            method="GET",
            path="/api/v1/deliverability/check",
            params={"domain": "testcompany.com", "selector": "google"},
        )


@pytest.mark.asyncio
async def test_check_ai_brand_visibility_handler():
    """Test AI brand visibility (GEO) audit tool handler."""
    mock_response = {
        "brand_name": "Pytch",
        "share_of_voice": 78.5,
        "cited_sources": ["TechCrunch", "Forbes"],
    }
    with patch("pytch_mcp.server._api_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        raw_res = await check_ai_brand_visibility(
            brand_name="Pytch",
            category="AI PR",
            website="https://pytch.cc",
            competitors=["Cision", "Muck Rack"],
        )
        res = json.loads(raw_res)

        assert res["share_of_voice"] == 78.5
        mock_req.assert_awaited_once_with(
            method="POST",
            path="/api/v1/ai-visibility/audit",
            json_data={
                "brand_name": "Pytch",
                "category": "AI PR",
                "website": "https://pytch.cc",
                "competitors": ["Cision", "Muck Rack"],
            },
        )


@pytest.mark.asyncio
async def test_search_journalists_handler():
    """Test journalist search tool handler."""
    mock_response = {
        "query": "Artificial Intelligence",
        "total": 2,
        "results": [
            {"name": "Jane Doe", "outlet": "TechCrunch", "beat": "AI"},
            {"name": "John Smith", "outlet": "Wired", "beat": "AI Infrastructure"},
        ],
    }
    with patch("pytch_mcp.server._api_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        raw_res = await search_journalists(topic="Artificial Intelligence", outlet="TechCrunch", limit=5)
        res = json.loads(raw_res)

        assert res["total"] == 2
        assert len(res["results"]) == 2
        mock_req.assert_awaited_once_with(
            method="GET",
            path="/public/journalists/search",
            params={"q": "Artificial Intelligence", "outlet": "TechCrunch", "limit": 5},
        )


@pytest.mark.asyncio
async def test_list_pr_projects_handler():
    """Test project listing tool handler."""
    mock_response = [{"id": "proj-1", "name": "Launch Campaign"}]
    with patch("pytch_mcp.server._api_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        raw_res = await list_pr_projects()
        res = json.loads(raw_res)

        assert len(res) == 1
        assert res[0]["name"] == "Launch Campaign"
        mock_req.assert_awaited_once_with(method="GET", path="/projects")


@pytest.mark.asyncio
async def test_get_project_results_handler():
    """Test project results retrieval handler."""
    mock_response = {"project_id": "proj-1", "contacts_reached": 15, "replies": 3}
    with patch("pytch_mcp.server._api_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        raw_res = await get_project_results(project_id="proj-1", limit=10)
        res = json.loads(raw_res)

        assert res["contacts_reached"] == 15
        mock_req.assert_awaited_once_with(
            method="GET",
            path="/results/proj-1",
            params={"limit": 10},
        )

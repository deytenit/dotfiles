"""Read-only verification against the actual stdio server and Joplin API."""

import asyncio
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent import child_environment, load_policy, load_server


def prepare_hierarchy(config):
    from server import configure
    configure(config)
    from joplin_mcp.fastmcp_server import get_joplin_client
    from joplin_mcp.notebook_utils import NotebookResolver, _build_split_specs, _matches_allowlist
    policy = load_policy(config)
    specs = _build_split_specs(policy["notebook_allowlist"])
    resolver = NotebookResolver(get_joplin_client)
    for destination in policy["hierarchy"].values():
        parent = ""
        pieces = destination.split("/")
        for index, title in enumerate(pieces):
            path = "/".join(pieces[:index + 1])
            matches = [key for key, item in resolver.get_map(force_refresh=True).items()
                       if item["title"] == title and (item["parent_id"] or "") == parent]
            if len(matches) > 1 or (not matches and index == 0):
                raise ValueError("Create an unambiguous root notebook in Joplin first")
            if not _matches_allowlist(path, "", *specs) and (not matches or index == len(pieces) - 1):
                raise ValueError("Hierarchy is outside notebook scope")
            if not matches and not _matches_allowlist("/".join(pieces[:index]), "", *specs):
                raise ValueError("Create the scope root notebook in Joplin first")
            parent = matches[0] if matches else resolver.add_notebook(title=title, parent_id=parent)


async def check(config):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from joppy.client_api import ClientApi
    from joplin_mcp.notebook_utils import NotebookResolver

    policy, server = load_policy(config), load_server(config)
    client = ClientApi(token=server["token"], url=f"http://127.0.0.1:{server['port']}")
    resolver = NotebookResolver(lambda: client)
    for path in policy["hierarchy"].values():
        resolver.resolve_by_path(path, allowlist_entries=policy["notebook_allowlist"])
    environment = child_environment(policy)
    environment["JOPLIN_MCP_CONFIG"] = str(config / "server.json")
    params = StdioServerParameters(command=sys.executable, args=["-I", str(Path(__file__).with_name("server.py")), str(config)], env=environment)
    with tempfile.TemporaryFile(mode="w+") as errors:
        async with stdio_client(params, errlog=errors) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                names = {tool.name for tool in (await session.list_tools()).tools}
                expected = {key for key, enabled in policy["tools"].items() if enabled}
                if names != expected:
                    raise ValueError("Unexpected tool surface")
                if policy["tools"]["list_notebooks"]:
                    result = await session.call_tool("list_notebooks")
                    if result.isError:
                        raise ValueError("Joplin health check failed")


if __name__ == "__main__":
    try:
        if "--hierarchy" in sys.argv[2:]:
            prepare_hierarchy(Path(sys.argv[1]))
        else:
            asyncio.run(asyncio.wait_for(check(Path(sys.argv[1])), 45))
    except Exception:
        print("Live check failed: verify hierarchy destinations, token, and Web Clipper", file=sys.stderr)
        sys.exit(1)

"""Exercise the locked upstream server over stdio against synthetic Clipper data."""

import asyncio
from contextlib import asynccontextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent
import check
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def uid(number):
    return f"{number:032x}"


class Clipper(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def do_PUT(self):
        self.dispatch("PUT")

    def dispatch(self, method):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        query = parse_qs(parsed.query)
        state = self.server.state
        if parts == ["ping"]:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"JoplinClipperServer")
            return
        if query.get("token") != ["synthetic-secret-12345"]:
            self.send_error(403)
            return
        if state.get("fail"):
            self.send_error(503)
            return
        raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        data = json.loads(raw) if raw else {}
        if method == "PUT" and parts == ["notes", uid(101)] and state.get("write_barrier"):
            state["write_barrier"].wait(timeout=10)
        with state["lock"]:
            if method == "GET":
                if parts == ["folders"]:
                    result = list(state["folders"].values())
                elif parts == ["notes"] or parts == ["search"]:
                    result = list(state["notes"].values())
                elif parts[0] == "folders" and len(parts) == 3 and parts[2] == "notes":
                    result = [n for n in state["notes"].values() if n["parent_id"] == parts[1]]
                elif parts[0] == "notes" and len(parts) == 2:
                    result = state["notes"].get(parts[1])
                elif parts[0] == "notes" and len(parts) == 3 and parts[2] == "resources":
                    result = [{"id": uid(900), "title": "attachment", "mime": "text/plain", "ocr_text": "Synthetic OCR", "ocr_status": 2}]
                elif parts[0] == "notes" and len(parts) == 3 and parts[2] == "tags":
                    result = [{"id": uid(901), "title": "synthetic-tag"}]
                else:
                    result = None
                if isinstance(result, list):
                    # Multiple pages ensure filtering is exercised across pagination.
                    page = int(query.get("page", [1])[0])
                    limit = min(int(query.get("limit", [100])[0]), 2)
                    start = (page - 1) * limit
                    result = {"items": result[start:start + limit], "has_more": start + limit < len(result)}
            elif method == "POST" and parts[0] in ("notes", "folders"):
                state["counter"] += 1
                identifier = uid(state["counter"])
                result = {"id": identifier, "created_time": 1000, "updated_time": 1000, **data}
                state[parts[0]][identifier] = result
            elif method == "PUT" and len(parts) == 2 and parts[0] in ("notes", "folders"):
                result = state[parts[0]].get(parts[1])
                if result:
                    result.update(data)
            else:
                result = None
            if result is None:
                self.send_error(404)
                return
            body = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class MCPTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        folders = {
            uid(1): {"id": uid(1), "title": "Work", "parent_id": ""},
            uid(2): {"id": uid(2), "title": "Personal", "parent_id": ""},
            uid(3): {"id": uid(3), "title": "Child", "parent_id": uid(1)},
            uid(4): {"id": uid(4), "title": "Nested", "parent_id": uid(3)},
            uid(5): {"id": uid(5), "title": "Private", "parent_id": uid(2)},
        }
        notes = {}
        for i, (parent, title) in enumerate([(1, "work-marker"), (2, "home-marker"), (4, "work-nested-marker"), (5, "home-nested-marker")], 101):
            notes[uid(i)] = {"id": uid(i), "title": title, "parent_id": uid(parent),
                             "body": "Original sentence. Preserve this paragraph.",
                             "created_time": 1000, "updated_time": 1000, "is_todo": 0, "todo_completed": 0}
        notes[uid(101)]["body"] += f" [related](:/{uid(102)})"
        self.state = {"folders": folders, "notes": notes, "counter": 200, "lock": threading.Lock()}
        self.http = ThreadingHTTPServer(("127.0.0.1", 0), Clipper)
        self.http.state = self.state
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.http.server_close)
        self.addCleanup(self.http.shutdown)

    def config(self, profile):
        directory = Path(self.temp.name) / profile
        agent.atomic_private(directory / "policy.json", json.dumps(agent.make_policy(profile)))
        agent.atomic_private(directory / "server.json", json.dumps({"token": "synthetic-secret-12345", "host": "127.0.0.1", "port": self.http.server_port, "timeout": 15, "verify_ssl": False}))
        return directory

    @asynccontextmanager
    async def client(self, profile, config=None):
        config = config or self.config(profile)
        environment = agent.child_environment(agent.load_policy(config))
        environment["JOPLIN_MCP_CONFIG"] = str(config / "server.json")
        params = StdioServerParameters(command=sys.executable, args=["-I", str(agent.APP / "server.py"), str(config)], env=environment)
        with tempfile.TemporaryFile(mode="w+") as errors:
            async with stdio_client(params, errlog=errors) as (read, write):
                async with ClientSession(read, write) as session:
                    await asyncio.wait_for(session.initialize(), 20)
                    yield session
            errors.seek(0)
            diagnostics = errors.read()
            self.assertNotIn("synthetic-secret-12345", diagnostics)
            self.assertNotIn("Preserve this paragraph", diagnostics)

    async def call(self, session, name, **arguments):
        result = await asyncio.wait_for(session.call_tool(name, arguments), 15)
        text = "\n".join(getattr(item, "text", "") for item in result.content)
        return result, text

    async def test_both_profiles_filter_descendants_searches_direct_ids_and_attachments(self):
        for profile, allowed, blocked, markers in [
            ("work", 103, 104, ("work-nested-marker", "home-marker", "home-nested-marker")),
            ("home", 104, 103, ("home-nested-marker", "work-marker", "work-nested-marker")),
        ]:
            with self.subTest(profile=profile):
                async with self.client(profile) as session:
                    names = {tool.name for tool in (await session.list_tools()).tools}
                    self.assertNotIn("list_tags", names)
                    self.assertNotIn("tag_note", names)
                    self.assertNotIn("delete_note", names)
                    result, text = await self.call(session, "find_notes", query="*", limit=100)
                    self.assertFalse(result.isError, text)
                    self.assertIn(markers[0], text)
                    for marker in markers[1:]:
                        self.assertNotIn(marker, text)
                    for tool in ("get_note", "get_note_resources", "get_tags_by_note", "find_in_note", "get_links"):
                        args = {"note_id": uid(blocked)}
                        if tool == "find_in_note":
                            args["pattern"] = "Original"
                        result, text = await self.call(session, tool, **args)
                        self.assertTrue(result.isError, (tool, text))
                        self.assertNotIn("Preserve this paragraph", text)
                    result, text = await self.call(session, "get_note_resources", note_id=uid(allowed))
                    self.assertFalse(result.isError, text)
                    self.assertIn("Synthetic OCR", text)
                    _, text = await self.call(session, "list_notebooks")
                    self.assertNotIn("Personal" if profile == "work" else "Work", text)

    async def test_forbidden_mutations_leave_notes_unchanged_and_targeted_edit_preserves_rest(self):
        async with self.client("work") as session:
            for tool, args in [
                ("update_note", {"note_id": uid(102), "title": "Forbidden"}),
                ("edit_note", {"note_id": uid(102), "old_string": "Original", "new_string": "Forbidden"}),
                ("create_note", {"title": "Forbidden", "notebook_name": "Personal", "body": "Forbidden"}),
                ("update_note", {"note_id": uid(101), "notebook_name": "Personal"}),
                ("create_notebook", {"title": "Forbidden", "parent_name": "Personal"}),
                ("update_notebook", {"notebook_id": uid(2), "title": "Forbidden"}),
            ]:
                result, text = await self.call(session, tool, **args)
                self.assertTrue(result.isError, (tool, text))
            self.assertEqual(self.state["notes"][uid(102)]["title"], "home-marker")
            self.assertEqual(self.state["notes"][uid(101)]["parent_id"], uid(1))
            result, text = await self.call(session, "edit_note", note_id=uid(101), old_string="Original sentence.", new_string="Updated sentence.")
            self.assertFalse(result.isError, text)
            self.assertIn("Updated sentence. Preserve this paragraph.", self.state["notes"][uid(101)]["body"])
            result, _ = await self.call(session, "edit_note", note_id=uid(101), old_string="Original sentence.", new_string="Stale edit.")
            self.assertTrue(result.isError)
            result, text = await self.call(session, "update_note", note_id=uid(101), notebook_name="Work/Child")
            self.assertFalse(result.isError, text)
            self.assertEqual(self.state["notes"][uid(101)]["parent_id"], uid(3))
            self.assertIn("Updated sentence. Preserve this paragraph.", self.state["notes"][uid(101)]["body"])

    async def test_concurrent_same_note_replacements_have_no_lock(self):
        async with self.client("work") as first, self.client("work") as second:
            self.state["write_barrier"] = threading.Barrier(2)
            results = await asyncio.gather(
                self.call(first, "update_note", note_id=uid(101), body="First writer"),
                self.call(second, "update_note", note_id=uid(101), body="Second writer"))
            self.assertTrue(all(not result.isError for result, _ in results), results)
            self.assertIn(self.state["notes"][uid(101)]["body"], {"First writer", "Second writer"})

    async def test_nested_scope_hierarchy_and_disabled_listing(self):
        config = self.config("work")
        policy = agent.load_policy(config)
        policy["notebook_allowlist"] = ["/Work/Child"]
        policy["hierarchy"] = {role: "Work/Child/" + role.title() for role in agent.ROLES}
        policy["tools"]["list_notebooks"] = False
        agent.atomic_private(config / "policy.json", json.dumps(policy))
        await asyncio.to_thread(check.prepare_hierarchy, config)
        await asyncio.wait_for(check.check(config), 30)
        async with self.client("work", config=config) as session:
            result, text = await self.call(session, "get_note", note_id=uid(101))
            self.assertTrue(result.isError, text)
            result, text = await self.call(session, "get_note", note_id=uid(103))
            self.assertFalse(result.isError, text)

    async def test_links_exclude_blocked_targets_and_clients_survive_independent_close(self):
        async with self.client("work") as first:
            async with self.client("work") as second:
                _, text = await self.call(first, "get_links", note_id=uid(101))
                self.assertNotIn("home-marker", text)
                results = await asyncio.gather(
                    self.call(first, "create_note", title="capture-a", notebook_name="Work/Child", body="A"),
                    self.call(second, "create_note", title="capture-b", notebook_name="Work/Child", body="B"))
                self.assertTrue(all(not result.isError for result, _ in results), results)
            result, text = await self.call(first, "get_note", note_id=uid(101))
            self.assertFalse(result.isError, text)
        captures = [n for n in self.state["notes"].values() if n["title"].startswith("capture-")]
        self.assertEqual({n["body"] for n in captures}, {"A", "B"})

    async def test_hierarchy_setup_is_idempotent_and_doctor_checks_real_stdio(self):
        config = self.config("work")
        await asyncio.to_thread(check.prepare_hierarchy, config)
        count = len(self.state["folders"])
        await asyncio.to_thread(check.prepare_hierarchy, config)
        self.assertEqual(len(self.state["folders"]), count)
        children = {f["title"] for f in self.state["folders"].values() if f["parent_id"] == uid(1)}
        self.assertTrue({"Agent Inbox", "Projects", "Areas", "Reference", "Archive"} <= children)
        await asyncio.wait_for(check.check(config), 30)

    async def test_hierarchy_setup_never_creates_a_missing_root(self):
        config = self.config("work")
        del self.state["folders"][uid(1)]
        count = len(self.state["folders"])
        with self.assertRaisesRegex(ValueError, "root notebook"):
            await asyncio.to_thread(check.prepare_hierarchy, config)
        self.assertEqual(len(self.state["folders"]), count)

    async def test_hierarchy_setup_never_creates_scope_root_under_hidden_parent(self):
        config = self.config("work")
        policy = agent.load_policy(config)
        policy["notebook_allowlist"] = ["/Work/Agent Inbox"]
        policy["hierarchy"] = {role: "Work/Agent Inbox/" + role.title() for role in agent.ROLES}
        agent.atomic_private(config / "policy.json", json.dumps(policy))
        count = len(self.state["folders"])
        with self.assertRaisesRegex(ValueError, "scope root"):
            await asyncio.to_thread(check.prepare_hierarchy, config)
        self.assertEqual(len(self.state["folders"]), count)

    async def test_api_failures_do_not_expose_credentials_through_mcp(self):
        async with self.client("work") as session:
            names = {tool.name for tool in (await session.list_tools()).tools}
            self.assertNotIn("ping_joplin", names)
            self.state["fail"] = True
            result, text = await self.call(session, "get_note", note_id=uid(101))
            self.assertTrue(result.isError)
            self.assertNotIn("synthetic-secret-12345", text)


if __name__ == "__main__":
    unittest.main()

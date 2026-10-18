"""Private configuration and lifecycle for independent local Joplin MCP clients."""

import argparse
import getpass
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

APP = Path(__file__).resolve().parent
ROLES = ("inbox", "projects", "areas", "reference", "archive")
TOOLS = {
    "find_notes": True, "find_notes_with_tag": False,
    "find_notes_in_notebook": True, "find_in_note": True,
    "get_all_notes": False, "get_note": True, "get_note_resources": True,
    "get_links": True, "create_note": True, "update_note": True,
    "edit_note": True, "delete_note": False, "list_notebooks": True,
    "create_notebook": True, "update_notebook": True, "delete_notebook": False,
    "list_tags": False, "create_tag": False, "update_tag": False,
    "delete_tag": False, "get_tags_by_note": True, "tag_note": False,
    # Upstream ping returns unsanitized exception text, including token-bearing URLs.
    "untag_note": False, "ping_joplin": False, "restore_from_trash": False,
    "import_from_file": False,
}


class SetupError(Exception):
    pass


def locations():
    home = Path.home()
    return home / ".config/joplin-agent", home / ".local/share/joplin-agent/runtime"


def check_private(path, directory=False):
    try:
        info = path.lstat()
    except OSError:
        raise SetupError(f"Missing private {'directory' if directory else 'file'}: {path}") from None
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    if not expected(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise SetupError(f"Expected an owned, private {'directory (0700)' if directory else 'regular file (0600)'}: {path}")
    # Public app links must never turn private settings into tracked files.
    for parent in (path.resolve(), *path.resolve().parents):
        if (parent / ".git").exists():
            raise SetupError("Private configuration must be outside version-controlled checkouts")


def read_private(path):
    check_private(path.parent, directory=True)
    check_private(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise SetupError(f"Cannot read valid JSON from {path.name}") from None
    if not isinstance(value, dict):
        raise SetupError(f"{path.name} must contain a JSON object")
    return value


def validate_policy(policy):
    if set(policy) != {"version", "notebook_allowlist", "hierarchy", "tools"} or policy["version"] != 1:
        raise SetupError("Policy requires version=1, notebook_allowlist, hierarchy, and tools")
    rules = policy["notebook_allowlist"]
    if not isinstance(rules, list) or not rules:
        raise SetupError("Notebook access rules must be an explicit nonempty list")
    for rule in rules:
        if (not isinstance(rule, str) or not rule.strip() or rule != rule.strip()
                or any(c in rule for c in ",\n\r\0") or rule.startswith("#") or rule == "!"):
            raise SetupError("Invalid notebook access pattern")
    if not any(not r.startswith("!") for r in rules):
        raise SetupError("Notebook policy needs at least one positive pattern")
    hierarchy = policy["hierarchy"]
    if not isinstance(hierarchy, dict) or set(hierarchy) != set(ROLES):
        raise SetupError("Hierarchy must define inbox, projects, areas, reference, and archive")
    for path in hierarchy.values():
        if (not isinstance(path, str) or not path or path != path.strip()
                or any(c in path for c in "\n\r\0")
                or any(p in ("", ".", "..") for p in path.split("/"))):
            raise SetupError("Hierarchy destinations must be nonempty notebook paths")
    if len(set(hierarchy.values())) != len(ROLES):
        raise SetupError("Each hierarchy role needs a distinct destination")
    tools = policy["tools"]
    if (not isinstance(tools, dict) or set(tools) != set(TOOLS)
            or any(type(v) is not bool for v in tools.values())):
        raise SetupError("Policy must explicitly set every supported tool to true or false")
    if any(tools[name] and not allowed for name, allowed in TOOLS.items()):
        raise SetupError("Policy enables a tool excluded by this integration's verified tool set")
    return policy


def load_policy(config):
    return validate_policy(read_private(config / "policy.json"))


def load_server(config):
    server = read_private(config / "server.json")
    if set(server) != {"token", "host", "port", "timeout", "verify_ssl"}:
        raise SetupError("server.json requires only token, host, port, timeout, and verify_ssl")
    if not isinstance(server["token"], str) or len(server["token"].strip()) < 10:
        raise SetupError("Joplin token is missing or invalid; run setup locally")
    if server["host"] not in ("127.0.0.1", "localhost"):
        raise SetupError("Joplin must use a loopback host")
    if type(server["port"]) is not int or not 1 <= server["port"] <= 65535:
        raise SetupError("Joplin port must be an integer between 1 and 65535")
    if type(server["timeout"]) is not int or not 1 <= server["timeout"] <= 60:
        raise SetupError("Joplin timeout must be an integer between 1 and 60 seconds")
    if server["verify_ssl"] is not False:
        raise SetupError("Local Clipper uses HTTP; verify_ssl must be false")
    return server


def child_environment(policy):
    environment = {k: v for k, v in os.environ.items()
                   if not k.startswith(("JOPLIN_", "PYTHON", "FASTMCP_"))
                   and k not in {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"}}
    environment["JOPLIN_NOTEBOOK_ALLOWLIST"] = ",".join(policy["notebook_allowlist"])
    environment.update({"JOPLIN_TOOL_" + k.upper(): str(v).lower() for k, v in policy["tools"].items()})
    environment["JOPLIN_MCP_NOTEBOOK_CACHE_TTL"] = "5"
    environment["NO_PROXY"] = environment["no_proxy"] = "localhost,127.0.0.1"
    return environment


def launch(config, runtime):
    policy = load_policy(config)
    load_server(config)
    python = runtime / "bin/python"
    if not python.is_file():
        raise SetupError("Joplin runtime is missing; run joplin-agent setup --install")
    environment = child_environment(policy)
    environment["JOPLIN_MCP_CONFIG"] = str(config / "server.json")
    os.chdir(config)
    os.execve(python, [str(python), "-I", str(APP / "server.py"), str(config)], environment)


def atomic_private(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    check_private(path.parent, directory=True)
    if path.exists() or path.is_symlink():
        check_private(path)
    fd, temporary = tempfile.mkstemp(prefix=".joplin-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def make_policy(profile):
    root = "Work" if profile == "work" else "Personal"
    return {"version": 1,
            "notebook_allowlist": ["/Work"] if profile == "work" else ["**", "!/Work"],
            "hierarchy": dict(zip(ROLES, [root + "/" + x for x in
                              ("Agent Inbox", "Projects", "Areas", "Reference", "Archive")])),
            "tools": TOOLS.copy()}


def api(server, endpoint, method="GET", data=None, params=None):
    query = urllib.parse.urlencode({"token": server["token"], **(params or {})})
    url = f"http://127.0.0.1:{server['port']}/{endpoint}?{query}"
    request = urllib.request.Request(url, method=method,
                                    data=json.dumps(data).encode() if data is not None else None,
                                    headers={"Content-Type": "application/json"})
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(
                request, timeout=server["timeout"]) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise SetupError(f"Joplin API returned HTTP {error.code}; check the local token and service") from None
    except (OSError, ValueError):
        raise SetupError("Cannot reach Joplin; enable Settings → Web Clipper and check the port") from None


def run_checked(command, failure, **kwargs):
    try:
        result = subprocess.run(command, timeout=300, capture_output=True, text=True, **kwargs)
    except (OSError, subprocess.TimeoutExpired):
        raise SetupError(failure + " (command could not start or timed out)") from None
    if result.returncode:
        raise SetupError(failure)


def install(runtime):
    uv = shutil.which("uv")
    if not uv:
        raise SetupError("Install uv, then rerun setup --install")
    for parent in (runtime.resolve(), *runtime.resolve().parents):
        if (parent / ".git").exists():
            raise SetupError("The isolated runtime must be outside the public checkout")
    environment = os.environ.copy()
    environment["UV_PROJECT_ENVIRONMENT"] = str(runtime)
    run_checked([uv, "sync", "--project", str(APP), "--frozen", "--no-dev", "--no-install-project"],
                "Runtime installation failed; check uv, network access, and runtime directory permissions", env=environment)


def register(harness, runtime, config_path=None):
    python = runtime / "bin/python"
    if not python.exists():
        raise SetupError("Install the runtime before registering a harness")
    command = [str(python), "-I", str(APP / "register.py"), harness, str(APP / "agent.py")]
    if config_path:
        command.append(str(config_path.expanduser().absolute()))
    run_checked(command, "Harness registration failed; check config format, permissions, concurrent edits, and that its path is outside the checkout and Joplin private/runtime directories")


def doctor(config, runtime):
    load_policy(config)
    server = load_server(config)
    if not (runtime / "bin/python").exists():
        raise SetupError("Runtime is missing; run setup --install")
    api(server, "notes", params={"limit": 1, "fields": "id"})
    run_checked([str(runtime / "bin/python"), "-I", str(APP / "check.py"), str(config)],
                "MCP verification failed; check hierarchy destinations, notebook scope, token, and Web Clipper")
    print("Private configuration, authentication, hierarchy, and MCP handshake: OK")


def setup(args, config, runtime):
    if args.install:
        install(runtime)
        print("Pinned Joplin runtime installed")
    if args.profile:
        policy = make_policy(args.profile)
        validate_policy(policy)
        atomic_private(config / "policy.json", json.dumps(policy, indent=2) + "\n")
        print("Private notebook policy saved; restart existing Joplin MCP connections")
    if args.credentials:
        token = getpass.getpass("Joplin Web Clipper token (hidden): ").strip()
        server = {"token": token, "host": "127.0.0.1", "port": args.port,
                  "timeout": 15, "verify_ssl": False}
        if len(token) < 10:
            raise SetupError("Token is missing or invalid")
        atomic_private(config / "server.json", json.dumps(server, indent=2) + "\n")
        print("Private credentials saved")
    if args.hierarchy:
        load_policy(config)
        load_server(config)
        run_checked([str(runtime / "bin/python"), "-I", str(APP / "check.py"), str(config), "--hierarchy"],
                    "Hierarchy setup failed; check existing root, unambiguous destination paths, notebook scope, token, and Web Clipper")
        print("Hierarchy notebooks prepared; existing content preserved")
    for harness in args.harness:
        load_policy(config)
        load_server(config)
        register(harness, runtime, args.harness_config)
        print(f"Registered Joplin in {harness}; reload its MCP connections")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("serve", help="Validate private policy and run one independent stdio server")
    commands.add_parser("context", help="Print the active policy and hierarchy, without reading credentials")
    commands.add_parser("doctor", help="Check the live local API and MCP connection without displaying notes")
    p = commands.add_parser("setup", help="Install runtime, provision private configuration, and register harnesses")
    p.add_argument("--install", action="store_true")
    p.add_argument("--profile", choices=("work", "home"))
    p.add_argument("--credentials", action="store_true")
    p.add_argument("--hierarchy", action="store_true", help="Create configured role notebooks under an existing root")
    p.add_argument("--port", type=int, default=41184)
    p.add_argument("--harness", choices=("codex", "antigravity"), action="append", default=[])
    p.add_argument("--harness-config", type=Path, help="Explicit config path selected from the harness UI")
    args = parser.parse_args()
    config, runtime = locations()
    try:
        if args.command == "serve":
            launch(config, runtime)
        elif args.command == "context":
            print(json.dumps(load_policy(config), indent=2, ensure_ascii=False))
        elif args.command == "doctor":
            doctor(config, runtime)
        else:
            setup(args, config, runtime)
    except SetupError as error:
        print(f"joplin-agent: {error}", file=sys.stderr)
        return 1
    except (OSError, ValueError):
        print("joplin-agent: local configuration operation failed; check permissions and JSON syntax", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

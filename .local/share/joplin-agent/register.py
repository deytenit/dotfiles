"""Preserve unrelated harness settings when registering the local MCP command."""

import json
import os
from pathlib import Path
import stat
import sys
import tempfile

import tomlkit


def merged(text, harness, command, args):
    if harness == "codex":
        data = tomlkit.parse(text)
        servers = data.setdefault("mcp_servers", tomlkit.table())
        servers["joplin"] = {"command": command, "args": args, "startup_timeout_sec": 30, "tool_timeout_sec": 60}
        return tomlkit.dumps(data)
    data = json.loads(text) if text.strip() else {}
    if not isinstance(data, dict) or not isinstance(data.get("mcpServers", {}), dict):
        raise ValueError("Expected a JSON object with an mcpServers object")
    data.setdefault("mcpServers", {})["joplin"] = {"command": command, "args": args}
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def register_file(path, harness, command, args):
    destination = path.resolve()
    protected = (Path.home() / ".config/joplin-agent", Path.home() / ".local/share/joplin-agent")
    if any(destination.is_relative_to(root.resolve()) for root in protected):
        raise ValueError("Harness configuration cannot replace Joplin private or runtime files")
    if any((parent / ".git").exists() for parent in (destination, *destination.parents)):
        raise ValueError("Harness registration must be local, outside a public checkout")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("Refusing to modify a symlinked harness configuration")
    existed = path.exists()
    original = path.read_bytes() if existed else b""
    updated = merged(original.decode(), harness, command, args).encode()
    if original == updated:
        return
    if existed:
        fd, backup = tempfile.mkstemp(prefix=path.name + ".joplin-backup-", dir=path.parent)
        with os.fdopen(fd, "wb") as stream:
            stream.write(original)
    fd, temporary = tempfile.mkstemp(prefix=".joplin-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(updated)
            stream.flush()
            os.fsync(stream.fileno())
        if path.is_symlink() or (path.read_bytes() if path.exists() else b"") != original:
            raise ValueError("Harness configuration changed during registration")
        if existed:
            mode = stat.S_IMODE(path.stat().st_mode) & 0o600
            os.chmod(temporary, mode | 0o600)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    harness, entry = sys.argv[1:3]
    home = Path.home()
    path = Path(sys.argv[3]) if len(sys.argv) > 3 else (
        home / ".codex/config.toml" if harness == "codex" else home / ".gemini/config/mcp_config.json")
    try:
        register_file(path, harness, sys.executable, ["-I", entry, "serve"])
    except Exception:
        print("Joplin registration failed: check configuration format, permissions, and concurrent edits", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

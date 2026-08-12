"""Vendored dependencies for dotfiles bootstrap."""
import sys
from pathlib import Path

WHEEL_FILES = ("questionary-2.1.1-py3-none-any.whl", "prompt_toolkit-3.0.52-py3-none-any.whl", "wcwidth-0.8.2-py3-none-any.whl")
class VendorError(RuntimeError): pass
def activate_wheels(require=False):
    paths = tuple(Path(__file__).parent / "wheels" / name for name in WHEEL_FILES); missing = tuple(p for p in paths if not p.is_file())
    if require and missing: raise VendorError("Missing vendored UI packages: " + ", ".join(map(str, missing)))
    for path in reversed(tuple(p for p in paths if p.is_file())):
        if str(path) not in sys.path: sys.path.insert(0, str(path))
    return tuple(p for p in paths if p.is_file())

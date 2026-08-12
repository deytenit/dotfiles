#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent
if sys.version_info < (3, 10):
    print("Python 3.10 or newer is required.", file=sys.stderr); raise SystemExit(1)
sys.path.insert(0, str(REPO_ROOT / ".local/share"))
from dotfiles.vendor import activate_wheels
from dotfiles.strap.app import run_bootstrap
def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--all", action="store_true"); args = parser.parse_args()
    activate_wheels(require=False); return run_bootstrap(REPO_ROOT, install_all=args.all)
if __name__ == "__main__": raise SystemExit(main())

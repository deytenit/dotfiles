#!/usr/bin/env python3

import sys
import json
from subprocess import run

NEXT_STATUS = {
    "default": "invisible",
    "invisible": "dnd",
    "dnd": "default"
}

def get_status():
    return run(["makoctl", "mode"], capture_output=True, encoding="utf-8").stdout.strip()

def set_status(mode):
    return run(["makoctl", "mode", "-s", mode], capture_output=True, encoding="utf-8").stdout.strip()

status = get_status()

if len(sys.argv) > 1:
    status = set_status(NEXT_STATUS[status])
else:
    output = {"text": status,
                "class": status,
                "alt": status}


    sys.stdout.write(json.dumps(output) + "\n")
    sys.stdout.flush()

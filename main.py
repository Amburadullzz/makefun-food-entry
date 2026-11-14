#!/usr/bin/env python3
"""make.fun entry: publish entry.png into the harness output directory.

Standard library only (Python 3.13+). The image is located next to this file
through ``os.path.dirname(os.path.abspath(__file__))``, the destination
directory is created when missing, and the bytes are copied verbatim so the
published file is byte-identical to the source.

Destination directory resolution order:
    1. $MAKEFUN_OUTPUT_DIR, when set to a non-empty value
    2. /output  (make.fun runner default)

Exit codes:
    0  image copied and verified
    1  source missing, destination not writable, or copy did not round-trip
"""

from __future__ import annotations

import os
import shutil
import sys

IMAGE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"


def source_path() -> str:
    """Absolute path of entry.png sitting beside this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, IMAGE_NAME)


def output_dir() -> str:
    """Destination directory: $MAKEFUN_OUTPUT_DIR if usable, else /output."""
    configured = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    return configured or DEFAULT_OUTPUT_DIR


def same_bytes(left: str, right: str) -> bool:
    """Compare two files chunk by chunk."""
    with open(left, "rb") as a, open(right, "rb") as b:
        while True:
            chunk_a = a.read(1 << 16)
            chunk_b = b.read(1 << 16)
            if chunk_a != chunk_b:
                return False
            if not chunk_a:
                return True


def main() -> int:
    source = source_path()
    if not os.path.isfile(source):
        print(f"error: source image not found: {source}", file=sys.stderr)
        return 1

    target_dir = output_dir()
    try:
        os.makedirs(target_dir, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot create {target_dir}: {exc}", file=sys.stderr)
        return 1

    destination = os.path.join(target_dir, IMAGE_NAME)
    try:
        # copyfile moves raw bytes only: no re-encoding, no metadata, no symlinks.
        shutil.copyfile(source, destination)
    except OSError as exc:
        print(f"error: cannot write {destination}: {exc}", file=sys.stderr)
        return 1

    if not same_bytes(source, destination):
        print(f"error: copy mismatch for {destination}", file=sys.stderr)
        return 1

    size = os.path.getsize(destination)
    print(f"copied {source} -> {destination} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

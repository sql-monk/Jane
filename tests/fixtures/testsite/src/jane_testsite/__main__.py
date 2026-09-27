"""``python -m jane_testsite [--host H] [--port P]`` or ``--write-expected FILE``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .server import make_server
from .site import expected


def expected_json() -> str:
    return json.dumps(expected().as_dict(), indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="jane-testsite", description="Jane test site server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--verbose", action="store_true", help="log every request")
    ap.add_argument("--write-expected", type=Path, metavar="FILE", help="write expected URL sets and exit")
    ns = ap.parse_args(argv)
    if ns.write_expected:
        ns.write_expected.write_text(expected_json(), encoding="utf-8", newline="\n")
        print(f"written {ns.write_expected}")
        return 0
    server = make_server(ns.host, ns.port, quiet=not ns.verbose)
    print(f"Jane testsite on http://{ns.host}:{server.server_address[1]}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

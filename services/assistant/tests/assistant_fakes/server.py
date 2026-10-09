"""A contract fake served over real HTTP (uvicorn in a thread) - for tests that need real sockets and timeouts."""

from __future__ import annotations

import socket
import threading
import time
from typing import Any

import uvicorn

from . import START_S

__all__ = ["Server"]


class Server:
    def __init__(self, app: Any) -> None:
        # the socket is bound here and handed to uvicorn: no other process can take the port in between
        # (a free port picked and released first was taken by a parallel test run: WinError 10048)
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.port = int(self.sock.getsockname()[1])
        self.server = uvicorn.Server(uvicorn.Config(app, log_level="warning", lifespan="off"))
        self.thread = threading.Thread(target=self.server.run, kwargs={"sockets": [self.sock]}, daemon=True)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def __enter__(self) -> Server:
        self.thread.start()
        deadline = time.monotonic() + START_S
        while not self.server.started:
            if time.monotonic() > deadline:
                raise RuntimeError("fake server did not start")
            time.sleep(0.02)
        return self

    def __exit__(self, *exc: object) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)
        self.sock.close()

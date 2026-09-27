"""Execution context passed to the extractor callable as ``ctx``."""

from __future__ import annotations

import base64
import codecs
from collections.abc import Callable, Mapping
from typing import Any

from .types import Diagnostic, DiagnosticLevel

__all__ = ["Context", "DiagnosticsLog"]


class DiagnosticsLog:
    """``ctx.log``: messages that end up in ``HandlerResult.diagnostics.messages``.

    Use it instead of ``print``: stdout/stderr of the sandbox go only to the (truncated) execution log.
    """

    def __init__(self, material_id: str | None = None) -> None:
        self.messages: list[Diagnostic] = []
        self._material_id = material_id

    def add(
        self,
        level: DiagnosticLevel,
        message: str,
        *,
        code: str | None = None,
        selector: str | None = None,
        pointer: str | None = None,
    ) -> None:
        diag: Diagnostic = {"level": level, "message": message}
        if code:
            diag["code"] = code
        if selector:
            diag["selector"] = selector
        if pointer:
            diag["pointer"] = pointer
        if self._material_id:
            diag["material_id"] = self._material_id
        self.messages.append(diag)

    def debug(self, message: str, **kw: Any) -> None:
        self.add("debug", message, **kw)

    def info(self, message: str, **kw: Any) -> None:
        self.add("info", message, **kw)

    def warning(self, message: str, **kw: Any) -> None:
        self.add("warning", message, **kw)

    def error(self, message: str, **kw: Any) -> None:
        self.add("error", message, **kw)


def _inline_bytes(content: Mapping[str, Any]) -> bytes:
    data = str(content.get("data", ""))
    if content.get("encoding") == "base64":
        return base64.b64decode(data)
    return data.encode("utf-8")


class Context:
    """What the extractor may use besides ``material`` and ``params``.

    * :meth:`bytes` / :meth:`text` - content of the material (inline or blob: the runtime has already fetched
      and checked it; the extractor never downloads anything, there is no network in the sandbox);
    * :attr:`log` - diagnostics; :attr:`test_mode` - run without writing to working data (informative);
    * :attr:`params` - the same parameters the callable receives.
    """

    def __init__(
        self,
        material: Mapping[str, Any],
        params: Mapping[str, Any] | None = None,
        *,
        content_loader: Callable[[], bytes] | None = None,
        test_mode: bool = False,
    ) -> None:
        self.material = material
        self.params: Mapping[str, Any] = params or {}
        self.test_mode = test_mode
        material_id = material.get("material_id") if isinstance(material, Mapping) else None
        self.log = DiagnosticsLog(material_id if isinstance(material_id, str) else None)
        self._loader = content_loader
        self._cache: bytes | None = None

    def bytes(self) -> bytes:
        """Raw bytes of the material content."""
        if self._cache is None:
            if self._loader is not None:
                self._cache = self._loader()
            else:
                content = self.material.get("content") or {}
                if content.get("kind") != "inline":
                    raise RuntimeError("material content is not available (blob without a loaded copy)")
                self._cache = _inline_bytes(content)
        return self._cache

    def charset(self) -> str:
        """Charset from the content, then the format, then ``utf-8`` (unknown names fall back to utf-8)."""
        content = self.material.get("content") or {}
        fmt = self.material.get("format") or {}
        for candidate in (content.get("charset"), fmt.get("charset")):
            if isinstance(candidate, str) and candidate:
                try:
                    codecs.lookup(candidate)
                except LookupError:
                    continue
                return candidate
        return "utf-8"

    def text(self, errors: str = "replace") -> str:
        """Content decoded as text (inline ``utf-8`` content is already text)."""
        content = self.material.get("content") or {}
        if self._loader is None and content.get("kind") == "inline" and content.get("encoding") == "utf-8":
            return str(content.get("data", ""))
        return self.bytes().decode(self.charset(), errors=errors)

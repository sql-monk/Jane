"""Secret references of managed connections and allowlists of their destinations (ADR-0006, R17).

A connection decides *where* a resolved secret goes, and connections arrive through ``PUT /v1/connections/{id}``,
so an executor (storage, llm, the collectors) restricts both ends with one policy:

* :class:`SecretPolicy` - ``env:VAR`` only for variables with the configured prefix (default ``JANE_SECRET_``;
  a name equal to the prefix or not a plain upper-case variable name is refused), ``file:<path>`` only for a file
  strictly inside the configured directory (default ``/run/secrets``; ``None`` disables files; the path is
  resolved first, so ``..`` and symlinks do not escape), ``vault:`` and anything else refused. Violations are
  ``FieldError`` with code ``secret_ref_not_allowed`` (``PUT`` -> 422); a connection stored bypassing the API gets
  no secrets when it is resolved.
* :func:`read_secret_file` - reads the resolved path through pinned filesystem objects (POSIX: directory
  descriptors and ``O_NOFOLLOW`` on every component; Windows: a non-delete-sharing handle per component, reparse
  points refused, final path checked), so a component swapped after the check is not followed (TOCTOU).
* :class:`HostAllowlist` - ``hostname`` (any port) or ``hostname:port`` entries; :func:`parse_host_port` - the
  strict ``hostname[:port]`` parser shared with the ``ContentRef`` reader's ``download_url`` allowlist.
* :class:`OriginAllowlist` - exact ``http(s)://host[:port]`` origins (default ports normalized); a checked URL
  may have a path, never userinfo, backslashes or whitespace.
"""

from __future__ import annotations

import os
import re
import stat
import sys
from collections.abc import Iterable, Mapping
from contextlib import ExitStack
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from jane_kit.errors import FieldError

__all__ = [
    "SECRET_REF_NOT_ALLOWED",
    "HostAllowlist",
    "OriginAllowlist",
    "SecretPolicy",
    "parse_host_port",
    "read_secret_file",
]

SECRET_REF_NOT_ALLOWED = "secret_ref_not_allowed"  # noqa: S105 - an error code, not a secret

_ENV_NAME = re.compile(r"[A-Z_][A-Z0-9_]{0,127}\Z")
_LABEL = r"(?!-)[A-Za-z0-9_-]{1,63}(?<!-)"
_HOST_PORT = re.compile(rf"(?P<host>{_LABEL}(?:\.{_LABEL})*)(?::(?P<port>[0-9]{{1,5}}))?", re.ASCII)
_DEFAULT_PORTS = {"http": 80, "https": 443}


def parse_host_port(value: object) -> tuple[str, int | None] | None:
    """Strict ``hostname[:port]`` -> ``(lower-case host, port)``; anything else (userinfo, IPv6 literal, trailing
    dot, path, whitespace, port outside 1..65535) -> ``None``."""
    if not isinstance(value, str) or len(value) > 300:
        return None
    m = _HOST_PORT.fullmatch(value)
    if m is None or len(m["host"]) > 253:
        return None
    if m["port"] is None:
        return m["host"].lower(), None
    port = int(m["port"])
    return (m["host"].lower(), port) if 0 < port < 65536 else None


@dataclass(frozen=True)
class HostAllowlist:
    """``hostname`` entries allow any port, ``hostname:port`` entries only that port; an invalid entry raises
    ``ValueError`` (a typo in the setting stops the service at start)."""

    entries: tuple[str, ...] = ()
    _allowed: frozenset[tuple[str, int | None]] = field(init=False, repr=False, default=frozenset())

    def __post_init__(self) -> None:
        allowed = set()
        for entry in self.entries:
            parsed = parse_host_port(entry.strip()) if isinstance(entry, str) else None
            if parsed is None:
                raise ValueError(f"host allowlist entry {entry!r} must be hostname or hostname:port")
            allowed.add(parsed)
        object.__setattr__(self, "_allowed", frozenset(allowed))

    @classmethod
    def of(cls, entries: Iterable[str]) -> HostAllowlist:
        return cls(tuple(entries))

    def allows(self, host: str, port: int | None) -> bool:
        """``port=None`` (not known) matches only ``hostname`` entries."""
        host = host.lower()
        return (host, None) in self._allowed or (port is not None and (host, port) in self._allowed)


def _origin(url: object, *, allow_path: bool) -> tuple[str, str, int] | None:
    if not isinstance(url, str) or "\\" in url or any(c.isspace() for c in url) or len(url) > 2048:
        return None
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:  # a bad port ("...:99999", "...:abc") or bracket
        return None
    if (
        parts.scheme not in _DEFAULT_PORTS
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or (not allow_path and (parts.path not in {"", "/"} or parts.query or parts.fragment))
        or port == 0
    ):
        return None
    return parts.scheme, parts.hostname.lower().rstrip("."), port or _DEFAULT_PORTS[parts.scheme]


@dataclass(frozen=True)
class OriginAllowlist:
    """Exact ``http(s)://host[:port]`` origins; an entry with a path, userinfo or another scheme raises
    ``ValueError``."""

    entries: tuple[str, ...] = ()
    _origins: frozenset[tuple[str, str, int]] = field(init=False, repr=False, default=frozenset())

    def __post_init__(self) -> None:
        parsed = [_origin(entry, allow_path=False) for entry in self.entries]
        if any(origin is None for origin in parsed):
            raise ValueError("origin allowlist entries must be exact HTTP(S) origins (scheme://host[:port])")
        object.__setattr__(self, "_origins", frozenset(o for o in parsed if o is not None))

    @classmethod
    def of(cls, entries: Iterable[str]) -> OriginAllowlist:
        return cls(tuple(entries))

    def allows(self, url: object) -> bool:
        """The origin of ``url`` (path allowed; userinfo, backslash, whitespace refused) is on the list."""
        origin = _origin(url, allow_path=True)
        return origin is not None and origin in self._origins

    def __str__(self) -> str:
        return str(sorted(f"{s}://{h}:{p}" for s, h, p in self._origins))


@dataclass(frozen=True)
class SecretPolicy:
    """Bounds of ``secret_refs`` (see the module docstring)."""

    env_prefix: str = "JANE_SECRET_"
    files_dir: Path | None = Path("/run/secrets")

    def secret_file(self, ref: str) -> Path | None:
        """Resolved path (``..`` and symlinks resolved) of an allowed ``file:`` reference, else ``None``.

        The reader must still pin every component (:func:`read_secret_file`): resolving a pathname alone does
        not prevent a later replacement of the target or a parent directory.
        """
        if self.files_dir is None or not ref.startswith("file:") or not ref[5:]:
            return None
        try:
            path = Path(ref[5:]).resolve()
            base = self.files_dir.resolve()
        except (OSError, RuntimeError, ValueError):
            return None
        return path if path != base and path.is_relative_to(base) else None

    def ref_error(self, ref: str) -> str | None:
        """Why a secret reference is not allowed (``None`` if allowed)."""
        if ref.startswith("env:"):
            name = ref[4:]
            if (
                not self.env_prefix
                or not _ENV_NAME.fullmatch(name)
                or not name.startswith(self.env_prefix)
                or name == self.env_prefix
            ):
                return f"env: references must name variables starting with {self.env_prefix!r}"
            return None
        if ref.startswith("file:"):
            if self.files_dir is None:
                return "file: references are disabled"
            if self.secret_file(ref) is None:
                return f"file: references must point to a file inside {self.files_dir}"
            return None
        if ref.startswith("vault:"):
            return "vault: references are not configured in this service"
        return "unknown secret reference scheme"

    def violations(self, refs: object, pointer: str = "/secret_refs") -> list[FieldError]:
        """``FieldError`` (code ``secret_ref_not_allowed``) for every reference of ``refs`` that is not allowed."""
        if refs is None:
            return []
        if not isinstance(refs, Mapping):
            return [FieldError(pointer=pointer, code=SECRET_REF_NOT_ALLOWED, message="must be an object")]
        return [
            FieldError(pointer=f"{pointer}/{name}", code=SECRET_REF_NOT_ALLOWED, message=message)
            for name, ref in refs.items()
            if (message := self.ref_error(str(ref))) is not None
        ]

    def resolve(self, ref: str, environ: Mapping[str, str] | None = None) -> str | None:
        """Value of an allowed ``env:VAR`` / ``file:<path>``; ``None`` if missing, empty or not allowed."""
        if self.ref_error(ref) is not None:
            return None
        if ref.startswith("env:"):
            env = os.environ if environ is None else environ
            return env.get(ref[4:]) or None
        path = self.secret_file(ref)  # re-resolved now; the raw reference is never opened
        return read_secret_file(path) if path is not None else None


# ---------------------------------------------------------------------------------------------- pinned reading
def read_secret_file(path: Path) -> str | None:
    """Text of the resolved secret ``path`` (stripped; ``None`` if empty). Fails closed (``None``) on a changed
    component, a non-regular file or an unsupported platform; validation precedes reading any secret bytes."""
    try:
        if not path.is_absolute():
            return None
        if os.name == "nt":
            return _windows_text(path).strip() or None
        if (
            os.name == "posix"
            and os.open in os.supports_dir_fd
            and all(hasattr(os, flag) for flag in ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK"))
        ):
            return _posix_text(path).strip() or None
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    return None


def _posix_text(path: Path) -> str:
    nofollow = int(getattr(os, "O_NOFOLLOW", 0))
    directory_flags = os.O_RDONLY | int(getattr(os, "O_DIRECTORY", 0)) | nofollow
    with ExitStack() as stack:
        parent = os.open(path.anchor, directory_flags)
        stack.callback(os.close, parent)
        for part in path.parts[1:-1]:
            parent = os.open(part, directory_flags, dir_fd=parent)
            stack.callback(os.close, parent)
            if not stat.S_ISDIR(os.fstat(parent).st_mode):
                raise OSError("secret path component is not a directory")
        leaf = os.open(path.name, os.O_RDONLY | nofollow | int(getattr(os, "O_NONBLOCK", 0)), dir_fd=parent)
        stack.callback(os.close, leaf)
        if not stat.S_ISREG(os.fstat(leaf).st_mode):
            raise OSError("secret is not a regular file")
        with os.fdopen(leaf, "r", encoding="utf-8", closefd=False) as stream:
            return stream.read()


if sys.platform == "win32":

    def _windows_text(path: Path) -> str:
        import ctypes
        import msvcrt
        from ctypes import wintypes

        class AttributeTag(ctypes.Structure):
            _fields_ = [("attributes", wintypes.DWORD), ("tag", wintypes.DWORD)]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        ]
        create.restype = wintypes.HANDLE
        information = kernel.GetFileInformationByHandleEx
        information.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
        information.restype = wintypes.BOOL
        final_path = kernel.GetFinalPathNameByHandleW
        final_path.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
        final_path.restype = wintypes.DWORD
        close = kernel.CloseHandle
        close.argtypes = [wintypes.HANDLE]
        close.restype = wintypes.BOOL

        # Opening the link/reparse object itself avoids following a replacement. Holding every directory
        # without FILE_SHARE_DELETE prevents it being renamed or replaced during the rest of this walk.
        open_reparse = 0x00200000
        backup_semantics = 0x02000000
        reparse_attribute = 0x400
        directory_attribute = 0x10
        invalid = wintypes.HANDLE(-1).value
        handles: list[int] = []
        try:
            current = Path(path.anchor)
            for index in range(len(path.parts)):
                directory = index < len(path.parts) - 1
                if index:
                    current /= path.parts[index]
                # FILE_READ_ATTRIBUTES for directories; GENERIC_READ for the regular secret file.
                access = 0x80 if directory else 0x80000000
                # FILE_SHARE_READ | FILE_SHARE_WRITE on directories, FILE_SHARE_READ only on the leaf.
                sharing = 3 if directory else 1
                handle = create(str(current), access, sharing, None, 3, open_reparse | backup_semantics, None)
                if handle is None or handle == invalid:
                    raise ctypes.WinError(ctypes.get_last_error())
                handles.append(handle)
                attributes = AttributeTag()
                if not information(handle, 9, ctypes.byref(attributes), ctypes.sizeof(attributes)):
                    raise ctypes.WinError(ctypes.get_last_error())
                if attributes.attributes & reparse_attribute:
                    raise OSError("secret path component is a reparse point")
                if bool(attributes.attributes & directory_attribute) != directory:
                    raise OSError("secret path component has the wrong type")
            handle = handles[-1]
            needed = final_path(handle, None, 0, 0)
            if not needed:
                raise ctypes.WinError(ctypes.get_last_error())
            buffer = ctypes.create_unicode_buffer(needed + 1)
            count = final_path(handle, buffer, len(buffer), 0)
            if not 0 < count < len(buffer):
                raise ctypes.WinError(ctypes.get_last_error())
            opened_path = buffer.value
            if opened_path.startswith("\\\\?\\UNC\\"):
                opened_path = "\\\\" + opened_path[8:]
            elif opened_path.startswith("\\\\?\\"):
                opened_path = opened_path[4:]
            if Path(opened_path) != path:
                raise OSError("opened secret is not the checked path")
            # The CRT descriptor owns the same validated handle; it never reopens the pathname.
            leaf = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
            handles.pop()
            try:
                if not stat.S_ISREG(os.fstat(leaf).st_mode):
                    raise OSError("secret is not a regular file")
                with os.fdopen(leaf, "r", encoding="utf-8", closefd=False) as stream:
                    return stream.read()
            finally:
                os.close(leaf)
        finally:
            for handle in reversed(handles):
                close(handle)
else:

    def _windows_text(path: Path) -> str:
        raise OSError("Windows secret reader is unavailable")

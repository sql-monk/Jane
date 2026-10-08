"""Read an already resolved secret path through verified, pinned filesystem objects.

POSIX uses directory descriptors and O_NOFOLLOW at every component. Windows pins each component with
a non-delete-sharing handle and refuses reparse points. Validation precedes reading any secret bytes.
This service-owned helper is mirrored in the other affected service; jane-kit is outside this assignment.
"""

from __future__ import annotations

import os
import stat
import sys
from contextlib import ExitStack
from pathlib import Path


def read_secret_file(path: Path) -> str | None:
    """Fail closed on a changed component, non-regular file or unsupported platform."""
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

"""Bounded read-only local inputs; no provider, GPU, solver or key imports."""
import hashlib
from pathlib import Path
import re
import stat


MAXIMUM_INPUT_BYTES = 16*1024**2


def confined_path(root, relative):
    root = Path(root).resolve(strict=True)
    if not isinstance(relative, str):
        raise ValueError("input path must be a string")
    rel = Path(relative)
    if not rel.parts or rel.is_absolute() or ".." in rel.parts or rel.as_posix() != relative:
        raise ValueError("input path must be canonical relative path")
    path = root
    for part in rel.parts:
        path = path/part
        if path.is_symlink():
            raise ValueError("input symlink is not permitted")
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("input must be a regular file")
    return path


def checked_input(root, declaration):
    digest = declaration["sha256"]
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("invalid input SHA-256")
    path = confined_path(root, declaration["path"])
    if path.stat().st_size > MAXIMUM_INPUT_BYTES:
        raise ValueError("input exceeds fixed byte bound")
    with path.open("rb") as stream:
        content = stream.read(MAXIMUM_INPUT_BYTES+1)
    if len(content) > MAXIMUM_INPUT_BYTES:
        raise ValueError("input exceeds fixed byte bound")
    if hashlib.sha256(content).hexdigest() != digest:
        raise ValueError("input hash mismatch")
    if "bytes" in declaration and (type(declaration["bytes"]) is not int or declaration["bytes"] != len(content)):
        raise ValueError("input byte size mismatch")
    return content


def collection_file(directory, declaration):
    name = declaration["path"]
    if not isinstance(name, str) or Path(name).name != name:
        raise ValueError("collection assets must use plain basenames")
    checked_input(directory, declaration)
    return confined_path(directory, name)

"""Pre-write JSON quota admission for a task-owned single-writer output tree.

Frozen historical writers are unchanged. New runners must use this for every
normal JSON product, including their final summary, and reserve space for a
small failure receipt. Concurrent writers require an external shared lock.
"""
import json
from pathlib import Path
import shutil

from butterfly._paired_startup import write_json


class ArtifactQuotaExceeded(ValueError):
    """The complete serialized artifact will not fit the declared quota."""


def check_size(existing,additional,limit):
    if any(type(v) is not int or v < 0 for v in (existing,additional,limit)):
        raise ValueError('nonnegative integer byte counts required')
    if existing+additional > limit:
        raise ArtifactQuotaExceeded(f'complete output would use {existing+additional} bytes; limit is {limit}')


def directory_bytes(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('existing non-symlink output directory required')
    total = 0
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('output quota does not follow symlinks')
        if path.is_file():
            total += path.stat().st_size
    return total


def write_bounded_json(root,path,value,*,limit_bytes,minimum_free_bytes=0,reserve_bytes=0):
    """Reject an oversized summary before creating it; same bytes as write_json."""
    root,path = Path(root),Path(path)
    if any(type(v) is not int or v < 0 for v in (limit_bytes,minimum_free_bytes,reserve_bytes)) or reserve_bytes > limit_bytes:
        raise ValueError('valid nonnegative quota and reserves required')
    used = directory_bytes(root)
    if not path.parent.is_dir() or not path.resolve().is_relative_to(root.resolve()) or path.exists() or path.is_symlink():
        raise ValueError('fresh output path within the declared tree required')
    # Match the canonical existing writer exactly, including the final newline.
    size = 1
    check_size(used,size,limit_bytes-reserve_bytes)
    encoder = json.JSONEncoder(sort_keys=True,indent=2,allow_nan=False)
    for chunk in encoder.iterencode(value):
        size += len(chunk.encode('utf-8'))
        check_size(used,size,limit_bytes-reserve_bytes)
    if shutil.disk_usage(root).free < minimum_free_bytes+reserve_bytes+size:
        raise ArtifactQuotaExceeded('free-space floor would be crossed by the complete artifact')
    write_json(path,value)
    if path.stat().st_size != size:
        raise RuntimeError('canonical serialization size changed')
    return dict(bytes=size,output_bytes_after=used+size,limit_bytes=limit_bytes,reserve_bytes=reserve_bytes)

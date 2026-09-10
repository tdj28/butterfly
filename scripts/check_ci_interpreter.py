#!/usr/bin/env python3
"""Fail if CI silently uses a different interpreter distribution or version."""
import json
import os
from pathlib import Path
import platform
import sys


def validate(base_prefix, install_root, actual_version, requested_version):
    if not install_root or not requested_version:
        raise ValueError('explicit managed install root and requested version required')
    root, actual = Path(install_root), Path(base_prefix)
    if not root.is_absolute() or not actual.is_absolute() or not actual.resolve().is_relative_to(root.resolve()):
        raise ValueError('interpreter does not belong to the managed install root')
    wanted = tuple(int(v) for v in requested_version.split('.'))
    if len(wanted) not in (2, 3) or tuple(actual_version[:len(wanted)]) != wanted:
        raise ValueError('actual interpreter version differs from matrix request')
    return True


if __name__ == '__main__':
    validate(sys.base_prefix, os.environ.get('UV_PYTHON_INSTALL_DIR'),
             sys.version_info, os.environ.get('UV_PYTHON'))
    print(json.dumps(dict(managed_interpreter_verified=True, python=platform.python_version(),
        implementation=platform.python_implementation(), compiler=platform.python_compiler(),
        executable=sys.executable, base_prefix=sys.base_prefix), sort_keys=True))

#!/usr/bin/env python3
"""Operational NPZ-cache adapter around the unchanged frozen EXP-494 audit."""
import argparse
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import audit_exp494_periodic_winding_transport as frozen


class ArrayArchive(dict):
    @property
    def files(self):
        return list(self)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def eager_loader(original):
    def load(*args, **kwargs):
        raw = original(*args, **kwargs)
        if not isinstance(raw, np.lib.npyio.NpzFile):
            return raw
        try:
            if len(raw.files) > 64:
                raise ValueError("unexpected large archive schema")
            arrays, size = ArrayArchive(), 0
            for name in raw.files:
                value = raw[name]
                size += value.nbytes
                if value.dtype.hasobject or size > 128*1024**2:
                    raise ValueError("unsafe/oversized cached arrays")
                value.setflags(write=False)
                arrays[name] = value
            return arrays
        finally:
            raw.close()
    return load


def audit(directory, summary_sha):
    original = np.load
    with patch.object(np,"load",eager_loader(original)):
        result = frozen.audit(directory,summary_sha)
    return dict(result,io_adapter=dict(path="scripts/audit_exp494_cached.py",
        sha256=frozen.run.sha256(Path(__file__)),
        scope="Load each NPZ member once as a read-only array; unchanged frozen numerical checks and raw hashes."))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--summary-sha256",required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    result = audit(args.run,args.summary_sha256)
    frozen.run.write_json(args.output,result)
    import json
    print(json.dumps(result))


if __name__ == "__main__":
    main()

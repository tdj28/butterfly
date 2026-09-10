"""Single-writer quota adapters; scientific producer bytes remain frozen."""
from contextlib import contextmanager, ExitStack
import gzip
import io
from pathlib import Path
import shutil
from unittest.mock import patch

from butterfly.bounded_json import check_size, directory_bytes, write_bounded_json, ArtifactQuotaExceeded
from butterfly.decimal_taylor import StreamArchive


class Sink:
    """Admit each compressed chunk; no concurrent writes while this sink is open."""
    def __init__(self, root, path, limits):
        self.used = directory_bytes(root)
        self.root, self.limits, self.written = root, limits, 0
        if path.exists() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('fresh in-tree binary path required')
        self.file = path.open('xb')

    def write(self, data):
        p = self.limits
        check_size(self.used+self.written, len(data), p['output_bytes']-p['failure_reserve_bytes'])
        if shutil.disk_usage(self.root).free < p['minimum_free_bytes']+p['failure_reserve_bytes']+len(data):
            raise ArtifactQuotaExceeded('compressed product free-space floor')
        n = self.file.write(data)
        self.file.flush()
        self.written += n
        return n

    def tell(self):
        return self.file.tell()

    def flush(self):
        return self.file.flush()

    def close(self):
        self.file.close()


@contextmanager
def producers(base, root, limits):
    """Route the exact three producer boundaries through pre-write admission."""
    def json_write(path, value):
        return write_bounded_json(root, path, value, limit_bytes=limits['output_bytes'],
            minimum_free_bytes=limits['minimum_free_bytes'], reserve_bytes=limits['failure_reserve_bytes'])

    original_npz = base.np.savez_compressed
    def npz(stream, **raw):
        # Only one trajectory product is buffered; output bytes are unchanged.
        memory = io.BytesIO()
        original_npz(memory, **raw)
        data = memory.getbuffer()
        check_size(directory_bytes(root), len(data), limits['output_bytes']-limits['failure_reserve_bytes'])
        if shutil.disk_usage(root).free < limits['minimum_free_bytes']+limits['failure_reserve_bytes']+len(data):
            raise ArtifactQuotaExceeded('NPZ product free-space floor')
        stream.write(data)
        stream.flush()

    class Archive(StreamArchive):
        def __init__(self, path, metadata):
            self.file = Sink(root, Path(path), limits)
            try:
                self.stream = gzip.GzipFile(filename='', fileobj=self.file, mode='wb', mtime=0)
                self.emit(dict(header=metadata))
            except BaseException:
                self.file.close()
                raise

        def close(self):
            try:
                self.stream.close()
            finally:
                self.file.close()

    with ExitStack() as stack:
        stack.enter_context(patch.object(base, 'write_json', json_write))
        stack.enter_context(patch.object(base.previous.cycles_run, 'write_json', json_write))
        stack.enter_context(patch.object(base.np, 'savez_compressed', npz))
        stack.enter_context(patch.object(base.numeric, 'StreamArchive', Archive))
        yield json_write

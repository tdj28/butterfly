"""Prospective exact-serialization and quota failures at real producer boundaries."""
import gzip
import io
import json
from pathlib import Path
import numpy as np
import pytest
from butterfly._paired_startup import write_json
from butterfly.bounded_json import ArtifactQuotaExceeded, directory_bytes
from butterfly.decimal_taylor import StreamArchive
from scripts import run_exp507_fold_restoration as run
from scripts.exp507_bounded_products import Sink, producers


def limits(cap=1024**2):
    return dict(output_bytes=cap,minimum_free_bytes=0,failure_reserve_bytes=128)


def test_real_json_bindings_and_restoration(tmp_path):
    base = run.prior.base
    originals = (base.write_json,base.previous.cycles_run.write_json,base.numeric.StreamArchive,base.np.savez_compressed)
    reference = tmp_path/'reference.json'
    write_json(reference,{'x':'unicode \u03b1'})
    with producers(base,tmp_path,limits()) as writer:
        base.write_json(tmp_path/'base.json',{'x':'unicode \u03b1'})
        base.previous.cycles_run.write_json(tmp_path/'cycle.json',{'x':'unicode \u03b1'})
        assert base.write_json is writer
    assert (base.write_json,base.previous.cycles_run.write_json,base.numeric.StreamArchive,base.np.savez_compressed) == originals
    assert reference.read_bytes() == (tmp_path/'base.json').read_bytes() == (tmp_path/'cycle.json').read_bytes()


def test_oversized_json_never_created(tmp_path):
    with producers(run.prior.base,tmp_path,limits(200)):
        with pytest.raises(ArtifactQuotaExceeded):
            run.prior.base.write_json(tmp_path/'oversize.json',{'large':'x'*1000})
    assert not (tmp_path/'oversize.json').exists()


def test_npz_bytes_unchanged_and_quota_applies(tmp_path):
    raw = dict(x=np.arange(10,dtype=float))
    memory = io.BytesIO()
    np.savez_compressed(memory,**raw)
    with producers(run.prior.base,tmp_path,limits()):
        with (tmp_path/'raw.npz').open('xb') as stream:
            np.savez_compressed(stream,**raw)
    assert (tmp_path/'raw.npz').read_bytes() == memory.getvalue()
    used = directory_bytes(tmp_path)
    with producers(run.prior.base,tmp_path,limits(used+128+1)):
        with (tmp_path/'failed.npz').open('xb') as stream:
            with pytest.raises(ArtifactQuotaExceeded):
                np.savez_compressed(stream,**raw)
    assert (tmp_path/'failed.npz').stat().st_size == 0


def test_decimal_stream_exact_bytes_and_decoding(tmp_path):
    ref = StreamArchive(tmp_path/'reference.json.gz',{'x':1})
    ref.step({'q':[1,2,3]})
    ref.finish({'steps':[],'final':[3]})
    ref.close()
    with producers(run.prior.base,tmp_path,limits()):
        out = run.prior.base.numeric.StreamArchive(tmp_path/'bounded.json.gz',{'x':1})
        out.step({'q':[1,2,3]})
        out.finish({'steps':[],'final':[3]})
        out.close()
    assert (tmp_path/'reference.json.gz').read_bytes() == (tmp_path/'bounded.json.gz').read_bytes()
    with gzip.open(tmp_path/'bounded.json.gz','rt') as stream:
        assert len([json.loads(line) for line in stream]) == 3


def test_sink_exact_boundary_reserve_and_no_overrun(tmp_path):
    sink = Sink(tmp_path,tmp_path/'stream',limits(138))
    assert sink.write(b'1234567890') == 10
    with pytest.raises(ArtifactQuotaExceeded):
        sink.write(b'x')
    sink.close()
    assert directory_bytes(tmp_path) == 10


def test_sink_free_floor_and_path_guards(tmp_path):
    p = limits()
    p['minimum_free_bytes'] = 10**30
    sink = Sink(tmp_path,tmp_path/'stream',p)
    with pytest.raises(ArtifactQuotaExceeded):
        sink.write(b'x')
    sink.close()
    with pytest.raises(ValueError):
        Sink(tmp_path,tmp_path/'stream',limits())
    with pytest.raises(ValueError):
        Sink(tmp_path,tmp_path.parent/'escape',limits())


def test_final_summary_included_and_reserved_failure_fits(tmp_path):
    p = dict(limits=limits(1024))
    run.write(tmp_path,tmp_path/'first.json',{'x':'x'*600},p)
    before = directory_bytes(tmp_path)
    with pytest.raises(ArtifactQuotaExceeded):
        run.write(tmp_path,tmp_path/'summary.json',{'x':'x'*400},p)
    assert directory_bytes(tmp_path) == before
    assert not (tmp_path/'summary.json').exists()
    run.write(tmp_path,tmp_path/'failure.json',{'error':'quota'},p,reserve=False)
    assert directory_bytes(tmp_path) < 1024

#!/usr/bin/env python3
"""One-shot, raw-retaining short precision test of six realized inputs."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal as D, localcontext
import gzip
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

from butterfly import decimal_grazing as numeric
from butterfly.decimal_taylor import StreamArchive, load_stream
from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes, write_bounded_json
from scripts.exp507_bounded_products import Sink
from scripts import exp515_precision_analysis as model

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'experiments/manifests/EXP-515-third-return-precision.json'
RECEIPT = 'docs/experiments/receipts/EXP-512-censored-return-extension-result.json'
INPUTS = {RECEIPT: 'c89bb30f90bf26a4f4902e349459b234201a66b00d3d2b4a500d6849fdb96e76'}
MODULES = ['__init__', '_paired_startup', 'atlas', 'augmented_flip', 'basins', 'boundary',
    'bounded_json', 'candidates', 'classify', 'decimal_grazing', 'decimal_taylor', 'hopf',
    'integrate', 'lyapunov', 'models', 'periodic', 'poincare', 'polynomial_census',
    'return_map', 'saddle', 'scan', 'symbolic', 'tiles', 'upo']
SOURCES = sorted(['python/butterfly/'+n+'.py' for n in MODULES]+[
    'scripts/run_exp515_third_return_precision.py', 'scripts/exp515_precision_analysis.py',
    'scripts/audit_exp515_third_return_precision.py', 'scripts/exp507_bounded_products.py',
    'scripts/exp500_census_analysis.py', 'tests/test_exp515_third_return_precision.py',
    'docs/experiments/EXP-515-third-return-precision.md',
    'experiments/manifests/EXP-515-third-return-precision.json', 'pyproject.toml', 'uv.lock'])
KINDS = ['ordinary', 'phase-zero', 'phase-small', 'initial', 'near-initial', 'after-initial']


def utc():
    return datetime.now(timezone.utc).isoformat()


def expected():
    if any(sha256(ROOT/n) != h for n, h in INPUTS.items()):
        raise ValueError('fixed public input differs')
    old = json.loads((ROOT/RECEIPT).read_bytes())
    if old['experiment_id'] != 'EXP-512' or old['passed'] is not True or old['protocol_compliant'] is not True:
        raise ValueError('audited historical receipt required')
    return dict(experiment_id='EXP-515', status='prospective-outcome-informed-precision-diagnostic',
        inputs=INPUTS, cases=model.selection(old), configurations=numeric.CONFIGS, source_paths=SOURCES,
        limits=dict(target_ivps=12, wall_seconds=3600, output_bytes=2*1024**3,
            initial_free_bytes=11*1024**3, minimum_free_bytes=8*1024**3, failure_reserve_bytes=1024**2),
        controls=dict(kinds=KINDS, ivps=12, wall_seconds=180, output_bytes=64*1024**2),
        paid_review='not-requested-human-approval-policy', attempts=1,
        symbolic_chains_verified=False, historical_decisions_changed=False)


def load():
    p = json.loads(PLAN.read_bytes())
    if p != expected():
        raise ValueError('frozen precision plan differs')
    return p


def validate():
    from scripts import audit_exp515_third_return_precision  # noqa: F401
    p = load()
    imported = {Path(m.__file__).resolve().relative_to(ROOT).as_posix()
        for n, m in list(sys.modules.items()) if n.startswith(('butterfly', 'scripts.'))
        and getattr(m, '__file__', None) and Path(m.__file__).resolve().is_relative_to(ROOT)}
    if not imported <= set(p['source_paths']):
        raise ValueError('source closure incomplete: '+str(sorted(imported-set(p['source_paths']))))
    return dict(valid=True, new_integrations=0, cases=6, target_ivps=12)


def startup(p):
    folder = Path(tempfile.mkdtemp(prefix='exp515-startup-')).resolve()
    names = set(p['source_paths']) | set(INPUTS)
    for name in names:
        dest = folder/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/name, dest)
    code = (f'import sys;from pathlib import Path;root=Path({str(folder)!r});'
        f'sys.path[:0]={[str(folder),str(folder/"python")]!r};'
        'from scripts.run_exp515_third_return_precision import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=folder,
                           capture_output=True, text=True, check=True, timeout=180)
    hashes = {n: sha256(folder/n) for n in sorted(names)}
    if hashes != {n: sha256(ROOT/n) for n in sorted(names)} or list(folder.rglob('*.pyc')):
        raise ValueError('isolated source drift or bytecode')
    return dict(passed=True, isolated=True, sources=hashes, stdout=child.stdout,
                stderr=child.stderr, new_integrations=0)


def write(root, path, value, limits, reserve=True):
    return write_bounded_json(root, path, value, limit_bytes=limits['output_bytes'],
        minimum_free_bytes=limits['minimum_free_bytes'],
        reserve_bytes=limits['failure_reserve_bytes'] if reserve else 0)


def produce(case, config, output, limits, budget):
    label = case['id']+'--'+config['name']
    write(output, output/(label+'-started.json'), dict(id=case['id'], configuration=config['name'], utc=utc()), limits)

    class Archive(StreamArchive):
        def __init__(self, path, metadata):
            self.file = Sink(output, path, limits)
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

    budget(True)
    name = label+'.json.gz'
    with patch.object(numeric, 'StreamArchive', Archive):
        raw = numeric.run_profile(output/name, case['initial'], case['field'], case['horizon'], config,
                                  before_step=budget)
    # Release memory only after the complete artifact can be reopened exactly.
    if load_stream(output/name)[1] != raw:
        raise ValueError('complete coefficient archive round trip differs')
    result, certificates = model.analyze(raw, case['section'], before_segment=budget)
    result.update(raw_path=name, certificate_path=label+'-certificates.json')
    write(output, output/result['certificate_path'], certificates, limits)
    write(output, output/(label+'-result.json'), result, limits)
    return result


def control_case(kind):
    if kind not in KINDS:
        raise ValueError('unknown control kind')
    y = {'initial': '0', 'near-initial': '1e-10', 'after-initial': '2e-8'}.get(kind, '1')
    tangent = ['1', '0', '0'] if kind == 'ordinary' else ['-1', '1', '1e-14' if kind == 'phase-small' else '0']
    field = numeric.augment(dict(constant=[1, -1, 0], linear=[], quadratic=[]))
    return dict(id=kind, initial=[str(D(v)) for v in ['-1', y, '0']+tangent], field=field,
                horizon='2', section=dict(offset='0', gate_upper='10'))


def control_identity(case, profile):
    with localcontext() as ctx:
        ctx.prec = 70
        events = profile['census']['events']
        t = D(case['initial'][1])
        accepted = t > D('1e-8')
        if not profile['census']['complete'] or len(events) != 1 or events[0]['accepted'] != accepted or abs(D(events[0]['time'])-t) > D('1e-23'):
            raise ValueError('analytic complete initial/event classification failed')
        expected = [D(case['initial'][3])+D(case['initial'][4]), D(0), D(case['initial'][5])]
        if len(profile['measures']) != int(accepted):
            raise ValueError('analytic accepted count failed')
        error = D(0)
        if accepted:
            m = profile['measures'][0]
            if not m['qualified']:
                raise ValueError('analytic event correction failed')
            error = max(abs(D(a)-b) for a, b in zip(m['corrected'], expected, strict=True))
            if error > D('1e-30'):
                raise ValueError('analytic cancellation identity failed')
        return dict(passed=True, corrected_absolute_error=str(error), expected_accepted=int(accepted))


def controls(p, output):
    from scripts import audit_exp515_third_return_precision as audit
    output.mkdir(parents=True, exist_ok=False)
    limits = dict(p['limits'], output_bytes=p['controls']['output_bytes'])
    count, start = 0, time.monotonic()
    def budget(integrating=False):
        nonlocal count
        if time.monotonic()-start > p['controls']['wall_seconds']:
            raise RuntimeError('analytic control time cap')
        if integrating:
            if count >= p['controls']['ivps']:
                raise RuntimeError('analytic control IVP cap')
            count += 1
    rows = []
    for kind in KINDS:
        c = control_case(kind)
        for config in p['configurations']:
            profile = produce(c, config, output, limits, budget)
            check = control_identity(c, profile)
            audit.profile(output, c, config, profile)
            rows.append(dict(kind=kind, profile=profile, identity=check))
    result = dict(passed=True, control_ivps=count, rows=rows, files=inventory(output))
    write(output, output/'controls.json', result, limits)
    return result


def execute(output, source, remote):
    p = load()
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
    if git('rev-parse', 'HEAD') != source or git('status', '--porcelain') or git('ls-remote', 'origin', remote).split() != [source, remote]:
        raise ValueError('clean exact live-pushed source required')
    validate()
    root = ROOT/'artifacts/EXP-515'
    marker = root/'target-once.json'
    output = output.resolve()
    if root not in output.parents or output.exists() or marker.exists() or shutil.disk_usage(ROOT).free < p['limits']['initial_free_bytes']:
        raise ValueError('fresh attempt/output and disk reserve required')
    isolated = startup(p)
    control_result = controls(p, root/('execution-controls-'+source[:7]))
    free = shutil.disk_usage(ROOT).free
    if free < p['limits']['initial_free_bytes']:
        raise ValueError('free-space reserve after controls')
    output.mkdir(parents=True)
    binding = dict(source_commit=source, remote_ref=remote, started_utc=utc(),
        plan_sha256=sha256(PLAN), inputs=INPUTS, sources={n: sha256(ROOT/n) for n in SOURCES},
        initial_free_bytes=free, runtime=dict(python=sys.version), paid_review=p['paid_review'])
    start, count, progress = time.monotonic(), 0, []
    def save(name, value, reserve=True):
        write(output, output/name, value, p['limits'], reserve)
    def budget(integrating=False):
        nonlocal count
        if time.monotonic()-start > p['limits']['wall_seconds'] or shutil.disk_usage(ROOT).free < p['limits']['minimum_free_bytes']:
            raise RuntimeError('EXP-515 wall/free-space cap')
        if integrating:
            if count >= p['limits']['target_ivps']:
                raise RuntimeError('EXP-515 IVP cap')
            count += 1
    def timeout(*_):
        raise TimeoutError('EXP-515 wall deadline')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        save('binding.json', binding)
        save('startup.json', isolated)
        save('controls.json', control_result)
        write_bounded_json(root, marker, binding, limit_bytes=directory_bytes(root)+1024**2,
                           minimum_free_bytes=p['limits']['minimum_free_bytes'])
        rows = []
        for case in p['cases']:
            profiles = []
            for config in p['configurations']:
                progress.append(dict(id=case['id'], configuration=config['name'], status='started'))
                profiles.append(produce(case, config, output, p['limits'], budget))
                progress[-1]['status'] = 'completed'
                print(json.dumps(dict(completed_profiles=count, planned_profiles=12)), flush=True)
            row = dict(id=case['id'], profiles=profiles, comparison=model.compare(profiles, case['historical']))
            rows.append(row)
            save(case['id']+'.json', row)
        budget()
        save('summary.json', dict(experiment_id='EXP-515', status='completed', binding=binding,
            rows=rows, target_ivps=count, progress=progress, elapsed_seconds=time.monotonic()-start,
            completed_utc=utc(), marker_sha256=sha256(marker), files=inventory(output),
            symbolic_chains_verified=False, historical_decisions_changed=False))
        print(json.dumps(dict(completed=True, target_ivps=count, summary_sha256=sha256(output/'summary.json'))), flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json', dict(error_type=type(exc).__name__, message=str(exc), target_ivps=count,
            utc=utc(), progress=progress, files=inventory(output)), False)
        raise
    finally:
        signal.alarm(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    for name in ('prepare', 'startup', 'controls', 'execute'):
        modes.add_argument('--'+name, action='store_true')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--source-commit')
    parser.add_argument('--remote-ref')
    a = parser.parse_args()
    if a.prepare:
        write_bounded_json(PLAN.parent, PLAN, expected(), limit_bytes=directory_bytes(PLAN.parent)+2*1024**2)
    elif a.execute:
        if not all((a.output_dir, a.source_commit, a.remote_ref)):
            parser.error('output, source and remote required')
        execute(a.output_dir, a.source_commit, a.remote_ref)
    elif a.controls:
        if a.output_dir is None:
            parser.error('fresh control output required')
        r = controls(load(), a.output_dir)
        print(json.dumps(dict(passed=r['passed'], control_ivps=r['control_ivps'])))
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__ == '__main__':
    main()

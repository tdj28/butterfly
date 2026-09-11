#!/usr/bin/env python3
"""Read-only byte preservation check for EXP-523's timeout; no numerical replay."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

TASK = Path('/home/ubuntu/butterfly-research/exp523-refreshed-eae6745d124c')
PLAN = 'experiments/manifests/EXP-523-refreshed-contact-path.json'
COMMIT = 'eae6745d124c2fa59efc4eff337929e9ff71607d'
EXPECTED = {
    'failure.json': '3816d1351a8efc5c2fa2610118fbab1fe40989acfb7c993850be4b7b750c5116',
    'binding.json': 'e743e50def0e93eceec532de7553c1c1083f1868500b20c615bf4a9711d662e7',
    'target-once.json': 'e743e50def0e93eceec532de7553c1c1083f1868500b20c615bf4a9711d662e7',
    'operational.log': '76d2f6f8e9105daeca39865370ad8966f6afa3d75a50dedfcd4cd812cfc39e5b',
    'plan': 'e4c5b399f77dc8a23d069419866ff4a9787c9c7970b1e5336d6a19e3510ce4aa',
}


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            value.update(block)
    return value.hexdigest()


def safe_file(root, name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or str(p) != name:
        raise ValueError('canonical relative path required')
    path = root
    if path.is_symlink() or not path.is_dir():
        raise ValueError('non-symlink directory required')
    for part in p.parts:
        path = path/part
        if path.is_symlink():
            raise ValueError('symlinks forbidden')
    if not path.is_file():
        raise ValueError('retained file missing')
    return path


def verify_inventory(root, ledger, *, omit=()):
    actual = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('symlinks forbidden')
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    if actual-set(omit) != set(ledger):
        raise ValueError('complete retained inventory differs')
    total = 0
    for name, item in ledger.items():
        path = safe_file(root, name)
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError('retained bytes differ: '+name)
        total += item['bytes']
    return dict(files=len(ledger), bytes=total)


def inspect():
    source = TASK/'source'; parent = source/'artifacts/EXP-523'
    run = parent/'target-eae6745d124c'
    paths = {name: run/name for name in ('failure.json', 'binding.json')}
    paths.update({'target-once.json': parent/'target-once.json',
                  'operational.log': TASK/'operational.log', 'plan': source/PLAN})
    for name, path in paths.items():
        safe_file(TASK, path.relative_to(TASK).as_posix())
        if path.stat().st_size > 1024**2 or digest(path) != EXPECTED[name]:
            raise ValueError('authenticated diagnostic differs: '+name)
    failure = json.loads(paths['failure.json'].read_bytes())
    binding = json.loads(paths['binding.json'].read_bytes())
    plan = json.loads(paths['plan'].read_bytes())
    if (binding['source_commit'] != COMMIT or binding['plan_sha256'] != EXPECTED['plan']
            or binding['experiment_id'] != 'EXP-523'
            or set(binding['sources']) != set(plan['source_paths'])
            or binding['inputs'] != plan['inputs']):
        raise ValueError('source/plan/input binding differs')
    physical = dict(binding['sources'])
    for ledger in (plan['inputs'], plan['ancillary_inputs']):
        for name, value in ledger.items():
            if name in physical and physical[name] != value:
                raise ValueError('inconsistent source/input identity')
            physical[name] = value
    for name, value in physical.items():
        if digest(safe_file(source, name)) != value:
            raise ValueError('frozen physical file differs: '+name)
    if (run/'summary.json').exists() or (parent/'primary-audit-01.json').exists():
        raise ValueError('expected incomplete, unaudited attempt')
    retained = verify_inventory(run, failure['files'], omit=('failure.json',))
    elapsed = (datetime.fromisoformat(failure['utc'])-
               datetime.fromisoformat(binding['started_utc'])).total_seconds()
    return dict(experiment_id='EXP-523', status='timeout-bytes-preserved-not-scientifically-audited',
        observed_utc=datetime.now(timezone.utc).isoformat(), source_commit=COMMIT,
        diagnostic_sha256=EXPECTED, frozen_physical_files_verified=len(physical),
        retained_inventory=retained, failure_receipt_bytes=paths['failure.json'].stat().st_size,
        total_run_bytes=retained['bytes']+paths['failure.json'].stat().st_size,
        started_utc=binding['started_utc'], failure_utc=failure['utc'], elapsed_seconds=elapsed,
        error_type=failure['error_type'], message=failure['message'], point_progress=failure['point_progress'],
        target_ivp_calls_started=failure['target_ivps'], periodic_census_segments=failure['segments'],
        complete_run_summary=False, complete_raw_audit=False, new_integrations=0,
        symbolic_chains_verified=False,
        scope='Byte inventory, fixed source and failure diagnostics only; no scientific outputs interpreted or replayed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--remote', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.remote:
        if args.output is not None: parser.error('remote phase is read-only')
        print(json.dumps(inspect(), sort_keys=True, indent=2, allow_nan=False))
    else:
        if args.output is None or args.output.exists() or not args.output.parent.is_dir():
            parser.error('fresh local output with existing parent required')
        code = Path(__file__).read_bytes()
        result = subprocess.run(['ssh', 'ubuntu@prax', 'python3', '-', '--remote'],
            input=code, capture_output=True, check=True, timeout=600)
        if len(result.stdout) > 16384: raise ValueError('diagnostic receipt cap')
        receipt = json.loads(result.stdout)
        receipt['inspector_sha256'] = hashlib.sha256(code).hexdigest()
        data = (json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
        if len(data) > 16384: raise ValueError('diagnostic receipt cap')
        with args.output.open('xb') as stream: stream.write(data)
        print(json.dumps(dict(receipt=str(args.output), sha256=digest(args.output))))

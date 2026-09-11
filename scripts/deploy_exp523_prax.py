#!/usr/bin/env python3
"""Fetch only public frozen source on the existing prax host; never upload raw data."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile

HOST = 'ubuntu@prax'
URL = 'https://github.com/tdj28/butterfly.git'
REF = 'refs/heads/codex/exp523-prax-execution'
BASE = Path('/home/ubuntu/butterfly-research')


def checked_commit(value):
    if not re.fullmatch('[0-9a-f]{40}', value): raise ValueError('exact full commit required')
    return value


def closure(root, plan):
    names = sorted(set(plan['source_paths']) | set(plan['inputs']) | set(plan['ancillary_inputs']))
    for name in names:
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\n' in name or any(x in name for x in '*?[]!'):
            raise ValueError('exact safe public sparse path required')
        if not (root/name).is_file() or (root/name).is_symlink(): raise ValueError('physical source closure incomplete')
    return {n: hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}


def bootstrap_code(commit, hashes, launch):
    """Metadata only crosses SSH. Public source blobs are fetched from GitHub."""
    checked_commit(commit)
    payload = dict(commit=commit, hashes=hashes, launch=launch)
    return '''import hashlib,json,os,pathlib,shutil,subprocess,sys
p = json.loads(PAYLOAD)
base = pathlib.Path('/home/ubuntu/butterfly-research')
task = base/('exp523-refreshed-'+p['commit'][:12]); tree = task/'source'
def call(args, **kw): return subprocess.run(args, check=True, **kw)
def out(args): return subprocess.check_output(args, cwd=tree, text=True).strip()
if not p['launch']:
    if task.exists(): raise RuntimeError('fresh preparation namespace required; preserve previous attempt')
    if shutil.disk_usage(base).free < 21*1024**3: raise RuntimeError('preparation disk reserve')
    task.mkdir(mode=0o700)
    call(['git','clone','--depth','1','--filter=blob:none','--no-checkout','--single-branch',
        '--branch','codex/exp523-prax-execution','https://github.com/tdj28/butterfly.git',str(tree)])
    call(['git','sparse-checkout','init','--no-cone'],cwd=tree)
    call(['git','sparse-checkout','set','--no-cone','--stdin'],cwd=tree,
        input=''.join('/'+n+'\\n' for n in p['hashes']),text=True)
    call(['git','checkout','--detach',p['commit']],cwd=tree)
if out(['git','rev-parse','HEAD']) != p['commit'] or out(['git','status','--porcelain']):
    raise RuntimeError('clean exact checkout required')
if out(['git','ls-remote','origin','refs/heads/codex/exp523-prax-execution']).split() != [p['commit'],'refs/heads/codex/exp523-prax-execution']:
    raise RuntimeError('live immutable source ref differs')
for n,h in p['hashes'].items():
    path = tree/n
    if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=h:
        raise RuntimeError('physically deployed source differs: '+n)
env = dict(os.environ, UV_MANAGED_PYTHON='true', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
if not p['launch']:
    call(['/home/ubuntu/.local/bin/uv','sync','--locked','--no-install-project','--python','3.13'],cwd=tree,env=env)
    code = 'import sys;sys.path[:0]=[".","python"];from scripts.run_exp523_refreshed_path import startup,load;import json;print(json.dumps(startup(load())))'
    receipt = subprocess.check_output([str(tree/'.venv/bin/python'),'-I','-B','-c',code],cwd=tree,env=env,text=True)
    with (task/'startup.json').open('x') as stream: stream.write(receipt)
    with (task/'preparation.json').open('x') as stream: json.dump(dict(commit=p['commit'],sources=p['hashes'],free_bytes=shutil.disk_usage(tree).free),stream,indent=2)
    print(json.dumps(dict(prepared=True,task=str(task),sources=len(p['hashes']),free_bytes=shutil.disk_usage(tree).free)))
else:
    if not (task/'preparation.json').is_file(): raise RuntimeError('sealed preparation required')
    if json.loads((task/'preparation.json').read_text())['sources'] != p['hashes']: raise RuntimeError('preparation closure differs')
    if (tree/'artifacts/EXP-523/target-once.json').exists(): raise RuntimeError('consumed attempt cannot be launched again')
    log = (task/'operational.log').open('xb')
    code = 'import sys;sys.path[:0]=[".","python"];from scripts.deploy_exp523_prax import worker;worker('+repr(p['commit'])+')'
    child = subprocess.Popen([str(tree/'.venv/bin/python'),'-I','-B','-c',code],cwd=tree,env=env,
        stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    with (task/'launch.json').open('x') as stream: json.dump(dict(pid=child.pid,commit=p['commit']),stream)
    print(json.dumps(dict(launched=True,pid=child.pid,task=str(task))))
'''.replace('PAYLOAD', repr(json.dumps(payload, sort_keys=True)))


def worker(commit):
    """Same frozen process executes then audits; operational log omits outcomes."""
    from scripts import run_exp523_refreshed_path as run
    from scripts import audit_exp523_refreshed_path as audit
    from butterfly.bounded_json import directory_bytes, write_bounded_json
    checked_commit(commit)
    if sys.version_info[:2] != (3, 13) or '/uv/python/' not in sys.base_prefix:
        raise ValueError('managed CPython 3.13 required')
    output = run.ROOT/'artifacts/EXP-523'/('target-'+commit[:12])
    run.execute(output, commit, REF)
    def deadline(*_): raise TimeoutError('EXP-523 complete raw-audit six-hour deadline')
    previous = signal.signal(signal.SIGALRM, deadline)
    signal.alarm(21600)
    try:
        result = audit.audit(output, run.sha256(output/'summary.json'))
        receipt = output.parent/'primary-audit-01.json'
        write_bounded_json(receipt.parent, receipt, result, limit_bytes=directory_bytes(receipt.parent)+128*1024**2,
            minimum_free_bytes=8*1024**3)
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM, previous)
    print(json.dumps(dict(raw_audit_passed=True, receipt_sha256=run.sha256(receipt))), flush=True)


def rehearse(root, commit, hashes):
    """Materialize the identical sparse closure locally before remote preparation."""
    checked_commit(commit)
    task = Path(tempfile.mkdtemp(prefix='exp523-sparse-rehearsal-')).resolve()
    tree = task/'source'
    subprocess.run(['git', 'clone', '--no-checkout', '--shared', str(root), str(tree)], check=True)
    subprocess.run(['git', 'sparse-checkout', 'init', '--no-cone'], cwd=tree, check=True)
    subprocess.run(['git', 'sparse-checkout', 'set', '--no-cone', '--stdin'], cwd=tree,
        input=''.join('/'+n+'\n' for n in hashes), text=True, check=True)
    subprocess.run(['git', 'checkout', '--detach', commit], cwd=tree, check=True)
    for name, digest in hashes.items():
        path = tree/name
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('rehearsed physical source closure differs: '+name)
    code = ('import sys;sys.path[:0]=[".","python"];'
        'from scripts.run_exp523_refreshed_path import startup,load;import json;print(json.dumps(startup(load())))')
    completed = subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=tree,
        check=True, capture_output=True, text=True, timeout=120)
    receipt = dict(passed=True, source_commit=commit, sources=hashes, startup=json.loads(completed.stdout))
    # Only remove this successfully verified, task-created temporary rehearsal.
    shutil.rmtree(task)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--launch', action='store_true')
    parser.add_argument('--rehearse', action='store_true')
    args = parser.parse_args(); checked_commit(args.commit)
    root = Path(__file__).resolve().parents[1]
    plan = json.loads((root/'experiments/manifests/EXP-523-refreshed-contact-path.json').read_bytes())
    hashes = closure(root, plan)
    if args.rehearse:
        if args.launch: parser.error('rehearsal cannot launch')
        print(json.dumps(rehearse(root, args.commit, hashes))); return
    code = bootstrap_code(args.commit, hashes, args.launch)
    subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15',HOST,
        shlex.join(['python3','-c',code])], check=True)


if __name__ == '__main__': main()

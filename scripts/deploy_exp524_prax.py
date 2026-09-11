#!/usr/bin/env python3
"""Deploy public audit source separately; read existing prax evidence in place."""
import argparse
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
from scripts import deploy_exp523_prax as previous


def bootstrap_code(commit, hashes, launch):
    previous.checked_commit(commit)
    payload = json.dumps(dict(commit=commit, hashes=hashes, launch=launch), sort_keys=True)
    return '''import hashlib,json,os,pathlib,shutil,subprocess,sys
p=json.loads(PAYLOAD)
base=pathlib.Path('/home/ubuntu/butterfly-research')
task=base/('exp524-partial-audit-'+p['commit'][:12]); tree=task/'source'
python=base/'exp523-refreshed-eae6745d124c/source/.venv/bin/python'
ref='refs/heads/codex/exp524-prax-execution'
def call(args,**kw): return subprocess.run(args,check=True,**kw)
def out(args): return subprocess.check_output(args,cwd=tree,text=True).strip()
if not p['launch']:
    if task.exists(): raise RuntimeError('fresh recovery preparation namespace required')
    if shutil.disk_usage(base).free<9*1024**3: raise RuntimeError('preparation reserve')
    task.mkdir(mode=0o700)
    call(['git','clone','--depth','1','--filter=blob:none','--no-checkout','--single-branch',
        '--branch','codex/exp524-prax-execution','https://github.com/tdj28/butterfly.git',str(tree)])
    call(['git','sparse-checkout','init','--no-cone'],cwd=tree)
    call(['git','sparse-checkout','set','--no-cone','--stdin'],cwd=tree,
        input=''.join('/'+n+'\\n' for n in p['hashes']),text=True)
    call(['git','checkout','--detach',p['commit']],cwd=tree)
if out(['git','rev-parse','HEAD'])!=p['commit'] or out(['git','status','--porcelain']):
    raise RuntimeError('clean exact audit checkout required')
if out(['git','ls-remote','origin',ref]).split()!=[p['commit'],ref]:
    raise RuntimeError('live audit freeze differs')
for n,h in p['hashes'].items():
    path=tree/n
    if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=h:
        raise RuntimeError('physical audit source differs: '+n)
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
code='import sys;sys.path[:0]=[".","python"];from scripts import audit_exp524_partial_calibration as a;'
probe=code+'import json;print(json.dumps(a.preflight('+repr(p['commit'])+')))'
receipt=subprocess.check_output([str(python),'-I','-B','-c',probe],cwd=tree,env=env,text=True)
if not p['launch']:
    with (task/'preflight.json').open('x') as f: f.write(receipt)
    with (task/'preparation.json').open('x') as f: json.dump(p,f,sort_keys=True)
    print(json.dumps(dict(prepared=True,task=str(task),sources=len(p['hashes']),free_bytes=shutil.disk_usage(tree).free)))
else:
    old=json.loads((task/'preparation.json').read_bytes())
    if old['commit']!=p['commit'] or old['hashes']!=p['hashes']: raise RuntimeError('prepared closure differs')
    if (tree/'artifacts/EXP-524/audit-once.json').exists() or (task/'launch.json').exists():
        raise RuntimeError('recovery attempt already consumed or launched')
    with (task/'launch-preflight.json').open('x') as f: f.write(receipt)
    log=(task/'operational.log').open('xb')
    child=subprocess.Popen([str(python),'-I','-B','-c',code+'a.execute('+repr(p['commit'])+')'],
        cwd=tree,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    identity=dict(pid=child.pid,commit=p['commit'],argv=child.args)
    identity['proc_start_ticks']=pathlib.Path('/proc/'+str(child.pid)+'/stat').read_text().split()[21]
    with (task/'launch.json').open('x') as f: json.dump(identity,f)
    print(json.dumps(dict(launched=True,task=str(task),**identity)))
'''.replace('PAYLOAD', repr(payload))


def rehearsal(root, hashes):
    """Outcome-free isolated startup from the exact physical deploy allowlist."""
    tree = Path(tempfile.mkdtemp(prefix='exp524-sealed-startup-')).resolve()
    for n, h in hashes.items():
        dest = tree/n; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root/n, dest)
        if previous.hashlib.sha256(dest.read_bytes()).hexdigest() != h:
            raise ValueError('sealed source copy differs')
    code = ('import sys;from pathlib import Path;sys.path[:0]=[".","python"];'
        'from scripts import audit_exp524_partial_calibration as a;import json;print(json.dumps(a.validate()));'
        'assert all(Path(m.__file__).resolve().is_relative_to(Path.cwd()) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=tree, text=True,
                           capture_output=True, check=True, timeout=120)
    if list(tree.rglob('*.pyc')):
        raise ValueError('sealed rehearsal wrote bytecode')
    receipt = dict(passed=True, sources=hashes, validation=json.loads(child.stdout))
    shutil.rmtree(tree)  # Only the successfully verified temporary copy above.
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--launch', action='store_true')
    mode.add_argument('--rehearse', action='store_true')
    args = parser.parse_args(); previous.checked_commit(args.commit)
    root = Path(__file__).resolve().parents[1]
    plan = json.loads((root/'experiments/manifests/EXP-524-partial-calibration-audit.json').read_bytes())
    hashes = previous.closure(root, dict(source_paths=plan['source_paths'], inputs={}, ancillary_inputs={}))
    if args.rehearse:
        print(json.dumps(rehearsal(root, hashes))); return
    code = bootstrap_code(args.commit, hashes, args.launch)
    subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15', 'ubuntu@prax',
                    shlex.join(['python3', '-c', code])], check=True)


if __name__ == '__main__':
    main()

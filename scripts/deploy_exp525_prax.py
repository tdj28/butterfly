#!/usr/bin/env python3
"""Public-source deployment; private calibration already resides on prax."""
import argparse
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
from scripts import deploy_exp524_prax as previous


def bootstrap_code(commit,hashes,launch):
    code=previous.bootstrap_code(commit,hashes,launch)
    substitutions={
        'exp524-partial-audit-':'exp525-recovered-step-',
        'codex/exp524-prax-execution':'codex/exp525-prax-execution',
        'from scripts import audit_exp524_partial_calibration as a;':'from scripts import run_exp525_recovered_step as a;',
        'artifacts/EXP-524/audit-once.json':'artifacts/EXP-525/target-once.json',
        '9*1024**3':'12*1024**3',
    }
    for old,new in substitutions.items():
        expected_count=2 if old=='codex/exp524-prax-execution' else 1
        if code.count(old)!=expected_count: raise ValueError('exact parent deployment seam changed: '+old)
        code=code.replace(old,new)
    return code


def rehearsal(root,hashes,calibration=None):
    tree=Path(tempfile.mkdtemp(prefix='exp525-sealed-startup-')).resolve()
    for name,digest in hashes.items():
        target=tree/name; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(root/name,target)
        if previous.previous.hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
            raise ValueError('sealed physical source differs')
    arg='None' if calibration is None else 'Path('+repr(str(Path(calibration).resolve()))+')'
    code=('import sys;from pathlib import Path;sys.path[:0]=[".","python"];'
        'from scripts import run_exp525_recovered_step as run;import json;'
        'print(json.dumps(run.validate('+arg+')));'
        'assert all(Path(m.__file__).resolve().is_relative_to(Path.cwd()) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=tree,capture_output=True,text=True,check=True,timeout=120)
    if list(tree.rglob('*.pyc')): raise ValueError('sealed startup wrote bytecode')
    receipt=dict(passed=True,sources=hashes,validation=json.loads(child.stdout))
    shutil.rmtree(tree)
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit',required=True); parser.add_argument('--calibration',type=Path)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--launch',action='store_true'); mode.add_argument('--rehearse',action='store_true')
    args=parser.parse_args(); previous.previous.checked_commit(args.commit)
    root=Path(__file__).resolve().parents[1]
    plan=json.loads((root/'experiments/manifests/EXP-525-recovered-single-step.json').read_bytes())
    hashes=previous.previous.closure(root,dict(source_paths=plan['source_paths'],inputs={},ancillary_inputs={}))
    if args.rehearse: print(json.dumps(rehearsal(root,hashes,args.calibration))); return
    if args.calibration is not None: parser.error('calibration is local rehearsal only; remote input is fixed and never uploaded')
    subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','ubuntu@prax',
        shlex.join(['python3','-c',bootstrap_code(args.commit,hashes,args.launch)])],check=True)


if __name__=='__main__': main()

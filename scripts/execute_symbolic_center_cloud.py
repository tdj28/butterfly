#!/usr/bin/env python3
"""Frozen EXP-477 source staging, authenticated SSH, raw collection and retrieval.

Preparation-only is the default; only explicit --execute can provision. The separate owned-worker lifecycle
controller creates at most one worker and enforces its durable local watchdog.
Only committed allowlisted source and two hash-bound scientific inputs transfer.
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import re
import select
import shlex
import shutil
import subprocess
import tarfile
import time

from scripts import runpod_symbolic_worker as worker
from scripts import run_symbolic_center_pilot as pilot
from scripts import qualify_symbolic_gpu_records as qualification
from scripts.check_public_repository import check_file
from scripts import symbolic_ssh_storage as ssh_storage


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_MANIFEST = "experiments/manifests/EXP-477-cloud-runtime.json"
PILOT_MANIFEST = "experiments/manifests/EXP-477-symbolic-center-pilot.json"
SOURCE_PATHS = ("scripts", "python", "experiments/manifests", "experiments/source-transcriptions",
                "docs/experiments/receipts", "pyproject.toml", "uv.lock", "README.md", "LICENSE")
STAGE_SECONDS = {"connect": 600, "setup": 900, "qualification": 900, "collection": 3900, "retrieval": 1200}
IMAGE = "runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04"
ASSET = re.compile(r"(?:gpu-control\.json|logs/(?:setup|qualification|collection)\.log|"
                   r"environment/(?:python\.txt|pip-freeze\.txt|nvidia-smi\.txt|torch\.json|storage\.json)|"
                   r"status/[a-z0-9-]+\.json|collection/(?:started|receipt)\.json|"
                   r"collection/batch-[0-9]{4}-profile-[01](?:-checkpoint)?\.(?:json|npz))\Z")


class DeploymentError(RuntimeError):
    pass


def safe_name(name):
    path = PurePosixPath(name)
    return bool(name and not path.is_absolute() and ".." not in path.parts and "." not in path.parts
                and "\\" not in name and str(path) == name)


def source_allowed(name, *, directory=False):
    if not safe_name(name) or any(part.startswith(".") or part in {"__pycache__", "node_modules"}
                                 for part in PurePosixPath(name).parts):
        return False
    if directory:
        return any(name == prefix or name.startswith(prefix + "/") or prefix.startswith(name + "/")
                   for prefix in SOURCE_PATHS[:5])
    if name in SOURCE_PATHS[5:]:
        return True
    return any(name.startswith(prefix + "/") and name.endswith(suffix)
               for prefix, suffix in zip(SOURCE_PATHS[:5], (".py", ".py", ".json", ".json", ".json"), strict=True))


def archive_byte_limit(limits):
    # Asset padding/headers, a <=1 MiB inventory, and tar end blocks.
    return limits["maximum_total_bytes"] + limits["maximum_files"] * 2048 + 2 * 1048576


def require_free_space(output_dir, limits):
    path = Path(output_dir).absolute()
    while not path.exists():
        path = path.parent
    required = archive_byte_limit(limits) + limits["maximum_total_bytes"] + 512 * 1048576
    available = shutil.disk_usage(path).free
    if available < required:
        raise DeploymentError(f"local retrieval storage insufficient: {available} available bytes; {required} required")
    return {"available_bytes": available, "required_bytes": required}


def require_local_control_space(output_dir):
    path = Path(output_dir).absolute()
    while not path.exists():
        path = path.parent
    available = shutil.disk_usage(path).free
    if available < ssh_storage.MINIMUM_LOCAL_FREE_BYTES:
        raise DeploymentError("local controller/staging storage requires at least 2 GiB free")
    return {"available_bytes": available, "required_bytes": ssh_storage.MINIMUM_LOCAL_FREE_BYTES,
            "bulk_evidence_destination": "authenticated SSH; no bulk Mac archive"}


def describe(path):
    path = Path(path)
    return {"path": path.name, "sha256": pilot.sha256_file(path), "bytes": path.stat().st_size}


def runtime_plan(commit, *, root=ROOT):
    path = Path(root) / RUNTIME_MANIFEST
    content = path.read_bytes()
    value = json.loads(content)
    if value.get("schema") != "butterfly.symbolic-cloud-runtime.v1" or value.get("experiment_id") != "EXP-477":
        raise DeploymentError("unsupported cloud runtime plan")
    if tuple(value["source_archive_paths"]) != SOURCE_PATHS or value["stage_seconds"] != STAGE_SECONDS:
        raise DeploymentError("source allowlist or stage limits differ from this frozen executor")
    runtime = value["runtime"]
    if runtime != {"uv": "0.9.21", "python_minor": "3.13", "torch": "2.8.0",
                   "torch_index_url": "https://download.pytorch.org/whl/cu128", "cuda_overlay_is_not_in_uv_lock": True}:
        raise DeploymentError("runtime installation pins differ from this frozen executor")
    plan = {**value["lifecycle"], "experiment_id": "EXP-477", "source_commit": commit}
    if plan["gpu_type"] != "NVIDIA A40" or plan["image"] != IMAGE:
        raise DeploymentError("only the frozen A40/image combination is allowed")
    worker.validate_plan(plan)
    if value["retrieval"] != {"maximum_total_bytes": 8589934592, "maximum_files": 2000}:
        raise DeploymentError("retrieval bounds differ from this frozen executor")
    if value.get("minimum_worker_free_bytes") != 9663676416:
        raise DeploymentError("worker disk gate differs from this frozen executor")
    pilot.source_binding(Path(root), commit, path, content)
    return value, plan


def build_source_archive(root, commit, archive_path):
    """Use Git objects only; reject links and any unexpected source member."""
    subprocess.run(["git", "archive", "--format=tar", "--output", str(archive_path), commit, "--", *SOURCE_PATHS],
                   cwd=root, check=True, timeout=60, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    files = {}
    with tarfile.open(archive_path, "r:") as archive:
        for member in archive:
            name = member.name.rstrip("/")
            if not source_allowed(name, directory=member.isdir()) or member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise DeploymentError(f"unsafe source archive member: {name}")
            if member.isfile():
                if name in files:
                    raise DeploymentError("duplicate source archive member")
                with archive.extractfile(member) as stream:
                    content = stream.read()
                if check_file(name, content):
                    raise DeploymentError(f"source archive failed credential scan: {name}; contents suppressed")
                files[name] = hashlib.sha256(content).hexdigest()
    required = {PILOT_MANIFEST, RUNTIME_MANIFEST, "scripts/execute_symbolic_center_cloud.py",
                "scripts/run_symbolic_center_pilot.py", "scripts/qualify_symbolic_gpu_records.py",
                "scripts/symbolic_ssh_storage.py", "pyproject.toml", "uv.lock"}
    if not required <= files.keys():
        raise DeploymentError("source archive lacks required runtime closure")
    return {"schema": "butterfly.source-inventory.v1", "source_commit": commit, "pushed_source_commit": commit,
            "source_archive_sha256": pilot.sha256_file(archive_path), "files": files}


def prepare_inputs(commit, cpu_control, cpu_sha256, output_dir, state_dir, *, root=ROOT, ssh_storage_dir=None):
    root, output_dir, state_dir = Path(root).resolve(), Path(output_dir).absolute(), Path(state_dir).absolute()
    if output_dir.exists() or output_dir.is_symlink() or state_dir.exists() or state_dir.is_symlink():
        raise DeploymentError("output and private state directories must both be new")
    runtime, plan = runtime_plan(commit, root=root)
    if ssh_storage_dir is not None:
        ssh_storage.validate_directory(ssh_storage_dir)
        expected_remote = {"host": ssh_storage.HOST, "base_directory": ssh_storage.BASE_DIRECTORY,
                           "minimum_local_free_bytes": ssh_storage.MINIMUM_LOCAL_FREE_BYTES,
                           "minimum_remote_free_bytes": ssh_storage.MINIMUM_REMOTE_FREE_BYTES,
                           "maximum_cached_asset_bytes": ssh_storage.MAXIMUM_CACHED_ASSET_BYTES,
                           "maximum_control_bytes": ssh_storage.MAXIMUM_CONTROL_BYTES}
        if runtime.get("remote_evidence") != expected_remote:
            raise DeploymentError("SSH evidence storage differs from frozen runtime declaration")
        storage = require_local_control_space(output_dir)
    else:
        storage = require_free_space(output_dir, runtime["retrieval"])
    prepared = pilot.prepare(root / PILOT_MANIFEST, commit, root=root)
    cpu_content = Path(cpu_control).read_bytes()
    if not re.fullmatch(r"[0-9a-f]{64}", cpu_sha256) or hashlib.sha256(cpu_content).hexdigest() != cpu_sha256:
        raise DeploymentError("CPU control hash mismatch")
    cpu = json.loads(cpu_content)
    if (cpu.get("schema") != "butterfly.symbolic-gpu-deployment-control.v1" or cpu.get("mode") != "cpu"
            or cpu.get("passed") is not True or cpu.get("source", {}).get("commit") != commit
            or cpu.get("parent_sha256") != qualification.PARENT_HASH
            or cpu.get("qualification_script_sha256") != pilot.sha256_file(root / "scripts/qualify_symbolic_gpu_records.py")
            or cpu.get("state_atol") != qualification.STATE_ATOL or cpu.get("time_atol") != qualification.TIME_ATOL):
        raise DeploymentError("CPU control is not passing and exactly source/design bound")
    qualification.validate_control(cpu["control"], qualification.parent_design())
    candidate_path = root / prepared["manifest"]["candidate_input"]["path"]
    if candidate_path.stat().st_size != worker.CANDIDATE_BYTES or pilot.sha256_file(candidate_path) != worker.CANDIDATE_HASH:
        raise DeploymentError("complete 551-candidate payload hash/size mismatch")
    # New local evidence must not dirty the frozen source used by this run.
    for path in (output_dir, state_dir):
        if path.is_relative_to(root):
            checked = subprocess.run(["git", "check-ignore", "--quiet", str(path.relative_to(root)) + "/"], cwd=root, check=False)
            if checked.returncode != 0:
                raise DeploymentError("in-repository output/state directories must be ignored")
    output_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
    incoming = output_dir / "prepared-inputs"
    incoming.mkdir(mode=0o700)
    archive = incoming / "source.tar"
    inventory = build_source_archive(root, commit, archive)
    pilot.write_new_json(incoming / "source-inventory.json", inventory)
    with (incoming / "cpu-control.json").open("xb") as stream:
        stream.write(cpu_content)
    with (incoming / "candidates.json").open("xb") as stream:
        stream.write(candidate_path.read_bytes())
    assets = {path.name: describe(path) for path in sorted(incoming.iterdir())}
    value = {"schema": "butterfly.symbolic-cloud-preparation.v1", "source_commit": commit,
             "runtime": runtime, "plan": plan, "pilot_manifest_sha256": prepared["manifest_sha256"],
             "collection_binding": {"input_hashes": prepared["input_hashes"],
                                    "candidate_ids": [row["id"] for row in prepared["candidates"]],
                                    "profiles": prepared["parent"]["profiles"],
                                    "batch_size": prepared["manifest"]["execution"]["batch_size"]},
             "cpu_control_sha256": cpu_sha256, "assets": assets,
             "local_storage_preflight": storage,
             "ssh_storage_directory": ssh_storage_dir,
             "prepared_utc": pilot.utc_now(), "provider_calls_performed": False}
    pilot.write_new_json(output_dir / "preparation.json", value)
    return value


# This standard-library bootstrap is sent as a command, never written over source.
# It cannot read credentials, extract links, or include arbitrary paths in retrieval.
REMOTE_PROGRAM = r'''
import hashlib, io, json, os, pathlib, re, shutil, signal, subprocess, sys, tarfile, time
mode, base_text = sys.argv[1:3]
base = pathlib.Path(base_text)
roots = ('scripts','python','experiments/manifests','experiments/source-transcriptions','docs/experiments/receipts','pyproject.toml','uv.lock','README.md','LICENSE')
asset = re.compile(r'(?:gpu-control\.json|logs/(?:setup|qualification|collection)\.log|environment/(?:python\.txt|pip-freeze\.txt|nvidia-smi\.txt|torch\.json|storage\.json)|status/[a-z0-9-]+\.json|collection/(?:started|receipt)\.json|collection/batch-[0-9]{4}-profile-[01](?:-checkpoint)?\.(?:json|npz))\Z')
def safe(name):
 p=pathlib.PurePosixPath(name)
 return bool(name and not p.is_absolute() and '..' not in p.parts and '.' not in p.parts and '\\' not in name and str(p)==name)
def allowed_source(name,directory):
 if not safe(name) or any(p.startswith('.') or p in {'__pycache__','node_modules'} for p in pathlib.PurePosixPath(name).parts): return False
 if directory: return any(name==r or name.startswith(r+'/') or r.startswith(name+'/') for r in roots[:5])
 if name in roots[5:]: return True
 return any(name.startswith(r+'/') and name.endswith(s) for r,s in zip(roots[:5],('.py','.py','.json','.json','.json')))
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''): h.update(block)
 return h.hexdigest()
def new_json(path,value):
 with path.open('x') as f: json.dump(value,f,sort_keys=True)
def identity(pid):
 try:
  value=pathlib.Path('/proc')/str(pid)/'stat'; raw=value.read_text(); fields=raw[raw.rfind(')')+2:].split()
  return {'pid':pid,'pgid':int(fields[2]),'session':int(fields[3]),'start_ticks':fields[19],'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'state':fields[0]}
 except (OSError,ValueError,IndexError): return None
def same_process(record):
 current=identity(record['pid'])
 return current is not None and current['state']!='Z' and all(current[k]==record[k] for k in ('pid','pgid','session','start_ticks','boot_id'))
def process_group_members(record):
 if record['pgid']!=record['pid'] or record['session']!=record['pid']: raise RuntimeError('recorded child lacks dedicated session/group')
 if pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=record['boot_id']: raise RuntimeError('owned group boot identity changed')
 members=[]
 for path in pathlib.Path('/proc').iterdir():
  if not path.name.isdigit(): continue
  current=identity(int(path.name))
  if current is not None and current['state']!='Z' and current['pgid']==record['pgid']:
   if current['session']!=record['session'] or int(current['start_ticks'])<int(record['start_ticks']): raise RuntimeError('ambiguous process group identity')
   members.append(current)
 return members
def stop_owned(record,group=False):
 if not same_process(record):
  current=identity(record['pid'])
  if current is not None and current['state']!='Z': raise RuntimeError('owned process identity changed; refusing signal')
  if group and process_group_members(record): raise RuntimeError('owned group outlived identifiable leader; snapshot refused')
  return
 if group: process_group_members(record)
 for sig,seconds in ((signal.SIGTERM,8),(signal.SIGKILL,5)):
  if not same_process(record):
   if group and process_group_members(record): raise RuntimeError('owned group remains after leader exit; snapshot refused')
   return
  try: os.killpg(record['pid'],sig) if group else os.kill(record['pid'],sig)
  except ProcessLookupError: return
  end=time.monotonic()+seconds
  while time.monotonic()<end and (bool(process_group_members(record)) if group else same_process(record)): time.sleep(.05)
 if same_process(record) or (group and process_group_members(record)): raise RuntimeError('owned writer group failed to stop')
child_program="import json,os,pathlib,sys; p=pathlib.Path('/proc/self/stat'); raw=p.read_text(); f=raw[raw.rfind(')')+2:].split(); r={'pid':os.getpid(),'pgid':os.getpgrp(),'session':os.getsid(0),'start_ticks':f[19],'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'state':f[0]}; out=open(sys.argv[1],'x'); json.dump(r,out); out.flush(); os.fsync(out.fileno()); out.close(); argv=json.loads(sys.argv[2]); os.execvpe(argv[0],argv,os.environ)"
if mode=='init':
 base.mkdir(mode=0o700)
 for name in ('incoming','results','results/logs','results/environment','results/status'): (base/name).mkdir(mode=0o700)
elif mode=='extract':
 expected=json.loads(sys.argv[3])
 for name,row in expected.items():
  p=base/'incoming'/name
  if p.stat().st_size!=row['bytes'] or digest(p)!=row['sha256']: raise RuntimeError('staged hash/size mismatch')
 destination=base/'source'; destination.mkdir(mode=0o700)
 with tarfile.open(base/'incoming/source.tar','r:') as archive:
  seen=set()
  for member in archive:
   name=member.name.rstrip('/')
   if not allowed_source(name,member.isdir()) or not(member.isfile() or member.isdir()): raise RuntimeError('unsafe source member')
   p=destination/name
   if member.isdir(): p.mkdir(parents=True,exist_ok=True); continue
   if name in seen: raise RuntimeError('duplicate source member')
   seen.add(name); p.parent.mkdir(parents=True,exist_ok=True)
   with archive.extractfile(member) as src,p.open('xb') as out:
    for block in iter(lambda:src.read(1048576),b''): out.write(block)
   p.chmod(member.mode & 0o777)
 target=destination/'artifacts/EXP-204/candidates.json'; target.parent.mkdir(parents=True)
 with (base/'incoming/candidates.json').open('rb') as src,target.open('xb') as out: out.write(src.read())
 new_json(base/'results/status/staged.json',{'verified':True,'files':expected})
elif mode=='stage':
 spec=json.loads(sys.argv[3]); started=time.monotonic(); end=started+spec['seconds']; ok=True
 new_json(base/'results/status'/(spec['name']+'-supervisor.json'),identity(os.getpid()))
 def interrupted(signum,frame): raise KeyboardInterrupt('owned stage interrupted')
 signal.signal(signal.SIGTERM,interrupted); signal.signal(signal.SIGHUP,interrupted)
 env=dict(os.environ); env['PYTHONPATH']='.:python'; env.pop('SSH_AUTH_SOCK',None); env.pop('RUNPOD_API_KEY',None)
 with (base/'results/logs'/ (spec['name']+'.log')).open('xb') as log:
  for step in spec['steps']:
   stamp=time.monotonic(); stdout=log; owned=None; code=-1; failure=None; p=None
   try:
    if 'stdout' in step:
     if not asset.fullmatch(step['stdout']) or not step['stdout'].startswith('environment/'): raise RuntimeError('invalid environment output')
     owned=(base/'results'/step['stdout']).open('xb'); stdout=owned
    if stamp>=end: raise TimeoutError('stage deadline')
    child_path=base/'results/status'/(spec['name']+'-'+step['name']+'-child.json')
    new_json(base/'results/status'/(spec['name']+'-'+step['name']+'-launch.json'),{'child_file':child_path.name})
    p=subprocess.Popen([sys.executable,'-c',child_program,str(child_path),json.dumps(step['argv'])],cwd=base/'source',env=env,stdout=stdout,stderr=log,start_new_session=True)
    try: code=p.wait(timeout=max(0.001,end-time.monotonic()))
    except subprocess.TimeoutExpired:
     os.killpg(p.pid,signal.SIGTERM)
     try: p.wait(timeout=20)
     except subprocess.TimeoutExpired: os.killpg(p.pid,signal.SIGKILL); p.wait(timeout=5)
     raise TimeoutError('owned stage process group exceeded deadline')
   except BaseException as e: failure={'type':type(e).__name__,'message':str(e)}
   finally:
    if p is not None and p.poll() is None:
     record=identity(p.pid)
     if record is not None: stop_owned(record,True)
     p.wait(timeout=5)
    if owned: owned.close()
   new_json(base/'results/status'/(spec['name']+'-'+step['name']+'.json'),{'returncode':code,'elapsed_seconds':time.monotonic()-stamp,'failure':failure})
   if code!=0 or failure: ok=False; break
 new_json(base/'results/status'/(spec['name']+'.json'),{'passed':ok,'elapsed_seconds':time.monotonic()-started})
 sys.exit(0 if ok else 1)
elif mode=='quiesce':
 # Stop exact saved supervisors first, so they cannot launch another writer.
 for path in sorted((base/'results/status').glob('*-supervisor.json')): stop_owned(json.loads(path.read_text()))
 for path in sorted((base/'results/status').glob('*-launch.json')):
  name=json.loads(path.read_text())['child_file']
  if name!=path.name.replace('-launch.json','-child.json'): raise RuntimeError('owned child filename identity mismatch')
  child=base/'results/status'/name; end=time.monotonic()+5
  while not child.exists() and time.monotonic()<end: time.sleep(.05)
  if not child.exists():
   status=path.with_name(path.name.replace('-launch.json','.json'))
   if not status.exists(): raise RuntimeError('unresolved owned launch; no quiescent snapshot')
   continue
  stop_owned(json.loads(child.read_text()),True)
 for path in sorted((base/'results/status').glob('*-child.json')):
  if process_group_members(json.loads(path.read_text())): raise RuntimeError('owned writer group remains live')
 print(json.dumps({'quiescent':True}))
elif mode=='storage':
 required=json.loads(sys.argv[3])['minimum_worker_free_bytes']
 if required!=9663676416: raise RuntimeError('unexpected frozen worker space gate')
 usage=shutil.disk_usage(base/'results'); stat=os.statvfs(base/'results')
 result={'available_bytes':usage.free,'required_bytes':required,'free_inodes':stat.f_favail,'passed':usage.free>=required and stat.f_favail>=2001}
 new_json(base/'results/environment/storage.json',result)
 print(json.dumps(result))
 sys.exit(0 if result['passed'] else 1)
elif mode=='snapshot':
 rows=[]
 for pattern in ('status/*.json','collection/*-checkpoint.json','collection/started.json','collection/receipt.json','gpu-control.json'):
  for path in sorted((base/'results').glob(pattern)):
   if path.is_file() and not path.is_symlink(): rows.append([str(path.relative_to(base/'results')),path.stat().st_size,digest(path)])
 print(json.dumps(rows,sort_keys=True))
elif mode=='pack':
 limits=json.loads(sys.argv[3]); rows=[]; total=0
 for path in sorted((base/'results').rglob('*')):
  name=str(path.relative_to(base/'results'))
  if path.is_symlink(): raise RuntimeError('retrieval contains symlink')
  if path.is_dir(): continue
  if not path.is_file() or not safe(name) or not asset.fullmatch(name): raise RuntimeError('retrieval contains unexpected filename')
  size=path.stat().st_size; total+=size
  if total>limits['maximum_total_bytes'] or len(rows)>=limits['maximum_files']: raise RuntimeError('retrieval exceeds frozen bounds')
  rows.append({'path':name,'bytes':size,'sha256':digest(path)})
 raw=json.dumps({'schema':'butterfly.symbolic-remote-assets.v1','assets':rows},sort_keys=True).encode()
 with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as archive:
  info=tarfile.TarInfo('retrieval-manifest.json'); info.size=len(raw); info.mode=0o600; archive.addfile(info,io.BytesIO(raw))
  for row in rows:
   info=tarfile.TarInfo(row['path']); info.size=row['bytes']; info.mode=0o600
   with (base/'results'/row['path']).open('rb') as f: archive.addfile(info,f)
else: raise RuntimeError('unsupported bootstrap mode')
'''


def remote_command(mode, base, payload=None):
    values = ["python3", "-c", REMOTE_PROGRAM, mode, base]
    if payload is not None:
        values.append(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return shlex.join(values)


def endpoint(pod):
    host = str(ipaddress.ip_address(pod["publicIp"]))
    port = pod["portMappings"]["22"]
    if isinstance(port, str) and port.isdigit():
        port = int(port)
    if type(port) is not int or not 1 <= port <= 65535:
        raise DeploymentError("provider did not return a valid direct SSH port")
    return host, port


class SSH:
    def __init__(self, host, port, state_dir):
        self.host, self.port, self.state_dir = host, port, Path(state_dir)
        self.known_hosts = self.state_dir / "task-known-hosts"
        self.strict = self.known_hosts.exists() and self.known_hosts.stat().st_size > 0

    def options(self, *, scp=False):
        return ["-F", "/dev/null", "-i", str(self.state_dir / "task_ed25519"),
                "-o", "IdentitiesOnly=yes", "-o", "IdentityAgent=none", "-o", "ForwardAgent=no",
                "-o", "BatchMode=yes", "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no",
                "-o", "PreferredAuthentications=publickey", "-o", "GlobalKnownHostsFile=/dev/null",
                "-o", "UserKnownHostsFile=" + str(self.known_hosts),
                "-o", "StrictHostKeyChecking=" + ("yes" if self.strict else "accept-new"),
                "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=10", "-o", "ServerAliveCountMax=3",
                "-P" if scp else "-p", str(self.port)]

    def argv(self, command):
        return ["/usr/bin/ssh", *self.options(), "root@" + self.host, command]

    def call(self, command, *, timeout=30):
        try:
            return subprocess.run(self.argv(command), check=True, capture_output=True, timeout=timeout)
        finally:
            if self.known_hosts.exists() and self.known_hosts.stat().st_size:
                self.strict = True
                os.chmod(self.known_hosts, 0o600)

    def upload(self, path, remote_directory):
        if not self.strict:
            raise DeploymentError("uploads require an authenticated, pinned host-key session")
        host = "[" + self.host + "]" if ":" in self.host else self.host
        subprocess.run(["/usr/bin/scp", *self.options(scp=True), str(path),
                        "root@" + host + ":" + remote_directory + "/" + Path(path).name],
                       check=True, capture_output=True, timeout=180)

    def monitored(self, command, *, log_path, seconds, progress, base, binary_output=None, maximum_bytes=None):
        """Separate SSH snapshots report only changed status/checkpoint contents."""
        started, snapshot = time.monotonic(), None
        if binary_output is not None and (type(maximum_bytes) is not int or maximum_bytes <= 0):
            raise DeploymentError("binary transfer requires an explicit positive byte limit")
        with Path(log_path).open("xb") as log:
            output = Path(binary_output).open("xb") if binary_output is not None else log
            process = subprocess.Popen(self.argv(command), stdout=subprocess.PIPE if binary_output is not None else output, stderr=log)
            try:
                if binary_output is not None:
                    total, reported = 0, started
                    while True:
                        if time.monotonic() - started >= seconds:
                            raise TimeoutError("bounded SSH retrieval exceeded local deadline")
                        ready, _, _ = select.select([process.stdout], [], [], min(1, max(0.001, seconds-(time.monotonic()-started))))
                        if not ready:
                            continue
                        block = os.read(process.stdout.fileno(), 1048576)
                        if not block:
                            break
                        if total + len(block) > maximum_bytes:
                            raise DeploymentError("retrieval transfer exceeds local byte limit; partial bytes retained")
                        output.write(block)
                        total += len(block)
                        if time.monotonic() - reported >= 30:
                            progress(f"retrieval-bytes-{total}"); reported = time.monotonic()
                    process.wait(timeout=max(0.001, seconds-(time.monotonic()-started)))
                    if process.returncode:
                        raise DeploymentError(f"remote retrieval returned {process.returncode}; partial bytes retained")
                    progress(f"retrieval-bytes-{total}")
                    return
                while process.poll() is None:
                    if time.monotonic() - started >= seconds:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill(); process.wait(timeout=5)
                        raise TimeoutError("bounded SSH stage exceeded local deadline")
                    try:
                        current = self.call(remote_command("snapshot", base), timeout=15).stdout
                    except (OSError, subprocess.SubprocessError):
                        current = None
                    if current is not None and current != snapshot:
                        parsed = json.loads(current)
                        if parsed:
                            progress("checkpoint-" + hashlib.sha256(current).hexdigest()[:16])
                        snapshot = current
                    try:
                        process.wait(timeout=min(30, max(0.001, seconds-(time.monotonic()-started))))
                    except subprocess.TimeoutExpired:
                        pass
                if process.returncode != 0:
                    raise DeploymentError(f"remote stage returned {process.returncode}; owned logs retained")
            finally:
                if process.poll() is None:
                    process.terminate()
                    try: process.wait(timeout=5)
                    except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=5)
                if output is not log:
                    output.close()
                if process.stdout is not None:
                    process.stdout.close()


def connect_owned(store, progress, *, seconds=600):
    deadline = time.monotonic() + seconds
    ssh = None
    while time.monotonic() < deadline:
        record = worker.owned_record(store)
        pod = worker.direct_lookup(record["pod_id"])
        if pod is None:
            raise DeploymentError("owned worker disappeared before SSH readiness")
        worker.observed_actual_contract(store, pod)
        try:
            host, port = endpoint(pod)
            if ssh is not None and ssh.strict and (host, port) != (ssh.host, ssh.port):
                raise DeploymentError("pinned worker SSH endpoint changed")
            if ssh is None or (host, port) != (ssh.host, ssh.port):
                ssh = SSH(host, port, store.directory)
            ssh.call("true", timeout=15)
            if not ssh.strict:
                raise DeploymentError("SSH did not retain a task-owned host-key binding")
            progress("ssh-authenticated")
            return ssh
        except (KeyError, ValueError, subprocess.SubprocessError):
            time.sleep(3)
    raise TimeoutError("owned worker SSH readiness deadline exceeded")


def stages(base, prepared):
    source, incoming, results = (base + "/" + name for name in ("source", "incoming", "results"))
    python = source + "/.venv/bin/python"
    common = ["--source-commit", prepared["source_commit"], "--source-inventory", incoming + "/source-inventory.json",
              "--source-inventory-sha256", prepared["assets"]["source-inventory.json"]["sha256"]]
    torch_probe = ("import json,sys,torch; d={'python':sys.version,'torch':torch.__version__,'cuda':torch.version.cuda,"
                   "'gpu_count':torch.cuda.device_count(),'gpu_name':torch.cuda.get_device_name(0)}; print(json.dumps(d)); "
                   "assert sys.version_info[:2]==(3,13) and torch.__version__.split('+')[0]=='2.8.0' "
                   "and torch.version.cuda=='12.8' and d['gpu_count']==1 and d['gpu_name'] in ('A40','NVIDIA A40')")
    setup = [
        {"name": "install-uv", "argv": ["python3", "-m", "pip", "install", "uv==0.9.21", "--index-url", "https://pypi.org/simple"]},
        {"name": "managed-python", "argv": ["uv", "python", "install", "3.13"]},
        {"name": "locked-environment", "argv": ["uv", "sync", "--locked", "--no-dev", "--python", "3.13"]},
        {"name": "cuda-overlay", "argv": ["uv", "pip", "install", "--python", python, "torch==2.8.0", "--index-url", "https://download.pytorch.org/whl/cu128"]},
        {"name": "python-version", "argv": [python, "-c", "import sys; print(sys.version)"], "stdout": "environment/python.txt"},
        {"name": "pip-freeze", "argv": ["uv", "pip", "freeze", "--python", python], "stdout": "environment/pip-freeze.txt"},
        {"name": "hardware", "argv": ["nvidia-smi", "--query-gpu=name,uuid,driver_version,memory.total", "--format=csv"], "stdout": "environment/nvidia-smi.txt"},
        {"name": "torch-probe", "argv": [python, "-c", torch_probe], "stdout": "environment/torch.json"},
        {"name": "source-preflight", "argv": [python, "scripts/run_symbolic_center_pilot.py", "--manifest", PILOT_MANIFEST, "--mode", "preflight", *common]},
    ]
    qualification_steps = [{"name": "gpu-control", "argv": [python, "scripts/qualify_symbolic_gpu_records.py", "--mode", "gpu",
                           "--output", results + "/gpu-control.json", "--cpu-control", incoming + "/cpu-control.json",
                           "--cpu-control-sha256", prepared["cpu_control_sha256"], *common]}]
    collection = [{"name": "raw-collection", "argv": [python, "scripts/run_symbolic_center_pilot.py", "--manifest", PILOT_MANIFEST,
                   "--mode", "collect", "--output-dir", results + "/collection", *common]}]
    return [{"name": name, "seconds": STAGE_SECONDS[name], "steps": steps}
            for name, steps in (("setup", setup), ("qualification", qualification_steps), ("collection", collection))]


def extract_retrieval(archive_path, destination, limits):
    """Exclusive, bounded, no-link extraction; verify every remote file hash."""
    destination = Path(destination)
    destination.mkdir(mode=0o700, parents=False, exist_ok=False)
    with tarfile.open(archive_path, "r:") as archive:
        members = archive.getmembers()
        if len(members) > limits["maximum_files"] + 1 or not members or members[0].name != "retrieval-manifest.json":
            raise DeploymentError("retrieval archive lacks its bounded leading inventory")
        if any(not member.isfile() or not safe_name(member.name) for member in members):
            raise DeploymentError("retrieval archive contains links, directories, or unsafe names")
        if len({member.name for member in members}) != len(members) or members[0].size > 1048576:
            raise DeploymentError("duplicate or oversized retrieval inventory")
        with archive.extractfile(members[0]) as stream:
            inventory = json.loads(stream.read())
        if inventory.get("schema") != "butterfly.symbolic-remote-assets.v1":
            raise DeploymentError("unsupported remote inventory")
        rows = inventory["assets"]
        if len(rows) > limits["maximum_files"] or len({row["path"] for row in rows}) != len(rows):
            raise DeploymentError("duplicate or excessive remote inventory")
        expected = {row["path"]: row for row in rows}
        if set(expected) != {member.name for member in members[1:]}:
            raise DeploymentError("remote inventory and archive file sets differ")
        if sum(member.size for member in members[1:]) > limits["maximum_total_bytes"]:
            raise DeploymentError("retrieval archive exceeds byte budget")
        for member in members[1:]:
            row = expected[member.name]
            if not ASSET.fullmatch(member.name) or type(row["bytes"]) is not int or row["bytes"] != member.size:
                raise DeploymentError("unexpected retrieval filename or size")
            if not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
                raise DeploymentError("invalid remote SHA-256")
            path = destination / member.name
            path.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            with archive.extractfile(member) as source, path.open("xb") as output:
                for block in iter(lambda: source.read(1048576), b""):
                    digest.update(block); output.write(block)
            if digest.hexdigest() != row["sha256"]:
                raise DeploymentError("remote/local artifact hash mismatch")
    pilot.write_new_json(destination / "retrieval-manifest.json", inventory)
    return inventory


def validate_retrieved_collection(directory, inventory, prepared):
    """Check complete declared raw closure only; never integrate or fit records."""
    directory = Path(directory)
    listed = {row["path"]: row for row in inventory["assets"]}

    def asset(name):
        row = listed.get(name)
        path = directory / name
        if row is None or not ASSET.fullmatch(name) or path.is_symlink() or not path.is_file():
            raise DeploymentError("required retrieved evidence missing: " + name)
        if path.stat().st_size != row["bytes"] or pilot.sha256_file(path) != row["sha256"]:
            raise DeploymentError("retrieved evidence changed: " + name)
        return path

    def source_ok(value):
        return (value.get("commit") == prepared["source_commit"]
                and value.get("mode") == "explicit_inventory"
                and value.get("inventory_sha256") == prepared["assets"]["source-inventory.json"]["sha256"])

    gpu = json.loads(asset("gpu-control.json").read_bytes())
    cpu_path = directory.parent / "prepared-inputs/cpu-control.json"
    if pilot.sha256_file(cpu_path) != prepared["cpu_control_sha256"]:
        raise DeploymentError("prepared CPU control changed before retrieval validation")
    cpu = json.loads(cpu_path.read_bytes())
    benchmark = gpu.get("benchmark") or {}
    projected = benchmark.get("projected_collection_seconds_with_margin")
    if (gpu.get("schema") != "butterfly.symbolic-gpu-deployment-control.v1" or gpu.get("mode") != "gpu"
            or gpu.get("passed") is not True or not source_ok(gpu.get("source", {}))
            or gpu.get("cpu_control_sha256") != prepared["cpu_control_sha256"]
            or gpu.get("parent_sha256") != qualification.PARENT_HASH
            or gpu.get("qualification_script_sha256") != cpu["qualification_script_sha256"]
            or gpu.get("state_atol") != qualification.STATE_ATOL or gpu.get("time_atol") != qualification.TIME_ATOL
            or type(projected) not in (int, float) or not 0 < projected <= qualification.MAXIMUM_PROJECTED_COLLECTION_SECONDS):
        raise DeploymentError("retrieved GPU qualification is not passing and source/timing bound")
    collection = json.loads(asset("collection/receipt.json").read_bytes())
    binding = prepared["collection_binding"]
    if (collection.get("schema") != "butterfly.symbolic-center-collection.v1" or collection.get("experiment_id") != "EXP-477"
            or collection.get("status") != "completed" or collection.get("collection_passed") is not True
            or collection.get("nomination_performed") is not False or not source_ok(collection.get("source", {}))
            or collection.get("manifest_sha256") != prepared["pilot_manifest_sha256"]
            or collection.get("input_hashes") != binding["input_hashes"]
            or collection.get("completed_candidate_ids") != binding["candidate_ids"]
            or collection.get("uncompleted_candidate_ids") != []):
        raise DeploymentError("retrieved collection is incomplete or differs from frozen bindings")
    size, ids, profiles = binding["batch_size"], binding["candidate_ids"], binding["profiles"]
    batches = collection["batches"]
    if len(batches) != (len(ids) + size - 1) // size:
        raise DeploymentError("retrieved collection lacks complete batch set")
    for index, batch in enumerate(batches):
        expected_ids = ids[index * size:(index + 1) * size]
        if batch.get("index") != index or batch.get("candidate_ids") != expected_ids or len(batch["profiles"]) != len(profiles):
            raise DeploymentError("retrieved batch candidate/profile coverage differs from frozen order")
        for profile_index, (metadata, profile) in enumerate(zip(batch["profiles"], profiles, strict=True)):
            name = f"batch-{index:04d}-profile-{profile_index}"
            if (metadata.get("schema") != "butterfly.symbolic-center-raw-batch.v1"
                    or metadata.get("validity_passed") is not True or metadata.get("profile") != profile
                    or metadata.get("candidate_ids") != expected_ids):
                raise DeploymentError("retrieved raw metadata binding/validity failed")
            for key, suffix in (("metadata_file", ".json"), ("raw", ".npz")):
                descriptor = metadata[key]
                if descriptor.get("path") != name + suffix:
                    raise DeploymentError("retrieved raw descriptor filename differs from batch identity")
                path = asset("collection/" + name + suffix)
                if describe(path) != descriptor:
                    raise DeploymentError("retrieved raw descriptor differs from hashed inventory")
            expected = {key: value for key, value in metadata.items() if key != "metadata_file"}
            if json.loads((directory / "collection" / (name + ".json")).read_bytes()) != expected:
                raise DeploymentError("retrieved metadata differs from collection receipt")
            checkpoint = json.loads(asset("collection/" + name + "-checkpoint.json").read_bytes())
            if checkpoint != {"candidate_ids": expected_ids, "raw_metadata": metadata}:
                raise DeploymentError("retrieved checkpoint differs from complete raw metadata")
    for name in ("collection/started.json", "environment/python.txt", "environment/pip-freeze.txt",
                 "environment/nvidia-smi.txt", "environment/torch.json"):
        asset(name)
    for name in ("setup", "qualification", "collection"):
        asset("logs/" + name + ".log")
        if json.loads(asset("status/" + name + ".json").read_bytes()).get("passed") is not True:
            raise DeploymentError("retrieved stage did not finish successfully")
    return {"complete": True, "candidate_count": len(ids), "profile_batch_count": len(batches) * len(profiles)}


def workload(prepared, output_dir, *, evidence_store=None):
    output_dir = Path(output_dir)

    def execute(pod, store, progress):
        del pod  # Re-read exact-owned provider state; never trust an alternative host.
        owned = worker.owned_record(store)
        nonce = owned["nonce"]
        if not re.fullmatch(r"[0-9a-f]{32}", nonce):
            raise DeploymentError("invalid owned nonce")
        base = "/workspace/butterfly-exp477-" + nonce
        if evidence_store is not None:
            evidence_store.binding.update(task_worker_id=owned["pod_id"], task_worker_name=owned["name"],
                                          task_worker_nonce=nonce, source_commit=prepared["source_commit"])
        receipt = {"schema": "butterfly.symbolic-cloud-workload.v1", "started_utc": pilot.utc_now(),
                   "source_commit": prepared["source_commit"], "remote_directory": base,
                   "stages": [], "retrieval_verified": False, "complete_raw_closure_verified": False,
                   "target_collection_started": False}
        ssh = None
        try:
            ssh = connect_owned(store, progress, seconds=STAGE_SECONDS["connect"])
            ssh.call(remote_command("init", base))
            for name, descriptor in prepared["assets"].items():
                path = output_dir / "prepared-inputs" / name
                if describe(path) != descriptor:
                    raise DeploymentError("prepared input changed before upload")
                ssh.upload(path, base + "/incoming")
                progress("uploaded-" + name.replace(".", "-"))
            ssh.call(remote_command("extract", base, prepared["assets"]), timeout=120)
            progress("source-and-inputs-verified")
            for stage in stages(base, prepared):
                progress(stage["name"] + "-started")
                if stage["name"] == "collection":
                    probe = ssh.call("python3 -c " + shlex.quote("import json,sys; p=json.load(open(sys.argv[1])); assert p.get('mode')=='gpu' and p.get('passed') is True and p['benchmark']['projected_collection_seconds_with_margin']<=2400.0") + " " + shlex.quote(base + "/results/gpu-control.json"))
                    del probe
                    storage = json.loads(ssh.call(remote_command("storage", base,
                            {"minimum_worker_free_bytes": prepared["runtime"]["minimum_worker_free_bytes"]})).stdout)
                    if storage.get("passed") is not True:
                        raise DeploymentError("worker lacks space/inodes for retained raw collection")
                    receipt["worker_storage_preflight"] = storage
                    receipt["target_collection_started"] = True
                ssh.monitored(remote_command("stage", base, stage), log_path=output_dir / (stage["name"] + "-ssh.log"),
                              seconds=stage["seconds"] + 45, progress=progress, base=base)
                receipt["stages"].append({"name": stage["name"], "completed_utc": pilot.utc_now()})
                progress(stage["name"] + "-completed")
        except (Exception, SystemExit, KeyboardInterrupt) as error:
            receipt["failure"] = {"type": type(error).__name__, "message": str(error)}
        finally:
            if ssh is not None and ssh.strict:
                try:
                    quiet = json.loads(ssh.call(remote_command("quiesce", base), timeout=120).stdout)
                    if quiet.get("quiescent") is not True:
                        raise DeploymentError("owned writers were not proven quiescent; snapshot refused")
                    receipt["owned_writers_quiescent"] = True
                    command = remote_command("pack", base, prepared["runtime"]["retrieval"])
                    if evidence_store is None:
                        archive = output_dir / "retrieved.tar"
                        ssh.monitored(command, log_path=output_dir / "retrieval-ssh.log", seconds=STAGE_SECONDS["retrieval"],
                                      progress=progress, base=base, binary_output=archive,
                                      maximum_bytes=archive_byte_limit(prepared["runtime"]["retrieval"]))
                        inventory = extract_retrieval(archive, output_dir / "retrieved", prepared["runtime"]["retrieval"])
                        receipt["retrieval_verified"] = True
                        receipt["retrieved_file_count"] = len(inventory["assets"])
                        receipt["retrieval_archive"] = describe(archive)
                        receipt["raw_closure"] = validate_retrieved_collection(output_dir / "retrieved", inventory, prepared)
                        receipt["complete_raw_closure_verified"] = True
                    else:
                        retrieval_started = time.monotonic()
                        try:
                            receipt["remote_transfer"] = evidence_store.receive(ssh.argv(command),
                                    seconds=STAGE_SECONDS["retrieval"] - 300, progress=progress)
                        except (Exception, SystemExit, KeyboardInterrupt) as error:
                            receipt["transfer_failure"] = {"type": type(error).__name__, "message": str(error)}
                        remaining = STAGE_SECONDS["retrieval"] - (time.monotonic() - retrieval_started)
                        if remaining <= 0:
                            raise TimeoutError("remote evidence retrieval deadline")
                        result = evidence_store.finalize(seconds=remaining)
                        receipt["remote_storage"] = result
                        receipt["retrieval_verified"] = result.get("retrieval_verified") is True
                        if receipt["retrieval_verified"]:
                            remaining = STAGE_SECONDS["retrieval"] - (time.monotonic() - retrieval_started)
                            if remaining <= 0:
                                raise TimeoutError("compact evidence retrieval deadline")
                            inventory = evidence_store.retain_compact_receipts(seconds=remaining)
                            receipt["retrieved_file_count"] = len(inventory["assets"])
                            receipt["complete_raw_closure_verified"] = result.get("complete_raw_closure_verified") is True
                            receipt["raw_closure"] = result.get("raw_closure")
                        if not receipt["complete_raw_closure_verified"]:
                            raise DeploymentError("remote raw evidence is retained but incomplete or unqualified")
                    progress("retrieval-hashes-verified")
                except (Exception, SystemExit, KeyboardInterrupt) as error:
                    receipt["retrieval_failure"] = {"type": type(error).__name__, "message": str(error)}
            else:
                receipt["retrieval_failure"] = {"type": "Unavailable", "message": "no authenticated pinned SSH session was established"}
            receipt["finished_utc"] = pilot.utc_now()
            receipt["passed"] = ("failure" not in receipt and "transfer_failure" not in receipt and receipt["retrieval_verified"]
                                 and receipt["complete_raw_closure_verified"])
            pilot.write_new_json(output_dir / "workload.json", receipt)
        return receipt

    return execute


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--cpu-control", type=Path, required=True)
    parser.add_argument("--cpu-control-sha256", required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ssh-storage-dir", help="fresh /home/ubuntu/butterfly-research/<run> evidence directory on ubuntu@prax")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--prepare-only", action="store_true", help="prepare without provisioning; --ssh-storage-dir also stages small remote control files (default)")
    action.add_argument("--execute", action="store_true", help="explicitly authorize dispatch to the bounded owned-worker controller")
    args = parser.parse_args(argv)
    prepared = prepare_inputs(args.source_commit, args.cpu_control, args.cpu_control_sha256, args.output_dir, args.state_dir,
                              ssh_storage_dir=args.ssh_storage_dir)
    evidence_store = None
    if args.ssh_storage_dir is not None:
        inventory = json.loads((args.output_dir / "prepared-inputs/source-inventory.json").read_bytes())
        evidence_store = ssh_storage.SshEvidenceStore(args.ssh_storage_dir, local_control_directory=args.output_dir)
        evidence_store.prepare(prepared, (args.output_dir / "prepared-inputs/cpu-control.json").read_bytes(),
                               helper_sha256=inventory["files"]["scripts/symbolic_ssh_storage.py"])
    if not args.execute:
        print(json.dumps({"prepared": True, "provider_calls_performed": False, "output_dir": str(args.output_dir)}))
        return 0
    if evidence_store is None:
        require_free_space(args.output_dir, prepared["runtime"]["retrieval"])
    else:
        require_local_control_space(args.output_dir)
    result = worker.run_owned_worker(prepared["plan"], args.state_dir, workload(prepared, args.output_dir, evidence_store=evidence_store))
    state = worker.Store(args.state_dir).read()
    pilot.write_new_json(args.output_dir / "lifecycle-summary.json", {
        "termination_verified": state.get("termination_verified"), "pod_id": state.get("pod_id"),
        "actual_hourly_usd": state.get("actual_hourly_usd"), "create_attempted_at": state.get("create_attempted_at"),
        "terminated_at": state.get("terminated_at"), "storage_transfer_reserve_usd": prepared["plan"]["storage_transfer_reserve_usd"],
        "maximum_spend_usd": prepared["plan"]["maximum_spend_usd"], "unrelated_resources_mutated": False})
    print(json.dumps({"passed": result["passed"], "retrieval_verified": result["retrieval_verified"],
                      "termination_verified": state.get("termination_verified")}))
    return 0 if result["passed"] and state.get("termination_verified") else 2


if __name__ == "__main__":
    raise SystemExit(main())

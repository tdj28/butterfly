#!/usr/bin/env python3
"""Single-attempt replay and turning-geometry sensitivity on saved EXP-186 data."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from butterfly import return_map as legacy
from butterfly._paired_startup import inventory,sha256,write_json
from scripts import run_exp504_guarded_contact as shared
from scripts import qualify_jones_landmark_word as historical
from scripts import exp505_turn_geometry as geometry

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'experiments/manifests/EXP-505-legacy-turning-point-impact.json'
INPUTS = {
    'experiments/manifests/EXP-186-heldout-jones-landmark-word.json':'a5375219a3497ae852aa47d68d06f7671a66d23195b2b2cab36fd7b22347e601',
    'artifacts/EXP-186/receipt.json':'efae1b0cbee8edf74bf11b6bf3de38c56418c5f8acb454ea3297722d7a836903',
    'artifacts/EXP-186/states.npz':'f58894f952a40857d29b77f12f959001cb05eaa5a9a5eb2e88d1585ddb295731',
    'python/butterfly/return_map.py':'d6d74c1cf34dd21a1e99a5e431f1d4451d228449e33cfbe1e0046488aabfc58b',
    'scripts/qualify_jones_landmark_word.py':'8bda8d425548a447f763eea64a19df3d90e1efacda3e124951366d46137dcea8'}
EXPLICIT = ['scripts/run_exp505_legacy_impact.py','scripts/audit_exp505_legacy_impact.py',
    'scripts/exp505_turn_geometry.py','tests/test_exp505_legacy_impact.py',
    'docs/experiments/EXP-505-legacy-turning-point-impact.md',
    'experiments/manifests/EXP-505-legacy-turning-point-impact.json']
equal = shared.public.numeric_equal


def plain(value):
    if isinstance(value,dict):
        return {k:plain(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):
        return [plain(v) for v in value]
    if isinstance(value,float) and not np.isfinite(value):
        return 'Infinity' if value > 0 else '-Infinity' if value < 0 else 'NaN'
    return value


def inputs():
    if any(sha256(ROOT/n) != h for n,h in INPUTS.items()):
        raise ValueError('historical raw or source hash differs')
    manifest,old = [json.loads((ROOT/n).read_bytes()) for n in list(INPUTS)[:2]]
    if (old['source']['commit'] != '877ee75e77bbbd874bbd4311ebd38f8f14e1ed95'
            or old['source']['dirty'] or old['manifest_sha256'] != INPUTS[next(iter(INPUTS))]
            or old['states_artifact_sha256'] != INPUTS['artifacts/EXP-186/states.npz']):
        raise ValueError('historical source/input binding differs')
    return manifest,old


def expected():
    inputs()
    return dict(experiment_id='EXP-505',status='prospective-retrospective-sensitivity',inputs=INPUTS,
        scopes=['both saved profiles','x and z','all five variants','all nominal/bootstrap fits','all eight word rows'],
        numerical_comparison=dict(rtol=1e-12,atol=1e-13,discrete='exact'),
        limits=dict(wall_seconds=600,output_bytes=100*1024**2,minimum_free_bytes=8*1024**3),
        target_integrations=0,attempts=1,paid_review='not-requested-human-approval-policy',
        historical_receipts_modified=False,symbolic_chains_verified=False)


def load():
    p = json.loads(PLAN.read_bytes())
    if {k:v for k,v in p.items() if k != 'source_paths'} != expected() or not set(EXPLICIT)|set(INPUTS) <= set(p['source_paths']):
        raise ValueError('frozen retrospective plan differs')
    return p


def validate():
    p = load()
    geometry.controls()
    if not shared.base.imported() <= set(p['source_paths']):
        raise ValueError('consumer source closure differs')
    return dict(valid=True,target_integrations=0,target_fits=0)


def startup(p):
    target = Path(tempfile.mkdtemp(prefix='exp505-startup-')).resolve()
    names = set(p['source_paths'])|set(INPUTS)|set(shared.INPUTS)
    for n in names:
        destination = target/n
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/n,destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(target)!r});sys.path[:0]={[str(target),str(target/"python")]!r};'
        'from scripts.run_exp505_legacy_impact import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable,'-I','-B','-c',code],cwd=target,text=True,capture_output=True,check=True,timeout=60)
    if any(sha256(ROOT/n) != sha256(target/n) for n in names):
        raise ValueError('copied source/input identity')
    return dict(passed=True,isolated=True,target_fits=0,target_integrations=0,stdout=child.stdout,stderr=child.stderr,
        sources={n:sha256(target/n) for n in sorted(names)})


def oracle(source,target,manifest,mode,trace,budget=lambda:None):
    if mode not in ('original','filtered'):
        raise ValueError('declared original or filtered mode required')
    original,infer,fit = legacy._critical_points,legacy.infer_return_map_branches,legacy._fit_branch_count
    variant,ordinal = -1,0
    current_fit = None
    def tracked(spline,**options):
        old = list(original(spline,**options))
        row = geometry.inspect(spline,**options)
        if row['legacy'] != old:
            raise ValueError('independent legacy candidate reconstruction differs')
        current_fit['geometry'] = row
        return tuple(old if mode == 'original' else row['filtered'])
    def tracked_fit(x,y,**options):
        nonlocal ordinal,current_fit
        current_fit = dict(variant=manifest['oracle_variants'][variant]['name'],ordinal=ordinal,mode=mode,
            sample_sha256=hashlib.sha256(np.column_stack((x,y)).astype('<f8').tobytes()).hexdigest(),
            geometry=None,status='started')
        trace.append(current_fit)
        ordinal += 1
        result = fit(x,y,**options)
        current_fit.update(status='completed',fit_result=plain(result))
        budget()
        return result
    def inferred(*args,**kwargs):
        nonlocal variant,ordinal
        variant += 1
        ordinal = 0
        return infer(*args,**kwargs)
    with patch.object(legacy,'_critical_points',tracked),patch.object(legacy,'_fit_branch_count',tracked_fit),\
            patch.object(legacy,'infer_return_map_branches',inferred):
        result = legacy.infer_return_map_branches_robust(source,target,
            variants=[dict(manifest['oracle_common'],**v['options']) for v in manifest['oracle_variants']],
            minimum_variant_consensus=1.,maximum_normalized_critical_point_span=manifest['acceptance']['maximum_normalized_critical_span'])
    return plain(asdict(result))


def analyze(emit=lambda *_:None,budget=lambda:None,partial=None):
    manifest,old = inputs()
    traces = [] if partial is None else partial
    rows = []
    with np.load(ROOT/'artifacts/EXP-186/states.npz',allow_pickle=False) as archive:
        for profile,saved_profile in zip(manifest['sprinkler_profiles'],old['profiles'],strict=True):
            if profile['name'] != saved_profile['name']:
                raise ValueError('historical profile order')
            prefix = profile['name']
            raw = SimpleNamespace(midpoint_states=archive[prefix+'_midpoint_states'],midpoint_times=archive[prefix+'_midpoint_times'],
                midpoint_trajectory_ids=archive[prefix+'_midpoint_ids'])
            for coordinate in manifest['coordinates']:
                source,target = geometry.pairs(raw.midpoint_states,raw.midpoint_times,raw.midpoint_trajectory_ids,coordinate['axis'])
                reference = historical.survivor_return_pairs(raw,coordinate['axis'])
                if (not all(np.array_equal(a,b) for a,b in zip((source,target),reference,strict=True))
                        or len(source) != saved_profile['coordinates'][coordinate['name']]['pair_count']):
                    raise ValueError('independent consecutive-pair replay differs')
                row = dict(profile=prefix,coordinate=coordinate['name'],pair_count=len(source),
                    pair_sha256=hashlib.sha256(np.column_stack((source,target)).astype('<f8').tobytes()).hexdigest(),modes={})
                for mode in ('original','filtered'):
                    entry = dict(profile=prefix,coordinate=coordinate['name'],mode=mode,fits=[])
                    traces.append(entry)
                    robust = oracle(source,target,manifest,mode,entry['fits'],budget)
                    words = [historical._word_row(dict(robust=robust,source_values=source,target_values=target),coordinate,
                        archive[solver+'_orbit_states'],solver,prefix,manifest) for solver in manifest['correction_solvers']]
                    if mode == 'original':
                        saved_words = [w for w in old['words'] if w['profile'] == prefix and w['coordinate'] == coordinate['name']]
                        if (not equal(robust,plain(saved_profile['coordinates'][coordinate['name']]['robust']))
                                or not equal(plain(words),plain(saved_words))):
                            raise ValueError('original partition or word replay differs')
                    entry.update(robust=robust,words=plain(words))
                    row['modes'][mode] = entry
                    emit(prefix+'--'+coordinate['name']+'--'+mode,entry)
                row['robust_unchanged'] = equal(row['modes']['original']['robust'],row['modes']['filtered']['robust'])
                row['words_unchanged'] = equal(row['modes']['original']['words'],row['modes']['filtered']['words'])
                original_fits,filtered_fits = [row['modes'][mode]['fits'] for mode in ('original','filtered')]
                if [(f['variant'],f['ordinal'],f['sample_sha256']) for f in original_fits] != [
                        (f['variant'],f['ordinal'],f['sample_sha256']) for f in filtered_fits]:
                    raise ValueError('sensitivity changed the requested fit population')
                row['removed_root_occurrences'] = sum(len(f['geometry']['legacy'])-len(f['geometry']['filtered'])
                    for f in original_fits if f['geometry'] is not None)
                rows.append(row)
    return dict(rows=rows,original_reproduced=True,all_robust_outputs_unchanged=all(r['robust_unchanged'] for r in rows),
        all_word_rows_unchanged=all(r['words_unchanged'] for r in rows),
        removed_root_occurrences=sum(r['removed_root_occurrences'] for r in rows),
        fit_calls=sum(len(r['modes'][mode]['fits']) for r in rows for mode in ('original','filtered')),
        scope='Only turning-filter sensitivity on saved EXP-186 partitions and words; not raw trajectory recertification or archive-wide clearance.')


def execute(output,source,remote):
    p = load()
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if git('rev-parse','HEAD') != source or git('status','--porcelain') or git('ls-remote','origin',remote).split() != [source,remote]:
        raise ValueError('clean live-pushed source required')
    validate()
    output = output.resolve()
    marker = ROOT/'artifacts/EXP-505/target-once.json'
    if ROOT/'artifacts/EXP-505' not in output.parents or output.exists() or marker.exists():
        raise ValueError('fresh output and new exclusive attempt required')
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=shared.base.utc(),plan_sha256=sha256(PLAN),
        inputs=INPUTS,sources={n:sha256(ROOT/n) for n in p['source_paths']},python=sys.version,
        numpy=np.__version__,scipy=shared.base.scipy.__version__)
    write_json(output/'binding.json',binding)
    start = time.monotonic()
    partial = []
    def budget():
        if (time.monotonic()-start > p['limits']['wall_seconds'] or shutil.disk_usage(ROOT).free < p['limits']['minimum_free_bytes']
                or sum(f.stat().st_size for f in output.rglob('*') if f.is_file()) > p['limits']['output_bytes']):
            raise RuntimeError('retrospective resource cap')
    def emit(name,entry):
        write_json(output/(name+'.json'),entry)
        budget()
        print(json.dumps(dict(completed=name,fit_calls=len(entry['fits']))),flush=True)
    def timeout(*_):
        raise RuntimeError('retrospective wall deadline')
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        write_json(output/'startup.json',startup(p))
        write_json(output/'controls.json',geometry.controls())
        budget()
        write_json(marker,binding)
        result = analyze(emit,budget,partial)
        write_json(output/'summary.json',dict(experiment_id='EXP-505',status='completed',binding=binding,result=result,
            target_integrations=0,paid_review=p['paid_review'],symbolic_chains_verified=False,files=inventory(output),
            marker_sha256=sha256(marker),completed_utc=shared.base.utc(),elapsed_seconds=time.monotonic()-start))
        print(json.dumps(dict(completed=True,summary_sha256=sha256(output/'summary.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        write_json(output/'failure.json',dict(error_type=type(exc).__name__,message=str(exc),partial=partial,files=inventory(output)))
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp505_legacy_impact  # noqa: F401
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--prepare',action='store_true')
    mode.add_argument('--startup',action='store_true')
    mode.add_argument('--execute',action='store_true')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--source-commit')
    parser.add_argument('--remote-ref')
    a = parser.parse_args()
    if a.prepare:
        p = expected()
        p['source_paths'] = sorted(set(EXPLICIT)|set(INPUTS)|set(shared.load()['source_paths'])|shared.base.imported())
        write_json(PLAN,p)
    elif a.execute:
        if not all((a.output_dir,a.source_commit,a.remote_ref)):
            parser.error('fresh output and source/ref required')
        execute(a.output_dir,a.source_commit,a.remote_ref)
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__ == '__main__':
    main()

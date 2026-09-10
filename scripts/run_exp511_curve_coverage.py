#!/usr/bin/env python3
"""One-shot direct sampling of the failed EXP-510 depth-eight curves."""
import argparse
from dataclasses import replace
import json
import math
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import numpy as np
from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from butterfly.models import RosslerParameters,rossler_rhs,rossler_jacobian
from butterfly.poincare import legacy_rossler_section,PoincareSection
from scripts import run_exp510_fold_transport as prior
from scripts import verify_exp510_public_transport as public
from scripts import exp511_curve_coverage as model
from scripts import exp511_dense_census as dense
from scripts.exp507_bounded_products import producers
from scripts.run_exp486_return_image_folds import control_field

ROOT = prior.ROOT
PLAN = ROOT/'experiments/manifests/EXP-511-direct-curve-coverage.json'
RECEIPT = 'docs/experiments/receipts/EXP-510-four-substep-fold-transport-result.json'
WITNESS = 'docs/experiments/receipts/EXP-510-collapsed-root-witness.json'
INPUTS = dict(prior.INPUTS,**{RECEIPT:'43399d794bf8c55a20e73706a4850453f43ac762a465a3a7d39b9cc7665a8fe7',
    WITNESS:'5b271195075b337b72b09552c5b86f707f2e68595a7f8974262a1cbce7518df9'})
EXPLICIT = ['scripts/run_exp511_curve_coverage.py','scripts/audit_exp511_curve_coverage.py',
    'scripts/exp511_curve_coverage.py','scripts/exp511_dense_census.py','scripts/prepare_exp511_prior_witness.py',
    'scripts/verify_exp510_public_transport.py','tests/test_exp510_public_transport.py',
    'tests/test_exp511_curve_coverage.py','docs/experiments/EXP-511-direct-curve-coverage.md',
    'experiments/manifests/EXP-511-direct-curve-coverage.json','python/butterfly/periodic_winding.py']
base = prior.base


def inputs():
    if any(sha256(ROOT/n)!=h for n,h in INPUTS.items()):
        raise ValueError('fixed curve inputs differ')
    public.verify(ROOT/RECEIPT,INPUTS[RECEIPT])
    rows = json.loads((ROOT/RECEIPT).read_bytes())['result']['rows']
    witness = json.loads((ROOT/WITNESS).read_bytes())
    if witness['parameters']!=rows[1]['spec']['parameters'] or witness['new_integrations']!=0:
        raise ValueError('collapsed diagnostic witness differs')
    curves = prior.model.candidates(base.load(),rows[0]['folds'],rows[1]['spec'],prior.offset(rows[1]['spec']['parameters']))
    curves = [c for c in curves if '--depth-8--' in c['family_id']]
    for c in curves:
        anchors = [r for r in witness['rows'] if r['family_id']==c['family_id']]
        if [r['method'] for r in anchors]!=['DOP853','Radau']:
            raise ValueError('complete failed-root solver matrix required')
        c['grid'] = model.grid(c,[r['u'] for r in anchors])
    targets = [dict(id=f['id'],method=v['method'],**{k:v['observations'][1][k] for k in ('image_state','next_state')})
        for f in rows[1]['folds'] if '--depth-4--' in f['family_id'] and f['qualified_in_region'] for v in f['solvers']]
    if len(curves)!=2 or len(targets)!=4:
        raise ValueError('two curves and four reference states required')
    return dict(parameters=rows[1]['spec']['parameters'],curves=curves,targets=targets)


def expected():
    return dict(experiment_id='EXP-511',status='prospective-outcome-informed-direct-curve-diagnostic',
        inputs=INPUTS,selection=inputs(),solvers=['DOP853','Radau'],attempts=1,
        grid_rule='17 uniform nodes in the original substep-2 u-box plus mean collapsed root and +/- epsilon; sorted unique, at most 20',
        numerical=base.load()['fold'],newton_refinements=0,new_cycles=0,new_boundaries=0,
        limits=dict(target_ivps=160,wall_seconds=3600,output_bytes=2*1024**3,
            initial_free_bytes=11*1024**3,minimum_free_bytes=8*1024**3,failure_reserve_bytes=1024**2),
        controls=dict(profiles=6,ivps=12,output_bytes=64*1024**2,wall_seconds=120,
            kinds=['fold','no-fold','projection-degenerate'],solvers=['DOP853','Radau'],analytic_tolerance=1e-8),
        paid_review='not-requested-human-approval-policy',symbolic_chains_verified=False,
        source_paths=sorted(set(prior.load()['source_paths'])|set(EXPLICIT)))


def load():
    p = json.loads(PLAN.read_bytes())
    if p!=expected():
        raise ValueError('direct-curve frozen plan differs')
    return p


def fields(candidate):
    par = RosslerParameters(**candidate['parameters'])
    return (lambda t,q:rossler_rhs(t,q,par),lambda t,q:rossler_jacobian(q,par),
        replace(legacy_rossler_section(par),direction=-1))


def validate():
    p = load()
    if not base.imported()<=set(p['source_paths']):
        raise ValueError('source closure incomplete: '+str(sorted(base.imported()-set(p['source_paths']))))
    selection = p['selection']
    for c in selection['curves']:
        rhs,_,section = fields(c)
        for u in c['grid']:
            q = np.asarray(c['initial_state'])+u*np.asarray(c['initial_tangent'])
            if not section.accepts(q) or abs(section.value(q))>1e-10 or section.direction*(np.asarray(section.normal)@rhs(0,q))<=0:
                raise ValueError('declared grid has invalid initial section orientation')
    return dict(valid=True,new_integrations=0,curves=len(selection['curves']),profiles=sum(len(c['grid'])*2 for c in selection['curves']))


def startup(p):
    target = Path(tempfile.mkdtemp(prefix='exp511-startup-')).resolve()
    names = set(p['source_paths'])|set(INPUTS)
    for name in names:
        destination = target/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(target)!r});'
        f'sys.path[:0]={[str(target),str(target/"python")]!r};'
        'from scripts.run_exp511_curve_coverage import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable,'-I','-B','-c',code],cwd=target,capture_output=True,text=True,check=True,timeout=120)
    if any(sha256(ROOT/n)!=sha256(target/n) for n in names):
        raise ValueError('isolated copied source changed')
    return dict(passed=True,isolated=True,new_integrations=0,stdout=child.stdout,stderr=child.stderr,
        sources={n:sha256(target/n) for n in sorted(names)})


def write(root,path,value,limits,reserve=True):
    return write_bounded_json(root,path,value,limit_bytes=limits['output_bytes'],
        minimum_free_bytes=limits['minimum_free_bytes'],reserve_bytes=limits['failure_reserve_bytes'] if reserve else 0)


def control_case(kind):
    # Express the analytic z coordinate in the target's .01 physical scale;
    # conjugate k*z^2 accordingly. Target regularity thresholds stay unchanged.
    k = 0. if kind=='no-fold' else 10000.
    initial,tangent,u = [-4.,0.,.005],[1.,0.,.01],0.
    if kind=='fold':
        u = 1/(2*(1-math.exp(-2*.03*2*math.pi*3)))-.5
    elif kind=='projection-degenerate':
        initial,tangent = [-4.,0.,0.],[0.,0.,.01]
    elif kind!='no-fold':
        raise ValueError('unknown analytic control')
    c = dict(initial_state=initial,initial_tangent=tangent,count=3,horizon=20.)
    settings = dict(base.load()['fold'],rtol=1e-11,atol=1e-13,max_step=.02)
    return c,u,settings,(*control_field(k=k),PoincareSection((0.,1.,0.),0.,-1)),k


def control_verdict(profile,c,u,k):
    if profile['status']!='completed' or profile['measurement']['image']['status']!='returned':
        raise ValueError('analytic control did not return')
    q = np.asarray(c['initial_state'])+u*np.asarray(c['initial_tangent'])
    v = np.asarray(c['initial_tangent'])
    errors = []
    for n,e in enumerate(profile['measurement']['image']['events'],1):
        rho = math.exp(-.03*2*math.pi*n)
        state = [q[0]-k*q[2]**2*(1-rho**2),0.,q[2]*rho]
        tangent = [v[0]-2*k*q[2]*v[2]*(1-rho**2),0.,v[2]*rho]
        errors.append(max(abs(e['time']-2*math.pi*n),float(np.max(abs(np.asarray(e['state'])-state))),float(np.max(abs(np.asarray(e['tangent'])-tangent)))))
    o = profile['measurement']['observation']
    degenerate = v[0]==0
    if max(errors)>1e-8 or o['valid']==degenerate:
        raise ValueError('analytic control state/tangent/regularity differs')
    if not degenerate:
        slope = 0. if k else 1.
        if abs(o['x_graph_slope']-slope)>1e-8:
            raise ValueError('analytic slope differs')
    return dict(passed=True,errors=errors,regular=o['valid'])


def controls(output):
    p = load()
    if output.exists():
        raise ValueError('fresh controls output required')
    output.mkdir(parents=True)
    limits = dict(p['limits'],output_bytes=p['controls']['output_bytes'])
    calls,start = 0,time.monotonic()
    def budget(integrating=False):
        nonlocal calls
        if time.monotonic()-start>p['controls']['wall_seconds']:
            raise RuntimeError('control time cap')
        if integrating:
            if calls>=p['controls']['ivps']:
                raise RuntimeError('control IVP cap')
            calls+=1
    rows = []
    with producers(base,output,limits):
        for kind in p['controls']['kinds']:
            c,u,settings,(rhs,jac,section),k = control_case(kind)
            for method in p['solvers']:
                label = kind+'--'+method
                retained = {}
                def retain(name,raw):
                    base.retain_npz(output/(label+'--'+name+'.npz'),raw)
                    retained[name]=raw
                profile = dense.capture(c,u,method,settings,rhs,jac,section,retain,budget)
                rebuilt = dense.replay(profile,c,u,settings,rhs,section,retained)
                if not public.equal(profile,rebuilt):
                    raise ValueError('analytic dense replay differs')
                verdict = control_verdict(rebuilt,c,u,k)
                row = dict(kind=kind,profile=profile,verdict=verdict)
                write(output,output/(label+'.json'),row,limits)
                rows.append(row)
    result = dict(passed=True,control_ivps=calls,rows=rows,elapsed_seconds=time.monotonic()-start,
        source_hashes={n:sha256(ROOT/n) for n in p['source_paths']},files=inventory(output))
    write(output,output/'summary.json',result,limits)
    return dict(passed=True,control_ivps=calls,summary_sha256=sha256(output/'summary.json'))


def execute(output,source,remote,control_output):
    from scripts.audit_exp511_curve_coverage import audit_controls
    p = load()
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if git('rev-parse','HEAD')!=source or git('status','--porcelain') or git('ls-remote','origin',remote).split()!=[source,remote]:
        raise ValueError('clean exact live-pushed source required')
    validate()
    control_result = audit_controls(control_output)
    root = ROOT/'artifacts/EXP-511'
    marker = root/'target-once.json'
    output = output.resolve()
    free = shutil.disk_usage(ROOT).free
    if root not in output.parents or output.exists() or marker.exists():
        raise ValueError('fresh output and unconsumed attempt required')
    if free<p['limits']['initial_free_bytes']:
        raise ValueError('initial disk reserve')
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=base.utc(),plan_sha256=sha256(PLAN),
        inputs=INPUTS,sources={n:sha256(ROOT/n) for n in p['source_paths']},initial_free_bytes=free,
        runtime=dict(python=sys.version,numpy=np.__version__,scipy=base.scipy.__version__),paid_review=p['paid_review'])
    start,calls = time.monotonic(),0
    progress,rows = [],[]
    def save(name,value,reserve=True):
        write(output,output/name,value,p['limits'],reserve)
    def budget(integrating=False):
        nonlocal calls
        if time.monotonic()-start>p['limits']['wall_seconds'] or shutil.disk_usage(ROOT).free<p['limits']['minimum_free_bytes']:
            raise RuntimeError('EXP-511 time/free-space cap')
        if integrating:
            if calls>=p['limits']['target_ivps']:
                raise RuntimeError('EXP-511 IVP cap')
            calls+=1
    def timeout(*_):
        raise TimeoutError('EXP-511 wall deadline')
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        save('binding.json',binding)
        save('startup.json',startup(p))
        save('control-replay.json',control_result)
        write_bounded_json(root,marker,binding,limit_bytes=directory_bytes(root)+1024**2,minimum_free_bytes=p['limits']['minimum_free_bytes'])
        with producers(base,output,p['limits']):
            for i,c in enumerate(p['selection']['curves']):
                folder = output/f'curve-{i}'
                folder.mkdir()
                samples = []
                rhs,jac,section = fields(c)
                for j,u in enumerate(c['grid']):
                    profiles = []
                    for method in p['solvers']:
                        label = f'node-{j:02d}--'+method
                        progress.append(dict(curve=i,node=j,method=method,status='started'))
                        save(f'curve-{i}/'+label+'-started.json',dict(u=u,method=method,started_utc=base.utc()))
                        profile = dense.capture(c,u,method,p['numerical'],rhs,jac,section,
                            lambda name,raw:base.retain_npz(folder/(label+'--'+name+'.npz'),raw),budget)
                        save(f'curve-{i}/'+label+'.json',profile)
                        progress[-1]['status']=profile['status']
                        profiles.append(profile)
                    sample = dict(u=u,profiles=profiles,pair=model.pair(profiles,p['numerical']['scales']))
                    samples.append(sample)
                    print(json.dumps(dict(curve=i,node=j,regular=sample['pair']['regular'],target_ivps=calls)),flush=True)
                row = dict(candidate=c,samples=samples,analysis=model.analyze(c,samples,p['selection']['targets']))
                save(f'curve-{i}/result.json',row)
                rows.append(row)
        budget()
        save('summary.json',dict(experiment_id='EXP-511',status='completed',binding=binding,rows=rows,
            target_ivps=calls,progress=progress,elapsed_seconds=time.monotonic()-start,completed_utc=base.utc(),
            marker_sha256=sha256(marker),files=inventory(output),symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,summary_sha256=sha256(output/'summary.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json',dict(error_type=type(exc).__name__,message=str(exc),utc=base.utc(),
            target_ivps=calls,progress=progress,files=inventory(output)),False)
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp511_curve_coverage  # noqa: F401
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    for name in ('prepare','startup','controls','execute'):
        modes.add_argument('--'+name,action='store_true')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--control-dir',type=Path)
    parser.add_argument('--source-commit')
    parser.add_argument('--remote-ref')
    a = parser.parse_args()
    if a.prepare:
        write_bounded_json(PLAN.parent,PLAN,expected(),limit_bytes=directory_bytes(PLAN.parent)+1024**2)
    elif a.execute:
        if not all((a.output_dir,a.source_commit,a.remote_ref,a.control_dir)):
            parser.error('output, source, remote and control directory required')
        execute(a.output_dir,a.source_commit,a.remote_ref,a.control_dir)
    elif a.controls:
        if a.output_dir is None:
            parser.error('fresh control output required')
        print(json.dumps(controls(a.output_dir)))
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__=='__main__':
    main()

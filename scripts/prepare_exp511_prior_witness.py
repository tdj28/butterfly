#!/usr/bin/env python3
"""Extract already-audited EXP-510 root coordinates for fixed diagnostic samples."""
import json
from pathlib import Path
from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from scripts import run_exp510_fold_transport as prior

ROOT = prior.ROOT
RAW = ROOT/'artifacts/EXP-510/target-0e11f95'
OUTPUT = ROOT/'docs/experiments/receipts/EXP-510-collapsed-root-witness.json'
SUMMARY_SHA = '539cedeb5b044f97761f510a5a91b1b8026732c5089b36df173b8993e1ab5577'


def derive():
    if sha256(RAW/'summary.json') != SUMMARY_SHA:
        raise ValueError('prior summary identity differs')
    s = json.loads((RAW/'summary.json').read_bytes())
    if (s['files'] != inventory(RAW,omit=('summary.json',))
            or s['binding']['sources'] != {n:sha256(ROOT/n) for n in prior.load()['source_paths']}
            or s['binding']['source_commit'] != '0e11f95e352364afcb0be43a2e39a1d12ffaf9b5'
            or s['result']['transport_completed'] is not False or len(s['result']['rows']) != 2):
        raise ValueError('prior complete evidence binding differs')
    rows = []
    for f in s['result']['rows'][1]['folds']:
        if '--depth-8--' not in f['family_id']:
            continue
        for method in ('DOP853','Radau'):
            name = 'substep-2/'+f['id']+'--'+method+'.json'
            v = json.loads((RAW/name).read_bytes())
            if v['shooting']['converged'] is not True or v['qualification']['reason'] != 'invalid event/input projection':
                raise ValueError('previously diagnosed root status differs')
            root = v['shooting']['trace'][-1]
            rows.append(dict(id=f['id'],family_id=f['family_id'],method=method,
                u=root['u'],time=root['time'],source_path=name,source_sha256=sha256(RAW/name)))
    if len(rows) != 4:
        raise ValueError('complete two-direction/two-solver root matrix required')
    return dict(source_experiment='EXP-510',summary_sha256=SUMMARY_SHA,
        audit_sha256='43399d794bf8c55a20e73706a4850453f43ac762a465a3a7d39b9cc7665a8fe7',
        parameters=s['result']['rows'][1]['spec']['parameters'],rows=rows,
        purpose='Diagnostic sampling anchors only, not qualified folds or Newton warm starts.',new_integrations=0)


if __name__ == '__main__':
    write_bounded_json(OUTPUT.parent,OUTPUT,derive(),limit_bytes=directory_bytes(OUTPUT.parent)+1024**2)
    print(sha256(OUTPUT))

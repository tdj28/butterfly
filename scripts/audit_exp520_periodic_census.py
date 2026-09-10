#!/usr/bin/env python3
"""Replay every dense segment with separate basis expansion and root proof checks."""
import argparse
import json
from pathlib import Path
import time

import numpy as np
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.bounded_json import directory_bytes
from butterfly.models import RosslerParameters, rossler_equilibria
from scripts import run_exp520_periodic_census as run


def same(actual, expected):
    """Strict structural identity; tolerate only ordinary scalar report roundoff."""
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(same(actual[k], expected[k]) for k in actual)
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(same(a, b) for a, b in zip(actual, expected, strict=True))
    if type(actual) is float and type(expected) is float:
        return np.isfinite(actual) and np.isfinite(expected) and abs(actual-expected) <= 1e-13*max(abs(actual), abs(expected), 1e-12)
    return type(actual) is type(expected) and actual == expected


def audit(folder):
    folder = Path(folder); plan = run.load()
    saved = json.loads((folder/'summary.json').read_bytes())
    binding = saved['binding']
    wanted = {'binding.json'} | {i+'--'+m+'.json' for i in run.IDS for m in run.METHODS}
    if (saved['experiment_id'] != 'EXP-520' or saved['status'] != 'completed'
            or saved['segments'] != plan['total_segments']
            or set(saved['files']) != wanted
            or saved['files'] != inventory(folder, omit=('summary.json',))
            or binding['plan_sha256'] != sha256(run.PLAN)
            or binding['inputs'] != plan['inputs']
            or binding['parent_raw_summary_sha256'] != run.RAW_SHA
            or binding['sources'] != {n: sha256(run.ROOT/n) for n in plan['source_paths']}
            or binding != json.loads((folder/'binding.json').read_bytes())
            or binding != json.loads(run.MARKER.read_bytes())
            or saved['marker_sha256'] != sha256(run.MARKER)
            or not binding['startup']['passed'] or binding['startup']['target_data_opened'] is not False
            or not 0 < saved['elapsed_seconds'] <= plan['limits']['wall_seconds']
            or directory_bytes(folder) > plan['limits']['output_bytes']
            or saved['new_integrations'] != 0
            or any(saved[k] is not False for k in ('exact_flow_completeness', 'symbolic_chains_verified', 'D_identified'))):
        raise ValueError('complete frozen census identity, source or output binding differs')
    run.authenticate_raw(plan)
    points, segments = [], 0
    started = time.monotonic()
    def tick():
        nonlocal segments
        segments += 1
        if time.monotonic()-started > plan['limits']['wall_seconds'] or segments > plan['limits']['maximum_segments']:
            raise ValueError('bounded audit limit reached')
    for trial in plan['trials']:
        profiles = []
        origin = rossler_equilibria(RosslerParameters(**trial['parameters']))[0].tolist()
        for config in trial['profiles']:
            name = trial['id']+'--'+config['method']+'.json'
            product = json.loads((folder/name).read_bytes())
            row = next(r for r in plan['observations'] if (r['point'], r['method']) == (trial['id'], config['method']))
            if product['trial'] != trial or product['method'] != config['method'] or product['input'] != row:
                raise ValueError('complete per-profile identity differs')
            with np.load(run.RAW/row['raw_path'], allow_pickle=False) as source:
                raw = {n: source[n] for n in source.files}
            result, _ = run.model.profile(raw, config['method'], trial['parameters'], origin,
                config['period'], certificate=product['certificates'], tick=tick)
            if not same(result, product['result']):
                raise ValueError('separate exact basis/root-proof replay differs')
            profiles.append(result)
            print(json.dumps(dict(audited_profile=name, segments=segments)), flush=True)
        points.append(dict(id=trial['id'], parameters=trial['parameters'], origin=origin,
            profiles=profiles, comparison=run.model.point_comparison(profiles, [p['period'] for p in trial['profiles']])))
    if (segments != plan['total_segments'] or not same(points, saved['points'])
            or saved['all_profiles_qualified'] != all(p['comparison']['qualified'] for p in points)
            or saved['all_nearest_consistent'] != all(p['comparison']['consistent_nearest'] for p in points)):
        raise ValueError('full point inventory or final qualifications differ')
    run.authenticate_raw(plan)
    if binding['sources'] != {n: sha256(run.ROOT/n) for n in plan['source_paths']}:
        raise ValueError('source drift during audit')
    return dict(experiment_id='EXP-520', passed=True, source_commit=binding['source_commit'],
        plan_sha256=sha256(run.PLAN), summary_sha256=sha256(folder/'summary.json'),
        parent_audit_sha256=run.PARENT_SHA, parent_raw_sha256=run.RAW_SHA,
        segments=segments, profiles=10, windows=20, points=points,
        all_profiles_qualified=saved['all_profiles_qualified'], all_nearest_consistent=saved['all_nearest_consistent'],
        output_bytes=directory_bytes(folder), new_integrations=0, paid_review=plan['paid_review'],
        exact_flow_completeness=False, symbolic_chains_verified=False, D_identified=False,
        scope='All retained-polynomial stationarity roots audited by separate exact basis expansion and Bernstein coverage verification. Geometry/classification code is shared. This is not exact-flow completeness, a C/D dictionary, a homoclinic proof or a verified Jones word arrow.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('fresh audit receipt required')
    result = audit(args.input)
    write_json(args.output, result)
    print(json.dumps(dict(passed=result['passed'], receipt_sha256=sha256(args.output))))

#!/usr/bin/env python3
"""Audit complete saved coverage and preserve the earlier fixed-ordinal verdicts.

This is a same-agent saved-event algebra audit, not independent integration
or a second audit of the predecessor's local raw dense polynomials.
"""
import argparse
import json
import math
from pathlib import Path

from scripts import exp516_ordinal_coverage as screen


def audit(path, expected_sha):
    replay = screen.verify(path, expected_sha)
    receipt = json.loads(path.read_bytes())
    saved, plan, _ = screen.load_inputs()
    source = saved['result']['rows']
    report = receipt['analysis']['rows']
    counts = dict(profiles=0, accepted_events=0, retained_pairs=0,
        terminal_events_without_successor=0, fixed_ordinal_decisions_preserved=0,
        paired_ordinal_cells=0, missing_ordinal_cells=0, regular_cells=0,
        coverage_cells=0, endpoint_candidate_cells=0, full_state_reference_distances=0)
    cancellation_absolute_error = 0.
    for old_row, row in zip(source, report, strict=True):
        parameters = old_row['candidate']['parameters']
        for old_sample, sample in zip(old_row['samples'], row['samples'], strict=True):
            for old_profile, profile in zip(old_sample['profiles'], sample['profiles'], strict=True):
                raw = [e for e in old_profile['report']['reconstructed'] if e['accepted']]
                if len(profile['events']) != len(raw) or len(profile['pairs']) != max(0, len(raw)-1):
                    raise ValueError('incomplete saved event/pair coverage')
                if profile['horizon'] != old_profile['report']['horizon']:
                    raise ValueError('horizon changed')
                if profile['last_event'] != (profile['events'][-1] if raw else None):
                    raise ValueError('terminal right-censoring changed')
                counts['profiles'] += 1
                counts['accepted_events'] += len(raw)
                counts['retained_pairs'] += max(0, len(raw)-1)
                counts['terminal_events_without_successor'] += bool(raw)
                for e, observed in zip(raw, profile['events'], strict=True):
                    if observed['time'] != e['time'] or observed['state'] != e['state']:
                        raise ValueError('event state/time changed')
                    x, y, z = e['state']
                    f = [-y-z, x+parameters['a']*y, parameters['b']+z*(x-parameters['c'])]
                    # Different arithmetic from the determinant-form producer.
                    dt = -e['raw_tangent'][1]/f[1]
                    v = [e['raw_tangent'][j]+f[j]*dt for j in range(3)]
                    error = max(abs(v[j]-observed['tangent'][j])/screen.SCALES[j] for j in range(3))
                    scale = max(1., *(abs(w)/s for w, s in zip(v, screen.SCALES, strict=True)))
                    if error > 1e-10*scale:
                        raise ValueError('separately evaluated event correction differs')
                    cancellation_absolute_error = max(cancellation_absolute_error, error)
            eighth = next(r for r in sample['comparisons'] if r['ordinal'] == 8)
            if eighth['paired_regular'] != old_sample['pair']['regular']:
                raise ValueError('old eighth-return regularity verdict changed')
            counts['fixed_ordinal_decisions_preserved'] += 1
        for ordinal in row['ordinals']:
            if len(ordinal['nodes']) != 20 or len(ordinal['cells']) != 19:
                raise ValueError('missing original node or adjacent cell')
            for node in ordinal['nodes']:
                comp = node['comparison']
                if any(m is None for m in comp['methods']):
                    counts['missing_ordinal_cells'] += 1
                    if comp['joint_distance'] is not None or comp['paired_regular']:
                        raise ValueError('missing pair fabricated')
                    continue
                counts['paired_ordinal_cells'] += 1
                counts['regular_cells'] += comp['paired_regular']
                counts['coverage_cells'] += comp['sampled_reference_coverage']
                values = []
                for which, ref, key in [('input', 'image_state', 'input_distances'),
                                        ('output', 'next_state', 'output_distances')]:
                    for mi, method in enumerate(comp['methods']):
                        for ti, target in enumerate(plan['selection']['targets']):
                            d = max(abs(method[which]['state'][j]-target[ref][j])/screen.SCALES[j] for j in range(3))
                            if comp[key][mi][ti] != d:
                                raise ValueError('full-state reference distance differs')
                            values.append(d)
                            counts['full_state_reference_distances'] += 1
                if comp['joint_distance'] != max(values):
                    raise ValueError('conservative full-reference maximum differs')
            counts['endpoint_candidate_cells'] += sum(c['endpoint_candidate'] for c in ordinal['cells'])
    if counts['profiles'] != 80 or counts['fixed_ordinal_decisions_preserved'] != 40:
        raise ValueError('complete old population required')
    if not math.isfinite(cancellation_absolute_error):
        raise ValueError('nonfinite correction error')
    return dict(experiment_id='EXP-516', passed=True, receipt_sha256=expected_sha,
        counts=counts, public_replay=replay, maximum_correction_scaled_absolute_error=cancellation_absolute_error,
        symbolic_chains_verified=False, full_raw_audit_repeated=False, new_integrations=0,
        scope='Complete saved population and all reference comparisons; no independent IVP or exact-flow proof.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = audit(a.result, a.expected_sha256)
    with a.output.open('xb') as stream:
        stream.write(screen.encode(result))
    print(json.dumps(result, sort_keys=True))

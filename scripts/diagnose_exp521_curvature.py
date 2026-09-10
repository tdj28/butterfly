#!/usr/bin/env python3
"""Post-run even-c curvature diagnostic; never replace EXP-521's failed verdict."""
import argparse
import json
from pathlib import Path
import numpy as np
from butterfly._paired_startup import sha256, write_json
from scripts import exp519_fold_response as fold
from scripts import exp521_critical_response as controller

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'docs/experiments/receipts/EXP-519-fixed-c-fold-response-result.json': '92ff9159ca3de7794a481e9d682d02626b945495f3ad87e6c7d095137f0117ec',
    'docs/experiments/receipts/EXP-521-critical-periodic-response-result.json': '8bfc3ec343335af24514a4162b22e9a9d52499e49c5ee8140fa92c08697d499d'}


def calculate(anchor, points, correction, proposal):
    if [p['spec'] for p in points] != controller.stencil(proposal['c_response_center']):
        raise ValueError('complete prescribed stencil required')
    base = fold.values(anchor); values = [fold.values(p['vectors']) for p in points]
    centers = [(p['spec']['parameters']['c']-proposal['c_response_center']['c'])/.005 for p in points]
    coefficients = []
    for lo, hi in ((0, 1), (2, 3)):
        left, right = centers[lo], centers[hi]
        if left >= 0 or right <= 0 or left != -right:
            raise ValueError('symmetric realized c stencil required')
        coefficients.append(((values[lo]+values[hi])/2-base)/right**2)
    actual = fold.values(correction['vectors']); predicted = fold.values(proposal['predicted_vectors'])
    even = coefficients[1]*proposal['normalized_c_step']**2
    rows = []
    for key, coarse, fine, q, p, e in zip(fold.KEYS, *coefficients, actual, predicted, even, strict=True):
        linear_error = float(np.linalg.norm(q-p)); residual = float(np.linalg.norm(q-(p+e)))
        rows.append(dict(key=key, coarse_quadratic=coarse.tolist(), fine_quadratic=fine.tolist(),
            curvature_relative_disagreement=float(np.linalg.norm(coarse-fine)/max(float(np.linalg.norm(fine)), 1e-30)),
            linear_error=linear_error, after_even_c_error=residual,
            unexplained_fraction=residual/max(linear_error, 1e-30),
            observed_linear_error=(q-p).tolist(), even_c_contribution=e.tolist()))
    return rows


def diagnose():
    if any(sha256(ROOT/n) != h for n, h in SOURCES.items()): raise ValueError('fixed audited bytes differ')
    old, current = [json.loads((ROOT/n).read_bytes()) for n in SOURCES]
    r = current['result']
    if not old['passed'] or not current['passed'] or r['decision']['qualified'] is not False:
        raise ValueError('preserved audited failed predictor required')
    rows = calculate(old['result']['correction']['vectors'], r['points'], r['correction'], r['proposal'])
    return dict(experiment_id='EXP-521', analysis='post-run-even-c-curvature-diagnostic', sources=SOURCES,
        outcome_informed=True, changes_frozen_verdict=False, frozen_predictor_qualified=False,
        correction_used_to_fit_coefficients=False, variants=rows, new_integrations=0,
        generator_sha256=sha256(Path(__file__)),
        scope='Post-run explanation of linear-model error. No newly validated prediction, contact locus or Jones arrow.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('fresh diagnostic output required')
    result = diagnose(); write_json(args.output, result)
    print(json.dumps(dict(rows=len(result['variants']),
        maximum_unexplained_fraction=max(r['unexplained_fraction'] for r in result['variants']),
        maximum_curvature_disagreement=max(r['curvature_relative_disagreement'] for r in result['variants']),
        receipt_sha256=sha256(args.output))))

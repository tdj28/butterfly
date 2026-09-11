"""One fresh predictor/corrector using explicitly historical EXP-524 calibration."""
from scripts import exp523_refreshed_path as prior


def follow(source, fresh, measure):
    if not fresh['qualified'] or fresh['center'] != source['anchor']:
        raise ValueError('qualified calibration at exact initial anchor required')
    row = dict(index=0, anchor=source['anchor'], proposal=prior.proposal(source, fresh, 0),
        predictor=None, predictor_decision=None, refinement_source=None,
        refinement_proposal=None, refinement=None, refinement_decision=None,
        accepted=None, stop_reason=None)
    def take(spec, origin):
        point = measure(spec, origin)
        if point['spec'] != spec: raise ValueError('prescribed fresh measurement differs')
        return point
    proposed = row['proposal']
    if proposed is None:
        row['stop_reason'] = 'no-qualified-bounded-predictor'
    else:
        trial = take(proposed['spec'], source)
        verdict = prior.local.verdict(trial, source['vectors'], source['gaps'], proposed)
        row.update(predictor=trial, predictor_decision=verdict)
        if verdict['qualified'] and prior.tight(trial):
            row['accepted'] = trial['spec']
        else:
            permitted = (trial['qualified'] and all(r['qualified'] for r in verdict['gaps'])
                and all(r['improved'] for r in verdict['gaps'][::2])
                and max(r['distance'] for r in verdict['folds']) <= 1e-4)
            if not permitted:
                row['stop_reason'] = 'predictor-geometry-gap-or-progress-failed'
            else:
                origin = dict(prior.recenter(source, trial), a_response=fresh['a'], a_gaps=fresh['a_gaps'],
                    a_center=source['anchor']['a'], a_derivative_center=source['anchor'],
                    progress_anchor=source['anchor'], progress_gaps=source['gaps'])
                correction = prior.normal.proposal(origin)
                row['refinement_source'] = dict(prediction_center=origin['anchor'],
                    derivative_center=source['anchor'], progress_center=source['anchor'])
                if correction is None:
                    row['stop_reason'] = 'no-bounded-normal-correction'
                else:
                    correction['spec']['id'] = 'step-0-refinement'
                    refined = take(correction['spec'], origin)
                    decision = prior.normal.verdict(refined, origin, correction)
                    row.update(refinement_proposal=correction, refinement=refined, refinement_decision=decision)
                    if decision['qualified'] and prior.tight(refined): row['accepted'] = refined['spec']
                    else: row['stop_reason'] = 'normal-correction-failed'
    return dict(step=row, qualified=row['accepted'] is not None, maximum_steps=1,
        reused_calibration='EXP-524-all-eight-complete-points',
        symbolic_chains_verified=False, D_identified=False, exact_critical_locus_proved=False)


def scalar_check(result, source, calibration):
    """Check the single row with the original separate scalar formulas."""
    from scripts import audit_exp523_refreshed_path as audit
    row = dict(result['step'], a_points=calibration['points'][:4], c_points=calibration['points'][4:],
               response=calibration['response'])
    accepted = [] if row['accepted'] is None else [row['accepted']]
    # This is an internal scalar-check projection, NOT an EXP-523 completion
    # summary. The original auditor's two-step overall flag must remain false.
    audit.scalar_check(dict(steps=[row], accepted=accepted, completed_steps=len(accepted), qualified=False), source)
    if result['qualified'] != bool(accepted) or result['maximum_steps'] != 1:
        raise ValueError('single fresh step qualification differs')

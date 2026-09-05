#!/usr/bin/env python3
"""Compare a completed scalar control with Jones's source, without refitting it.

This separate, conditional comparison cannot influence root isolation. It
checks the structure of a hash-bound receipt, not its Sturm proofs anew. The
only fixed dictionary is C1s -> CDs at periods >=3; period 2 retains C1.
Increasing mu is compared with the ORIGINAL Figure 6 top-to-bottom order,
visually transcribed before target enumeration. No dictionary, root order,
time direction, cyclic rotation, or arrow is searched or inferred.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
import hashlib
from itertools import zip_longest
import json
import os
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "butterfly.quadratic-source-comparison.v1"
CONTROL_SCHEMA = "butterfly.quadratic-symbolic-control.v1"
SOURCE_SCHEMA = "butterfly.jones2012-source-transcription.v1"
TRANSCRIPTION_SHA256 = "6a5aba797473d40db9197d7a2ebe51195193f888613800584f406742376581da"
PAPER_SHA256 = "54b2a35bcfe50c5c2dc2f8ac1f3d3f98acbb2991dab7bc6e66cf61dc4b5ffb6f"
PERIODS = tuple(range(2, 8))
# This is a source-only visual transcription of the original PDF p.4, not
# the frozen JSON's node-array order or the modern redraw's compact layout.
# In particular, CD00111 precedes CD00110 in the period-7 source column.
SOURCE_TOP_TO_BOTTOM = {
    2: ("C1", "C2"),
    3: ("C21", "CD0"),
    4: ("CD01", "CD00"),
    5: ("CD011", "CD001", "CD000"),
    6: ("CD0111", "CD0010", "CD0011", "CD0001", "CD0000"),
    7: ("CD01111", "CD01101", "CD00101", "CD00111", "CD00110",
        "CD00010", "CD00011", "CD00001", "CD00000"),
}
OUT_OF_MODEL = {"C2", "C21"}
CLAIM_BOUNDARY = (
    "Finite combinatorial comparison under a proposed dictionary only; "
    "not a coordinate map, conjugacy, generating partition, second critical "
    "visit, Rossler orbit or center verification, or parameter-plane arrow test."
)


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def exact_fraction(value):
    if not isinstance(value, str):
        raise ValueError("exact interval endpoints must be rational strings")
    return Fraction(value)


def validate_source(source):
    if source.get("schema") != SOURCE_SCHEMA:
        raise ValueError("unsupported source transcription schema")
    identity = source["source"]
    if identity.get("paper_sha256") != PAPER_SHA256 or identity.get("arxiv_id") != "1201.4343v1":
        raise ValueError("source paper identity differs from the frozen Jones paper")
    nodes = source["figure6"]["nodes"]
    expected = {word for words in SOURCE_TOP_TO_BOTTOM.values() for word in words}
    if len(nodes) != len(expected) or {row["word"] for row in nodes} != expected:
        raise ValueError("all and only the frozen source nodes are required")
    for row in nodes:
        word = row["word"]
        if type(row["period"]) is not int or row["period"] != len(word):
            raise ValueError("source node period differs from its word length")
        if row.get("branch3_connection", False) is not (word in OUT_OF_MODEL):
            raise ValueError("source third-branch exclusions changed")


def validate_control(control):
    """Check receipt consistency; rely on the bound enumerator for its proof.

    Deliberately do not construct recurrence polynomials or discover roots
    here. This program must never be a route for feedback into enumeration.
    """
    if control.get("schema") != CONTROL_SCHEMA or control.get("passed") is not True:
        raise ValueError("a completed passing scalar-control receipt is required")
    if control.get("family") != "f_mu(x)=1-mu*x^2" or control.get("parameter_domain") != ["0", "2"]:
        raise ValueError("receipt uses a different scalar family or parameter domain")
    if control["protocol"]["periods"] != list(PERIODS):
        raise ValueError("comparison requires the complete frozen period-2-through-7 control")
    rows = control["period_results"]
    if [row["period"] for row in rows] != list(PERIODS):
        raise ValueError("receipt period rows must preserve the frozen complete order")
    for row in rows:
        period, cycles = row["period"], row["cycles"]
        if (type(period) is not int or row.get("passed") is not True
                or row.get("primitive_polynomial_square_free") is not True
                or type(row["complete_domain_root_count"]) is not int
                or row["complete_domain_root_count"] != len(cycles)):
            raise ValueError("incomplete scalar period certificate")
        previous_upper = None
        for cycle in cycles:
            word = cycle["critical_anchored_word"]
            if (type(cycle["period"]) is not int or cycle["period"] != period
                    or not isinstance(word, str) or len(word) != period
                    or not word.startswith("C1") or set(word[1:]) - {"0", "1"}):
                raise ValueError("cycle violates the source-free critical-anchored scalar alphabet")
            for flag in ("unique_root_certified", "exact_recurrence_factor_verified", "primitive_period_certified"):
                if cycle.get(flag) is not True:
                    raise ValueError("all exact scalar-cycle certificates must pass")
            interval = cycle["parameter_interval"]
            if not isinstance(interval, list) or len(interval) != 2:
                raise ValueError("parameter certificate must have two rational endpoints")
            lower, upper = map(exact_fraction, interval)
            if not 0 <= lower <= upper <= 2:
                raise ValueError("cycle interval falls outside the frozen parameter domain")
            if (previous_upper is not None and previous_upper >= lower):
                raise ValueError("root intervals must already be disjoint and increasing; no reorder is allowed")
            previous_upper = upper
            if exact_fraction(cycle["parameter_interval_width"]) != upper - lower:
                raise ValueError("cycle interval width is inconsistent")
            if cycle.get("exact_rational_root") is not (lower == upper):
                raise ValueError("rational-root flag is inconsistent")
            signs = cycle["noncritical_sign_intervals"]
            if len(signs) != period - 1:
                raise ValueError("every noncritical iterate must have a sign certificate")
            for iterate, (symbol, bounds) in enumerate(zip(word[1:], signs, strict=True), start=1):
                left, right = exact_fraction(bounds["lower"]), exact_fraction(bounds["upper"])
                expected_sign = 1 if symbol == "1" else -1
                if (type(bounds["iterate"]) is not int or bounds["iterate"] != iterate
                        or type(bounds["sign"]) is not int or bounds["sign"] != expected_sign
                        or left > right or (left <= 0 if expected_sign == 1 else right >= 0)):
                    raise ValueError("itinerary word disagrees with an intermediate sign certificate")
                if iterate == 1 and (left, right) != (Fraction(1), Fraction(1)):
                    raise ValueError("the first critical image must be exactly one")


def proposed_dictionary(word):
    if not isinstance(word, str) or len(word) < 2 or not word.startswith("C1") or set(word[1:]) - {"0", "1"}:
        raise ValueError("dictionary accepts only critical-anchored scalar C1s words")
    return word if len(word) == 2 else "CD" + word[2:]


def compare_control(control, source):
    validate_source(source)
    validate_control(control)
    period_rows, source_rows = [], []
    for scalar_row in control["period_results"]:
        period = scalar_row["period"]
        source_order = [word for word in SOURCE_TOP_TO_BOTTOM[period] if word not in OUT_OF_MODEL]
        cycle_rows = [{
            "root_index_in_increasing_mu_order": index,
            "parameter_interval": list(cycle["parameter_interval"]),
            "scalar_word": cycle["critical_anchored_word"],
            "proposed_source_word": proposed_dictionary(cycle["critical_anchored_word"]),
            "dictionary": "retain native C1" if period == 2 else "C1s -> CDs",
            "membership": "matched" if proposed_dictionary(cycle["critical_anchored_word"]) in source_order else "extra",
        } for index, cycle in enumerate(scalar_row["cycles"])]
        proposed_order = [row["proposed_source_word"] for row in cycle_rows]
        counts = Counter(proposed_order)
        missing = [word for word in source_order if not counts[word]]
        extra = [row for row in cycle_rows if row["membership"] == "extra"]
        positions = [{"position_top_to_bottom_or_increasing_mu": index,
                      "scalar_mapped_word": computed, "source_word": historical,
                      "match": computed == historical}
                     for index, (computed, historical) in enumerate(zip_longest(proposed_order, source_order))]
        period_rows.append({
            "period": period, "cycles": cycle_rows,
            "source_top_to_bottom_words": source_order,
            "increasing_mu_proposed_words": proposed_order,
            "missing_source_words": missing, "extra_scalar_cycles": extra,
            "duplicate_proposed_word_counts": {word: count for word, count in counts.items() if count > 1},
            "conditional_set_match": set(proposed_order) == set(source_order),
            "conditional_multiset_match": counts == Counter(source_order),
            "conditional_order_match": proposed_order == source_order,
            "ordered_positions": positions,
        })
        for word in SOURCE_TOP_TO_BOTTOM[period]:
            source_rows.append({"period": period, "source_word": word,
                                "status": "out_of_model" if word in OUT_OF_MODEL else "matched" if counts[word] else "missing",
                                "matching_scalar_cycle_count": counts[word],
                                **({"reason": "source third-branch node is outside this unimodal scalar model"}
                                   if word in OUT_OF_MODEL else {})})
    return {
        "schema": SCHEMA, "comparison_completed": True,
        "control_experiment_id": control.get("experiment_id"),
        "conditional_multiset_match": all(row["conditional_multiset_match"] for row in period_rows),
        "conditional_order_match": all(row["conditional_order_match"] for row in period_rows),
        "period_results": period_rows, "all_source_nodes": source_rows,
        "source_order_provenance": "visual top-to-bottom transcription of original Jones 1201.4343v1 PDF page 4 Figure 6, frozen before target enumeration; not JSON node-array order or modern redraw coordinates",
        "comparison_convention": {"period_2": "C1 retained unchanged; C2 outside model",
                                  "periods_3_through_7": "C1s -> CDs; C21 outside model",
                                  "order": "increasing mu versus original source column top-to-bottom",
                                  "order_direction_selected_from_outcome": False,
                                  "dictionary_search_performed": False},
        "receipt_validation": "structural consistency and declared input hash; relies on the input enumerator for exact recurrence/Sturm certificates; no independent proof replay",
        "source_targets_previously_known": True,
        "rossler_nodes_verified": False, "source_arrows_tested": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_exclusive(path, document):
    payload = (json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def read_json(payload):
    def reject_constant(_value):
        raise ValueError("nonfinite JSON constants are not permitted")
    return json.loads(payload, parse_constant=reject_constant)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--control-sha256", required=True)
    parser.add_argument("--source", type=Path, default=ROOT / "experiments/source-transcriptions/jones2012-figures-2-and-6.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if os.path.lexists(args.output):
        parser.error("output already exists; choose a new receipt path")
    result = {"schema": SCHEMA, "comparison_completed": False, "claim_boundary": CLAIM_BOUNDARY,
              "created_utc": datetime.now(UTC).isoformat(),
              "comparison_script_sha256": sha256_bytes(Path(__file__).read_bytes())}
    try:
        if not re.fullmatch(r"[0-9a-f]{64}", args.control_sha256):
            raise ValueError("a lowercase SHA-256 of the completed control receipt is required")
        raw_control, raw_source = args.control.read_bytes(), args.source.read_bytes()
        result["input_hashes"] = {"scalar_control": sha256_bytes(raw_control),
                                  "source_transcription": sha256_bytes(raw_source),
                                  "source_paper_declared": PAPER_SHA256}
        if result["input_hashes"]["scalar_control"] != args.control_sha256:
            raise ValueError("scalar-control receipt hash mismatch")
        if result["input_hashes"]["source_transcription"] != TRANSCRIPTION_SHA256:
            raise ValueError("source-transcription hash mismatch")
        result.update(compare_control(read_json(raw_control), read_json(raw_source)))
    except (ValueError, TypeError, KeyError, ArithmeticError) as error:
        result["failure"] = {"kind": type(error).__name__, "message": str(error)}
    except OSError:
        result["failure"] = {"kind": "InputIOError", "message": "unable to read declared inputs"}
    write_exclusive(args.output, result)
    print(json.dumps({key: result.get(key) for key in ("comparison_completed", "conditional_multiset_match", "conditional_order_match", "failure")}, sort_keys=True))
    # A scientific mismatch is a completed comparison, not an execution error.
    return 0 if result["comparison_completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

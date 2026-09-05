#!/usr/bin/env python3
"""Render EXP-478 TeX and CSV evidence from fixed receipts; --verify is read-only.

Every table value is derived from the exact-control receipt and a replay of
the separately frozen comparison. Hash and source-identity gates precede any
rendering. This is a deterministic presentation check, not another root
enumeration or an independent proof of the input Sturm certificates.
"""

from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import sys

# Support both `python scripts/this_file.py` and package imports by pytest.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import compare_quadratic_source_words as comparison


SCHEMA = "butterfly.quadratic-control-table-provenance.v1"
FROZEN_COMMIT = "f4b2ea13c60395713911240b0fbf0ce469850cc4"
FROZEN_TREE = "983848a7559e06770b3d2796fd8c7bc4571ee06f"
CONTROL_PATH = "docs/experiments/receipts/EXP-478-quadratic-control.json"
COMPARISON_PATH = "docs/experiments/receipts/EXP-478-source-comparison.json"
SOURCE_PATH = "experiments/source-transcriptions/jones2012-figures-2-and-6.json"
MANIFEST_PATH = "experiments/manifests/EXP-478-quadratic-symbolic-control.json"
ENUMERATOR_PATH = "scripts/verify_quadratic_symbolic_control.py"
COMPARATOR_PATH = "scripts/compare_quadratic_source_words.py"
TABLE_PATH = "paper/tables/quadratic-symbolic-control.tex"
WORDS_PATH = "paper/tables/quadratic-symbolic-words.csv"
PROVENANCE_PATH = "paper/tables/quadratic-symbolic-control.provenance.json"
WORD_COLUMNS = (
    "period", "root_index_zero_based", "mu_midpoint_decimal_approx",
    "mu_lower_exact", "mu_upper_exact", "native_word", "mapped_source_word",
    "conditional_membership_match",
)
MIDPOINT_DECIMAL_PLACES = 16
FROZEN_HASHES = {
    CONTROL_PATH: "6d46529e6ae6b53f6796848855f1c01d6cf936399da6455fe6ef12e6140b925e",
    COMPARISON_PATH: "90031254a6f0ede05f77ff6d5cc2f617046b159b118dcc9fcba1889d2ecf31ae",
    SOURCE_PATH: "6a5aba797473d40db9197d7a2ebe51195193f888613800584f406742376581da",
    MANIFEST_PATH: "afc851204f68b3e248bb9eb980332e42252e46a4991ac308340ce80ce5b75781",
    ENUMERATOR_PATH: "221dc4635b4b6a7fe27b202299e182ca2f785619fcaf27b0fc837e2d423789c4",
    COMPARATOR_PATH: "4d1312518874d7bdda724b45bcd75ed0bc8830d4c13a5f1652837ed65c7a2373",
    "uv.lock": "a1118c46febbce18e7172acfeaa804909792185d3c48fae258044b82e145eeff",
}


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def load_frozen_inputs(root=ROOT):
    root = Path(root)
    raw = {}
    for name, expected in FROZEN_HASHES.items():
        payload = (root / name).read_bytes()
        if sha256_bytes(payload) != expected:
            raise ValueError(f"frozen input SHA-256 mismatch: {name}")
        raw[name] = payload
    control, compared, source, manifest = (
        comparison.read_json(raw[name]) for name in (CONTROL_PATH, COMPARISON_PATH, SOURCE_PATH, MANIFEST_PATH)
    )
    provenance = control["source"]
    if (provenance != control["source_after"] or provenance.get("dirty") is not False
            or provenance.get("commit") != FROZEN_COMMIT or provenance.get("tree") != FROZEN_TREE):
        raise ValueError("scalar control does not retain its clean frozen source identity")
    if (provenance.get("script_sha256") != FROZEN_HASHES[ENUMERATOR_PATH]
            or provenance.get("uv_lock_sha256") != FROZEN_HASHES["uv.lock"]
            or control.get("manifest_sha256") != FROZEN_HASHES[MANIFEST_PATH]
            or control.get("protocol") != manifest):
        raise ValueError("scalar control provenance does not bind the frozen runtime and protocol")
    if (compared.get("comparison_script_sha256") != FROZEN_HASHES[COMPARATOR_PATH]
            or compared.get("input_hashes") != {
                "scalar_control": FROZEN_HASHES[CONTROL_PATH],
                "source_transcription": FROZEN_HASHES[SOURCE_PATH],
                "source_paper_declared": comparison.PAPER_SHA256,
            }):
        raise ValueError("comparison does not bind its declared scalar receipt, source, and script")
    return control, compared, source


def derive_rows(control, compared, source):
    """Rederive all counts and comparisons, rejecting inconsistent snapshots."""
    derived = comparison.compare_control(control, source)
    for key, expected in derived.items():
        if compared.get(key) != expected:
            raise ValueError(f"stored comparison differs from independent presentation replay: {key}")
    rows = []
    for scalar, matched in zip(control["period_results"], derived["period_results"], strict=True):
        rows.append({
            "period": scalar["period"],
            "scalar_cycle_count": len(scalar["cycles"]),
            "comparable_source_node_count": len(matched["source_top_to_bottom_words"]),
            "conditional_set_match": matched["conditional_set_match"],
            "conditional_order_match": matched["conditional_order_match"],
        })
    return rows, derived


def render_table(rows):
    lines = [
        "% Generated by scripts/render_quadratic_control_table.py; do not hand-edit.",
        r"\begin{table}[htbp]",
        r"\centering",
        r"\small",
        r"\begin{tabular}{rrrrr}",
        r"\toprule",
        r"Period & Scalar cycles & Source nodes & Set match & Order match \\",
        r"\midrule",
    ]
    for row in rows:
        fields = (str(row["period"]), str(row["scalar_cycle_count"]),
                  str(row["comparable_source_node_count"]),
                  "Yes" if row["conditional_set_match"] else "No",
                  "Yes" if row["conditional_order_match"] else "No")
        lines.append(" & ".join(fields) + r" \\")
    lines.extend((
        r"\bottomrule",
        r"\end{tabular}",
        r"\caption{Exact quadratic-map control (EXP-478): primitive superstable cycles of $f_\mu(x)=1-\mu x^2$ on $0\leq\mu\leq2$. Matches are conditional on $C1s\mapsto CDs$ for periods at least three, with $C1$ retained at period two; order means increasing $\mu$ versus the original Figure~6 columns from top to bottom. The third-branch source nodes $C2$ and $C21$ are outside this model. No R\"ossler orbit or connecting arrow is verified by this table. \href{https://github.com/tdj28/butterfly/blob/main/docs/experiments/EXP-478-quadratic-symbolic-control.md}{Protocol and exact receipts}.}",
        r"\label{tab:quadratic-symbolic-control}",
        r"\end{table}",
    ))
    return ("\n".join(lines) + "\n").encode()


def approximate_midpoint(lower, upper):
    """Exact rational rounding to a display decimal, never a root certificate.

    Integer divmod implements nearest/ties-to-even without binary64 or a
    context-dependent Decimal intermediate. The display may lie outside its
    much narrower exact root enclosure; both exact endpoints are exported.
    """
    midpoint = (Fraction(lower) + Fraction(upper)) / 2
    if midpoint < 0:
        raise ValueError("this frozen scalar domain has no negative parameters")
    scale = 10 ** MIDPOINT_DECIMAL_PLACES
    rounded, remainder = divmod(midpoint.numerator * scale, midpoint.denominator)
    if 2 * remainder > midpoint.denominator or (2 * remainder == midpoint.denominator and rounded % 2):
        rounded += 1
    whole, fractional = divmod(rounded, scale)
    return f"{whole}.{fractional:0{MIDPOINT_DECIMAL_PLACES}d}"


def render_word_csv(control, derived):
    """Preserve all input cycles in period/increasing-mu order with exact bounds."""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=WORD_COLUMNS, lineterminator="\n")
    writer.writeheader()
    count = 0
    for scalar, compared in zip(control["period_results"], derived["period_results"], strict=True):
        for index, (cycle, matched) in enumerate(zip(scalar["cycles"], compared["cycles"], strict=True)):
            lower, upper = cycle["parameter_interval"]
            writer.writerow({
                "period": scalar["period"], "root_index_zero_based": index,
                "mu_midpoint_decimal_approx": approximate_midpoint(lower, upper),
                "mu_lower_exact": lower, "mu_upper_exact": upper,
                "native_word": cycle["critical_anchored_word"],
                "mapped_source_word": matched["proposed_source_word"],
                "conditional_membership_match": "true" if matched["membership"] == "matched" else "false",
            })
            count += 1
    return stream.getvalue().encode(), count


def build_artifacts(root=ROOT):
    control, compared, source = load_frozen_inputs(root)
    rows, derived = derive_rows(control, compared, source)
    table = render_table(rows)
    words, word_count = render_word_csv(control, derived)
    provenance = {
        "schema": SCHEMA,
        "generator": {"path": "scripts/render_quadratic_control_table.py",
                      "sha256": sha256_bytes(Path(__file__).read_bytes())},
        "input_sha256": dict(FROZEN_HASHES),
        "scalar_control_source_commit": FROZEN_COMMIT,
        "scalar_control_source_tree": FROZEN_TREE,
        "source_identity_check": "clean before/after receipt identity and frozen content hashes; publication of the declared commit is recorded by the experiment, not queried over the network here",
        "output": {"path": TABLE_PATH, "sha256": sha256_bytes(table), "bytes": len(table)},
        "word_csv": {
            "path": WORDS_PATH, "sha256": sha256_bytes(words), "bytes": len(words),
            "row_count": word_count, "columns": list(WORD_COLUMNS),
            "row_order": "increasing period, then strictly increasing mu within period; zero-based root index resets each period",
            "midpoint_display_decimal_places": MIDPOINT_DECIMAL_PLACES,
            "midpoint_display_rounding": "exact integer nearest/ties-to-even rounding of the rational enclosure midpoint",
            "midpoint_display_is_root_certificate": False,
            "exact_bounds_retained_verbatim": True,
            "conditional_membership_match_scope": "membership after the predeclared scalar-to-source dictionary, not Rossler verification",
        },
        "derived_rows": rows,
        "total_scalar_cycles": sum(row["scalar_cycle_count"] for row in rows),
        "total_comparable_source_nodes": sum(row["comparable_source_node_count"] for row in rows),
        "out_of_model_source_words": [row["source_word"] for row in derived["all_source_nodes"] if row["status"] == "out_of_model"],
        "comparison_replayed_without_root_reordering": True,
        "root_enumeration_rerun": False,
        "root_proof_independently_replayed": False,
        "rossler_nodes_verified": False,
        "source_arrows_tested": False,
        "claim_boundary": comparison.CLAIM_BOUNDARY,
    }
    return table, words, (json.dumps(provenance, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="verify existing output bytes without writing")
    args = parser.parse_args(argv)
    try:
        table, words, provenance = build_artifacts()
        outputs = ((ROOT / TABLE_PATH, table), (ROOT / WORDS_PATH, words),
                   (ROOT / PROVENANCE_PATH, provenance))
        if args.verify:
            for path, expected in outputs:
                if path.read_bytes() != expected:
                    raise ValueError(f"generated output is stale: {path.name}")
        else:
            for path, payload in outputs:
                if path.is_symlink():
                    raise ValueError("generated output must not overwrite a symlink")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"quadratic table {'verification' if args.verify else 'generation'} failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print("quadratic control table verified" if args.verify else "quadratic control table generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

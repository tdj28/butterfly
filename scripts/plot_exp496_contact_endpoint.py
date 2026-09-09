#!/usr/bin/env python3
"""Plot audited endpoint observations, never an uncomputed interpolating path."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from butterfly._paired_startup import sha256, write_json
from scripts import run_exp496_contact_endpoint as run
from scripts import audit_exp496_contact_endpoint as audit

STEM = "EXP-496-contact-endpoint"
COLORS = ["#007f86", "#4698cc", "#ad593d", "#93649c"]


def validate(result):
    p, data, folds, cycles = run.load_inputs()
    if (not result["passed"] or result["experiment_id"] != "EXP-496" or result["ledger"] != data["ledger"]
            or [r["id"] for r in result["candidates"]] != [c["id"] for c in data["candidates"]]):
        raise ValueError("audited complete ledger required")
    if audit.reconstruct_contact(result["candidates"], data, folds, cycles, p) != result["contact"]:
        raise ValueError("scalar figure-data replay differs")
    return p, data


def build(path, expected, output):
    if sha256(path) != expected:
        raise ValueError("audited input anchor differs")
    result = json.loads(path.read_bytes())
    p, data = validate(result)
    plt.rcParams.update({"svg.hashsalt": STEM})
    output.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), layout="constrained")
    fig.suptitle("Is there a critical-contact interval?", fontsize=19, fontweight="bold")
    for col, case in enumerate(result["contact"]["cases"]):
        rows = [r for r in result["contact"]["rows"] if r["case"] == case["case"]]
        candidates = [c for c in data["candidates"] if c["case"] == case["case"]]
        upper_a, lower_a = candidates[0]["parent_parameters"]["a"], candidates[0]["parameters"]["a"]
        top, bottom = axes[:, col]
        top.axhline(0, color="#555555", linewidth=1)
        for i, row in enumerate(rows):
            label = f"depth {candidates[i]['count']-1}, direction {i % 2}"
            vs = row["variants"]
            if vs:
                for a, key, marker in ((lower_a, "lower_signed_residual", "o"),
                                       (upper_a, "upper_signed_residual", "s")):
                    values = [v[key] for v in vs]
                    top.scatter([a]*len(values), values, s=35, marker=marker,
                                color=COLORS[i], alpha=.75, label=label if marker == "o" else None)
                    top.plot([a, a], [min(values), max(values)], color=COLORS[i], linewidth=2)
                distances = [v["pair_state_distance"][3]/p["primary_radius"] for v in vs]
                bottom.scatter([i]*len(distances), distances, color=COLORS[i], s=38)
                bottom.plot([i, i], [min(distances), max(distances)], color=COLORS[i], linewidth=2)
            else:
                bottom.text(i, .5, "fold\nunresolved", ha="center", va="center", color=COLORS[i], fontsize=10)
        top.set_title(f"a = {lower_a:.5f} / {upper_a:.5f}\n{case['status'].replace('-', ' ')}", fontsize=12)
        top.set_xticks([lower_a, upper_a], [f"{lower_a:.5f}\nlower", f"{upper_a:.5f}\noriginal"])
        top.set_xlim(lower_a-.00006, upper_a+.00006)
        top.set_ylabel("Signed event-3 input-x residual / 15")
        top.set_xlabel("a at b = 0.2, c = 7.212; endpoints only")
        if any(r["variants"] for r in rows):
            top.legend(fontsize=8, loc="best")
        else:
            top.text(.5, .5, "No qualified lower fold", ha="center", transform=top.transAxes)
        bottom.axhline(1, color="#333333", linestyle="--", label="primary proximity limit")
        bottom.set_yscale("log")
        bottom.set_ylim(bottom=.05)
        bottom.set_xlim(-.5, 3.5)
        bottom.set_xticks(range(4), ["d4 / v0", "d4 / v1", "d8 / v0", "d8 / v1"])
        bottom.set_ylabel("Lower endpoint full-state pair distance / 1e−4")
        bottom.set_xlabel("All four curve representations; both solvers and windows")
        bottom.legend(fontsize=9, loc="best")
        for ax in (top, bottom):
            ax.grid(alpha=.16)
            ax.spines[["top", "right"]].set_visible(False)
    fig.supxlabel("8 selected + 2 duplicate representations + 16 ineligible = all 26 parent candidates.\n"
                  "A sign change nominates an interval; it does not prove contact, continuity, C/D, or a Jones arrow.", fontsize=10)
    for extension in ("svg", "png"):
        fig.savefig(output/f"{STEM}.{extension}", dpi=300, metadata={"Date": None} if extension == "svg" else None)
    plt.close(fig)
    receipt_path = output/f"{STEM}.receipt.json"
    write_json(receipt_path, dict(experiment_id="EXP-496", source_data_sha256=expected,
        source_data_path=path.resolve().relative_to(run.ROOT).as_posix(),
        generator_sha256=sha256(Path(__file__)), audit_source_sha256=sha256(Path(audit.__file__)),
        ledger=26, selected=8, variants_per_qualified_representation=4, primary_event=3,
        exact_contact_verified=False, symbolic_chains_verified=False,
        source_commit=result["source_commit"], summary_sha256=result["summary_sha256"],
        matplotlib=matplotlib.__version__, derived_contact=result["contact"],
        interval_semantics="Observed solver/window range, not a statistical confidence interval; no interpolated trajectory.",
        accessibility="Endpoint shapes, parameter labels, four separate lower-panel positions and explicit failure text supplement colors.",
        alt_text="Both cases show signed contact residuals at two parameter endpoints and full-state event-3 pair mismatch at the lower endpoint for all four curve representations. Unqualified folds are explicitly marked; no path between endpoints is computed.",
        outputs={f"{STEM}.{e}": dict(sha256=sha256(output/f"{STEM}.{e}"),
                                   bytes=(output/f"{STEM}.{e}").stat().st_size) for e in ("svg", "png")}))
    write_json(output/f"{STEM}.index.json", dict(receipts={receipt_path.name:
        dict(bytes=receipt_path.stat().st_size, sha256=sha256(receipt_path))}))


def verify(output):
    name = f"{STEM}.receipt.json"
    index = json.loads((output/f"{STEM}.index.json").read_bytes())
    if set(index["receipts"]) != {name}:
        raise ValueError("figure receipt index differs")
    expected = index["receipts"][name]
    if sha256(output/name) != expected["sha256"] or (output/name).stat().st_size != expected["bytes"]:
        raise ValueError("figure receipt differs")
    r = json.loads((output/name).read_bytes())
    source = run.ROOT/r["source_data_path"]
    if (sha256(source) != r["source_data_sha256"] or sha256(Path(__file__)) != r["generator_sha256"]
            or sha256(Path(audit.__file__)) != r["audit_source_sha256"]):
        raise ValueError("figure source drift")
    result = json.loads(source.read_bytes())
    validate(result)
    if result["contact"] != r["derived_contact"]:
        raise ValueError("plotted data differ")
    for name, expected in r["outputs"].items():
        if sha256(output/name) != expected["sha256"] or (output/name).stat().st_size != expected["bytes"]:
            raise ValueError("figure output differs")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--output-dir", type=Path, required=True)
    a = parser.parse_args()
    if a.verify_only:
        print(json.dumps(dict(verified=verify(a.output_dir))))
    else:
        if not a.result or not a.expected_sha256:
            parser.error("build requires result and expected SHA")
        build(a.result, a.expected_sha256, a.output_dir)


if __name__ == "__main__":
    main()

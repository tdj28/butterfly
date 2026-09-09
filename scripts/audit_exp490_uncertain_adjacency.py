#!/usr/bin/env python3
"""Read-only impact check for EXP-491's stricter uncertain-extremum guard."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from butterfly._paired_startup import sha256,write_json
from scripts import run_exp491_event_sheet_probe as run


def audit(directory):
    anchor = "41fe7b8e5346a97946c2bb51400fb1109d0b5a29d682653494b36fd2962b345e"
    if sha256(directory/"summary.json") != anchor:
        raise ValueError("EXP-490 completed summary differs")
    summary = json.loads((directory/"summary.json").read_bytes())
    candidates,_ = run.load(json.loads(run.PLAN.read_bytes()))
    rows,files = [],{}
    for c in candidates:
        for method in ("DOP853","Radau"):
            name = f"{c['id']}--{method}.json"
            digest = sha256(directory/name)
            if digest != summary["files"][name]["sha256"]:
                raise ValueError("historical profile differs")
            files[name] = digest
            saved = json.loads((directory/name).read_bytes())
            for census in saved["censuses"]:
                r = census["report"]
                prefix = [e for e in r["reconstructed"] if e["accepted"]][:c["count"]]
                adjacent = any(t["time"] in e["bracket"] for t in r["uncertain_extrema"] for e in prefix)
                old = len(prefix) != c["count"] or any(t["time"] <= prefix[-1]["time"] for t in r["uncertain_extrema"])
                rows.append(dict(candidate_id=c["id"],method=method,offset=census["offset"],
                    uncertain_extrema=len(r["uncertain_extrema"]),adjacent_uncertainty=adjacent,
                    old_uncertainty_or_missing_gate=old,newly_rejected=bool(adjacent and not old)))
    if len(files) != 52 or len(rows) != 72:
        raise ValueError("complete historical census matrix required")
    return dict(experiment_id="EXP-491",kind="read-only-EXP-490-uncertainty-impact",summary_sha256=anchor,
        script_sha256=sha256(Path(__file__)),files=files,censuses=rows,
        newly_rejected=sum(r["newly_rejected"] for r in rows),
        boundary="Only the new adjacent-uncertainty guard is audited here; no reintegration or broader legacy certification.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    result = audit(args.run)
    write_json(args.output,result)
    print(json.dumps(dict(censuses=len(result["censuses"]),newly_rejected=result["newly_rejected"])))

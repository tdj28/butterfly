#!/usr/bin/env python3
"""Release/replay all EXP-493 local-window polygons and compact decisions."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
import numpy as np
from butterfly._paired_startup import sha256,write_json
from butterfly.projected_winding import compare_polygons
from scripts import analyze_exp493_projected_inner_turn as run

SUMMARY_SHA = "b9a6ec1834dfaa4de51fd260ac2da26184aa6c97ba964532e72c639af62daf2a"
BINDING_SHA = "ce948ffa61ac3f27f176037c59d7d48a92a35bbb74d3ff407ea0be39f1e45ac2"
ARCHIVE = "EXP-493-projected-inner-turn-data.json.gz"
RECEIPT = "EXP-493-projected-inner-turn-result.json"


def canonical(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()


def same_numeric(actual,stored):
    """Portable replay roundoff only; identities and gate decisions are exact."""
    if isinstance(actual,dict) and isinstance(stored,dict):
        return actual.keys() == stored.keys() and all(same_numeric(actual[k],stored[k]) for k in actual)
    if isinstance(actual,list) and isinstance(stored,list):
        return len(actual) == len(stored) and all(same_numeric(a,b) for a,b in zip(actual,stored,strict=True))
    if isinstance(actual,(float,np.floating)) and isinstance(stored,(float,np.floating)):
        return bool(np.isclose(actual,stored,rtol=1e-12,atol=1e-13,equal_nan=False))
    return type(actual) is type(stored) and actual == stored


def ray_index(q):
    """Independent signed intersections of a polygon with the negative ray.

    Half-open handling matches atan2's positive-zero endpoint convention.
    This is checked after angle accumulation, not used to construct it.
    """
    q = np.asarray(q)
    count = 0
    for a,b in zip(q[:-1],q[1:],strict=True):
        direction = 1 if a[1] >= 0 > b[1] else (-1 if a[1] < 0 <= b[1] else 0)
        if direction:
            x = a[0]+(b[0]-a[0])*a[1]/(a[1]-b[1])
            if x < 0:
                count += direction
    return count


def derive(saved,binding):
    if hashlib.sha256(canonical(saved)).hexdigest() != SUMMARY_SHA or hashlib.sha256(canonical(binding)).hexdigest() != BINDING_SHA:
        raise ValueError("completed analysis/binding anchors differ")
    if binding["source_commit"] != "972ca987d10b420d8d136151434f77d408c222a4" or binding["plan_sha256"] != sha256(run.PLAN) or binding["sources"] != {s:sha256(ROOT/s) for s in run.SOURCES}:
        raise ValueError("executed source differs")
    p = run.load_plan()
    table,candidates = run.parent.run.load(json.loads(run.parent.run.PLAN.read_bytes()))
    c_by_id = {c["id"]:c for c in candidates}
    parent = json.loads((ROOT/p["parent_receipt_path"]).read_bytes())
    if sha256(ROOT/p["parent_receipt_path"]) != p["parent_receipt_sha256"]:
        raise ValueError("parent result differs")
    prior = {r["id"]:r for r in parent["intervals"]}
    if saved["experiment_id"] != "EXP-493" or saved["status"] != "complete-saved-data-analysis" or saved["new_integrations"] != 0 or len(saved["intervals"]) != 26:
        raise ValueError("complete saved-data matrix required")
    compact,checks = [],0
    for r,c in zip(saved["intervals"],table["intervals"],strict=True):
        if r["id"] != c["id"] or r["family_id"] != c["family_id"] or r["selection_status"] != c["status"]:
            raise ValueError("input matrix differs")
        row = {k:v for k,v in r.items() if k != "profiles"}
        row["profiles"] = []
        if c["status"] != "nominated":
            if r["profiles"] or r["analysis"] is not None or r["status"] != "not-selected":
                raise ValueError("unselected interval changed")
            compact.append(row)
            continue
        parent_analysis = prior[r["id"]]["analysis"]
        if r["parent_boundary_qualified"] != parent_analysis["qualified"]:
            raise ValueError("parent failure was changed")
        if not parent_analysis["roots"]["eligible"]:
            if r["profiles"] or r["analysis"] is not None or r["status"] != "unresolved-parent-root-gate":
                raise ValueError("skipped parent changed")
            compact.append(row)
            continue
        if run.compare(r["profiles"],c_by_id[r["id"]],p,parent_analysis["qualified"]) != r["analysis"] or r["status"] != ("qualified" if r["analysis"]["qualified"] else "unresolved"):
            raise ValueError("full geometric matrix replay differs")
        for side in r["profiles"]:
            reduced = dict(dose=side["dose"],u=side["u"],profiles=[])
            for v in side["profiles"]:
                nodes = {k:[(q[0],np.asarray(q[1:])) for q in values] for k,values in v["polygons"].items()}
                if set(nodes) != {"raw","extrema_augmented","midpoint_enriched"}:
                    raise ValueError("complete polygon representations required")
                replay = compare_polygons(nodes,v["equilibrium"][:2],**{k:p[k] for k in ("radius_floor","angle_ceiling","angle_agreement")})
                if not same_numeric(replay,v["geometry"]):
                    raise ValueError("public polygon geometry replay differs")
                index = ray_index(np.array([q[:2]-v["equilibrium"][:2] for _,q in nodes["midpoint_enriched"]]))
                if index != replay["measures"]["midpoint_enriched"]["cut_index"]:
                    raise ValueError("independent polygon-ray count differs")
                event_match = index == v["local_negative_crossings"]
                if v["event_index_agrees"] != event_match or v["qualified"] != (replay["qualified"] and event_match):
                    raise ValueError("event/geometry decision differs")
                reduced["profiles"].append(dict({k:x for k,x in v.items() if k != "polygons"},
                    polygon_sha256=hashlib.sha256(canonical(v["polygons"])).hexdigest(),independent_polygon_ray_index=index))
                checks += 1
            row["profiles"].append(reduced)
        compact.append(row)
    if checks != 128:
        raise ValueError("all 128 realized profiles must be replayed")
    return dict({k:v for k,v in saved.items() if k != "intervals"},intervals=compact,binding=binding,
        completed_analysis_sha256=SUMMARY_SHA,polygon_replays=checks,
        public_scope="Complete local-window polygons and compact geometric decisions; not the full-horizon EXP-492 variational trajectories or a new integration validation.")


def export(directory,output):
    data = (directory/"summary.json").read_bytes()
    binding = json.loads((directory/"binding.json").read_bytes())
    if hashlib.sha256(data).hexdigest() != SUMMARY_SHA:
        raise ValueError("completed bytes differ")
    result = derive(json.loads(data),binding)
    output.mkdir(parents=True,exist_ok=False)
    with (output/ARCHIVE).open("xb") as stream:
        stream.write(gzip.compress(data,mtime=0))
    result.update(archive=dict(path=ARCHIVE,sha256=sha256(output/ARCHIVE),bytes=(output/ARCHIVE).stat().st_size,
        uncompressed_sha256=SUMMARY_SHA,uncompressed_bytes=len(data)),export_code=dict(path="scripts/export_exp493_projected_inner_turn.py",sha256=sha256(Path(__file__))))
    write_json(output/RECEIPT,result)


def verify(directory):
    receipt = json.loads((directory/RECEIPT).read_bytes())
    archive = receipt["archive"]
    if archive["path"] != ARCHIVE or sha256(directory/ARCHIVE) != archive["sha256"] or (directory/ARCHIVE).stat().st_size != archive["bytes"] or receipt["export_code"] != dict(path="scripts/export_exp493_projected_inner_turn.py",sha256=sha256(Path(__file__))):
        raise ValueError("archive/export source differs")
    data = gzip.decompress((directory/ARCHIVE).read_bytes())
    if hashlib.sha256(data).hexdigest() != SUMMARY_SHA or len(data) != archive["uncompressed_bytes"] or archive["uncompressed_sha256"] != SUMMARY_SHA:
        raise ValueError("released data differ")
    expected = derive(json.loads(data),receipt["binding"])
    if expected != {k:v for k,v in receipt.items() if k not in ("archive","export_code")}:
        raise ValueError("compact public result differs")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--verify-only",action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        export(args.run,args.output_dir)
    verify(args.output_dir)
    print("All 128 public polygon replays and independent ray-count checks passed")

#!/usr/bin/env python3
"""Bounded static caller inventory; does not reclassify any historical result."""
import argparse
import ast
import json
from pathlib import Path
import subprocess

from butterfly._paired_startup import sha256,write_json

ROOT = Path(__file__).resolve().parents[1]
LEGACY = "python/butterfly/return_map.py"


def affected_functions(tree):
    functions = {n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    edges = {name:{n.func.id for n in ast.walk(node) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
             for name,node in functions.items()}
    affected = {"_critical_points"}
    while True:
        expanded = affected|{name for name,calls in edges.items() if calls & affected}
        if expanded == affected:
            return sorted(affected)
        affected = expanded


def calls(tree,names):
    """Resolve explicit import aliases; dynamic imports/assignments are outside scope."""
    aliases,modules = {},set()
    for n in ast.walk(tree):
        if isinstance(n,ast.ImportFrom) and n.module in ("butterfly","butterfly.return_map"):
            for a in n.names:
                if a.name in names:
                    aliases[a.asname or a.name] = a.name
                if n.module == "butterfly" and a.name == "return_map":
                    modules.add(a.asname or a.name)
        elif isinstance(n,ast.Import):
            for a in n.names:
                if a.name in ("butterfly","butterfly.return_map"):
                    modules.add(a.asname or a.name)
    output = []
    for n in ast.walk(tree):
        if not isinstance(n,ast.Call):
            continue
        name = aliases.get(n.func.id) if isinstance(n.func,ast.Name) else None
        if isinstance(n.func,ast.Attribute) and n.func.attr in names:
            if ast.unparse(n.func.value) in modules:
                name = n.func.attr
        if name:
            output.append(dict(line=n.lineno,function=name))
    return sorted(output,key=lambda n:(n["line"],n["function"]))


def inventory():
    paths = sorted(filter(None,subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")))
    affected = affected_functions(ast.parse((ROOT/LEGACY).read_text()))
    # This function consumes branch results without calling the fitting helper.
    consumers = ["infer_return_map_branches_coverage_censored"]
    documents = {p:(ROOT/p).read_text() for p in paths
        if p.startswith(("docs/experiments/","experiments/manifests/")) and p.endswith((".md",".json"))}
    manifests = []
    for name,text in documents.items():
        if name.startswith("experiments/manifests/") and name.endswith(".json"):
            value = json.loads(text)
            if isinstance(value,dict) and isinstance(value.get("schema"),str):
                manifests.append(dict(path=name,sha256=sha256(ROOT/name),schema=value["schema"],
                                      experiment_id=value.get("experiment_id")))
    rows = []
    for name in paths:
        if not name.startswith(("scripts/","tests/","python/")) or not name.endswith(".py") or name == LEGACY:
            continue
        tree = ast.parse((ROOT/name).read_text())
        found = calls(tree,set(affected+consumers))
        if not found:
            continue
        references = sorted(p for p,text in documents.items() if name in text)
        constants = {n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
        rows.append(dict(path=name,sha256=sha256(ROOT/name),calls=found,
            role="test" if name.startswith("tests/") else "source",
            exact_path_references=references,
            matching_manifest_schemas=[m for m in manifests if m["schema"] in constants]))
    return dict(status="static-exposure-inventory-not-numerical-impact-audit",
        legacy_path=LEGACY,legacy_sha256=sha256(ROOT/LEGACY),
        generator_path=Path(__file__).resolve().relative_to(ROOT).as_posix(),generator_sha256=sha256(Path(__file__)),
        same_module_call_chain_functions=affected,explicit_result_consumers=consumers,callers=rows,
        source_callers=sum(r["role"] == "source" for r in rows),test_callers=sum(r["role"] == "test" for r in rows),
        source_scope="Tracked Python files under python/, scripts/ and tests/ at execution time; explicit import aliases and direct call expressions only.",
        reference_scope="Exact caller-path text mentions in tracked experiment Markdown/JSON and manifest JSON, plus manifest schema strings present literally in the caller. Neither a mention nor a schema match is proof of execution or numerical impact.",
        limitations=["Not a complete dynamic call graph", "No historical source checkout or raw-data replay",
            "No result is cleared or reclassified", "Unreferenced callers are retained", "No new numerical trajectories"],
        numerical_results_reclassified=0,new_integrations=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    a = parser.parse_args()
    if a.output.exists():
        parser.error("fresh inventory output required")
    result = inventory()
    write_json(a.output,result)
    print(json.dumps({k:result[k] for k in ("status","source_callers","test_callers","numerical_results_reclassified")}))


if __name__ == "__main__":
    main()

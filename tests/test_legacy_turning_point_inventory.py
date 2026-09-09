"""Static exposure is not a historical numerical-impact verdict."""
import ast
import json
from scripts import inventory_legacy_turning_point_callers as inventory


def test_transitive_local_callers_but_not_similar_names():
    tree = ast.parse("def _critical_points(): pass\ndef fit(): return _critical_points()\ndef public(): return fit()\ndef unaffected(): return different()")
    assert inventory.affected_functions(tree) == ["_critical_points","fit","public"]


def test_import_aliases_and_module_calls():
    tree = ast.parse("from butterfly import infer_return_map_branches as f\nimport butterfly.return_map as rm\nfrom butterfly import return_map as r\nf(); rm.infer_return_map_branches(); r.infer_return_map_branches()")
    result = inventory.calls(tree,{"infer_return_map_branches"})
    assert len(result) == 3 and all(r["function"] == "infer_return_map_branches" for r in result)


def test_same_name_without_import_is_not_assumed_to_be_legacy():
    tree = ast.parse("infer_return_map_branches(); unrelated.infer_return_map_branches()")
    assert inventory.calls(tree,{"infer_return_map_branches"}) == []


def test_published_inventory_binds_sources_without_claiming_impact():
    path = inventory.ROOT/"docs/experiments/receipts/EXP-481-legacy-caller-inventory.json"
    assert inventory.sha256(path) == "8f7baf60350d256e166155f561a9b47ee5f6b517ccaa20dd2e28f2e2a08dc8b8"
    saved = json.loads(path.read_bytes())
    assert saved["numerical_results_reclassified"] == saved["new_integrations"] == 0
    assert saved["source_callers"] == 21 and saved["test_callers"] == 3
    assert inventory.sha256(inventory.ROOT/saved["legacy_path"]) == saved["legacy_sha256"]
    assert inventory.sha256(inventory.ROOT/saved["generator_path"]) == saved["generator_sha256"]
    for row in saved["callers"]:
        assert inventory.sha256(inventory.ROOT/row["path"]) == row["sha256"]
        for manifest in row["matching_manifest_schemas"]:
            assert inventory.sha256(inventory.ROOT/manifest["path"]) == manifest["sha256"]
    assert len({m["experiment_id"] for r in saved["callers"] for m in r["matching_manifest_schemas"]}) == 42

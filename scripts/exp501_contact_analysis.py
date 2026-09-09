"""Complete limiting-boundary comparisons; no target integrations."""
from decimal import Decimal as D, localcontext
from butterfly.decimal_taylor import exact
from scripts.exp500_census_analysis import compare_events


def compare(profiles, candidate, cycles):
    if [v["configuration"] for v in profiles] != ["decimal-40", "decimal-50"]:
        raise ValueError("both ordered precision profiles required")
    root_pair, prefix_pair = None, None
    good_roots = all(v["shooting"]["status"] == "qualified" for v in profiles)
    with localcontext() as ctx:
        ctx.prec = 70
        if good_roots:
            a, b = [v["shooting"]["trace"][-1] for v in profiles]
            differences = dict(u=abs(D(a["u"])-D(b["u"])), time=abs(D(a["time"])-D(b["time"])),
                state=max(abs(D(x)-D(y))/exact(s) for x, y, s in zip(a["state"], b["state"], [15., 15., .01], strict=True)))
            root_pair = dict(**{k:str(v) for k,v in differences.items()},
                             passed=differences["u"] <= D("1e-12") and differences["time"] <= D("1e-12") and differences["state"] <= D("1e-9"))
            events = [[e for e in v["census"]["events"] if e["accepted"]] for v in profiles]
            prefix_pair = compare_events(*events, [15., 15., .01])
        rows = []
        for profile in profiles:
            eligible = (profile["shooting"]["status"] == "qualified" and profile["census"]["complete"]
                        and len([e for e in profile["census"]["events"] if e["accepted"]]) == candidate["accepted_prefix"]
                        and candidate["accepted_prefix"] > 0)
            if not eligible:
                continue
            event = [e for e in profile["census"]["events"] if e["accepted"]][-1]
            for cycle in cycles:
                for index, q in enumerate(cycle["states"]):
                    residual = [D(v)-exact(w) for v,w in zip(event["state"], q, strict=True)]
                    distance = max(abs(v)/exact(s) for v,s in zip(residual, [15.,15.,.01], strict=True))
                    rows.append(dict(configuration=profile["configuration"],method=cycle["method"],phase=cycle["phase"],
                        index=index,scaled_distance=str(distance),x_residual=str(residual[0]),
                        proximate=distance <= D("1e-4")))
        qualified = (good_roots and root_pair["passed"] and prefix_pair["passed"] and len(rows) == 48
                     and all(v["census"]["complete"] for v in profiles))
    return dict(qualified=qualified,root_pair=root_pair,prefix_pair=prefix_pair,comparisons=rows)


def aggregate(rows):
    if len(rows) != 8 or len({r["id"] for r in rows}) != 8:
        raise ValueError("all eight distinct candidates required")
    cells = [c for r in rows for c in r["comparison"]["comparisons"]]
    complete = all(r["comparison"]["qualified"] for r in rows) and len(cells) == 384
    with localcontext() as ctx:
        ctx.prec = 70
        by_index = []
        for index in range(6):
            selected = [D(c["scaled_distance"]) for c in cells if c["index"] == index]
            worst = max(selected) if selected else None
            by_index.append(dict(index=index,cells=len(selected),maximum_distance=None if worst is None else str(worst),
                all_proximate=complete and worst <= D("1e-4"),
                sensitivity=[dict(radius=r,all_proximate=complete and worst <= D(r)) for r in ("1e-6","1e-5","1e-3")]))
        def spread(states):
            if not states:
                return None
            envelope = [[min(D(q[i]) for q in states),max(D(q[i]) for q in states)] for i in range(3)]
            return dict(envelope=[[str(v) for v in pair] for pair in envelope],
                        maximum_scaled_spread=str(max((hi-lo)/exact(s) for (lo,hi),s in zip(envelope,[15.,15.,.01],strict=True))))
        roots, predecessors = [], []
        for row in rows:
            for v in row["profiles"]:
                if v["shooting"]["status"] == "qualified":
                    roots.append(v["shooting"]["trace"][-1]["state"])
                if v["census"] is not None and v["census"]["complete"]:
                    events = [e for e in v["census"]["events"] if e["accepted"]]
                    if events:
                        predecessors.append(events[-1]["state"])
    return dict(complete=complete,qualified_candidates=sum(r["comparison"]["qualified"] for r in rows),
                comparison_cells=len(cells),cycle_indices=by_index,grazing_spread=spread(roots),
                predecessor_spread=spread(predecessors),
                verdict=("proximate" if any(r["all_proximate"] for r in by_index) else "not-proximate") if complete else "mixed",
                symbolic_chains_verified=False,repairs_prior_failures=False,exact_flow_proof=False)

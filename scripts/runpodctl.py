#!/usr/bin/env python3
"""Small, auditable Runpod control surface with explicit cost gates.

The script reads RUNPOD_API_KEY from the environment or a local .env file. It
never prints the key. Provisioning is intentionally separate from workload
execution so every external resource has a recorded ID and teardown command.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REST_BASE = "https://rest.runpod.io/v1"
GRAPHQL_URL = "https://api.runpod.io/graphql"
DEFAULT_IMAGE = "runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04"


def load_local_env(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"").strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def api_key() -> str:
    load_local_env()
    value = os.environ.get("RUNPOD_API_KEY")
    if not value:
        raise SystemExit("RUNPOD_API_KEY is not set")
    return value


def request_json(
    method: str, url: str, *, payload: dict[str, Any] | None = None
) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key()}",
            "Content-Type": "application/json",
            "User-Agent": "butterfly-research/0.1 (+https://github.com/tdj28/butterfly)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Runpod API returned HTTP {error.code}: {message}") from None


def graphql(query: str) -> dict[str, Any]:
    # GraphQL currently authenticates through api_key in the query string.
    # Constructing it in-process keeps the secret out of command arguments.
    url = f"{GRAPHQL_URL}?{urllib.parse.urlencode({'api_key': api_key()})}"
    result = request_json("POST", url, payload={"query": query})
    if result.get("errors"):
        raise SystemExit(json.dumps(result["errors"], indent=2))
    return result["data"]


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def list_pods(_args: argparse.Namespace) -> None:
    pods = request_json("GET", f"{REST_BASE}/pods?includeMachine=true")
    print_json(
        [
            {
                "id": pod.get("id"),
                "name": pod.get("name"),
                "status": pod.get("desiredStatus"),
                "cost_per_hour": pod.get("adjustedCostPerHr", pod.get("costPerHr")),
                "gpu": (pod.get("gpu") or {}).get("displayName")
                or (pod.get("machine") or {}).get("gpuDisplayName"),
                "interruptible": pod.get("interruptible"),
            }
            for pod in pods
        ]
    )


def catalog(args: argparse.Namespace) -> None:
    data = graphql(
        """
        query {
          gpuTypes {
            id
            displayName
            memoryInGb
            secureCloud
            communityCloud
            lowestPrice(input: {gpuCount: 1}) {
              stockStatus
              uninterruptablePrice
              availableGpuCounts
            }
          }
        }
        """
    )
    rows = []
    for gpu in data["gpuTypes"]:
        price = (gpu.get("lowestPrice") or {}).get("uninterruptablePrice")
        stock = (gpu.get("lowestPrice") or {}).get("stockStatus")
        if price is None or price > args.max_hourly or stock == "None":
            continue
        rows.append(
            {
                "id": gpu["id"],
                "name": gpu["displayName"],
                "memory_gb": gpu["memoryInGb"],
                "price_per_hour": price,
                "stock": stock,
                "secure": gpu["secureCloud"],
                "community": gpu["communityCloud"],
            }
        )
    print_json(sorted(rows, key=lambda row: (row["price_per_hour"], row["id"])))


def launch(args: argparse.Namespace) -> None:
    if args.max_hourly <= 0.0:
        raise SystemExit("--max-hourly must be positive")
    existing = request_json("GET", f"{REST_BASE}/pods")
    duplicates = [pod for pod in existing if pod.get("name") == args.name]
    if duplicates:
        raise SystemExit(f"pod named {args.name!r} already exists; refusing duplicate")

    payload = {
        "name": args.name,
        "imageName": args.image,
        "cloudType": args.cloud,
        "computeType": "GPU",
        "gpuCount": 1,
        "gpuTypeIds": [args.gpu],
        "gpuTypePriority": "custom",
        "interruptible": args.interruptible,
        "containerDiskInGb": args.container_disk,
        "volumeInGb": args.volume,
        "volumeMountPath": "/workspace",
        "ports": ["22/tcp"],
        "supportPublicIp": True,
        "minVCPUPerGPU": 2,
        "minRAMPerGPU": 8,
    }
    pod = request_json("POST", f"{REST_BASE}/pods", payload=payload)
    cost = float(pod.get("adjustedCostPerHr", pod.get("costPerHr", "inf")))
    if cost > args.max_hourly:
        pod_id = pod.get("id")
        if pod_id:
            request_json("DELETE", f"{REST_BASE}/pods/{pod_id}")
        raise SystemExit(
            f"provider returned ${cost:.4f}/hour above ${args.max_hourly:.4f} ceiling; "
            "pod was terminated"
        )
    print_json(
        {
            "id": pod.get("id"),
            "name": pod.get("name"),
            "status": pod.get("desiredStatus"),
            "gpu": (pod.get("gpu") or {}).get("displayName"),
            "cost_per_hour": cost,
            "interruptible": pod.get("interruptible"),
            "teardown": f"python scripts/runpodctl.py terminate {pod.get('id')}",
        }
    )


def status(args: argparse.Namespace) -> None:
    print_json(request_json("GET", f"{REST_BASE}/pods/{args.pod_id}"))


def terminate(args: argparse.Namespace) -> None:
    result = request_json("DELETE", f"{REST_BASE}/pods/{args.pod_id}")
    print_json({"terminated": args.pod_id, "response": result})


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    list_parser = commands.add_parser("list", help="list account pods")
    list_parser.set_defaults(func=list_pods)

    catalog_parser = commands.add_parser("catalog", help="list live affordable GPUs")
    catalog_parser.add_argument("--max-hourly", type=float, default=0.30)
    catalog_parser.set_defaults(func=catalog)

    launch_parser = commands.add_parser("launch", help="create one cost-capped pod")
    launch_parser.add_argument("--name", default="butterfly-gpu-qualification")
    launch_parser.add_argument("--gpu", required=True)
    launch_parser.add_argument("--max-hourly", type=float, required=True)
    launch_parser.add_argument("--image", default=DEFAULT_IMAGE)
    launch_parser.add_argument("--cloud", choices=("SECURE", "COMMUNITY"), default="COMMUNITY")
    launch_parser.add_argument("--interruptible", action="store_true")
    launch_parser.add_argument("--container-disk", type=int, default=20)
    launch_parser.add_argument("--volume", type=int, default=0)
    launch_parser.set_defaults(func=launch)

    status_parser = commands.add_parser("status", help="inspect one pod")
    status_parser.add_argument("pod_id")
    status_parser.set_defaults(func=status)

    terminate_parser = commands.add_parser("terminate", help="permanently terminate one pod")
    terminate_parser.add_argument("pod_id")
    terminate_parser.set_defaults(func=terminate)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

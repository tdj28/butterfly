#!/usr/bin/env python3
"""Audit the separate Jones Figure 6 source-asset provenance record."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


SCHEMA = "butterfly.jones2012-figure6-asset-audit.v1"


def _valid_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("source asset is not a PNG")
    return struct.unpack(">II", header[16:24])


def audit_asset(document: dict, *, source_image: Path | None = None) -> dict:
    if document.get("schema") != SCHEMA:
        raise ValueError("unsupported Jones Figure 6 asset-audit schema")
    source = document["source"]
    asset = document["figure6_asset"]
    frozen = document["frozen_transcription"]
    for field, digest in (
        ("paper_sha256", source["paper_sha256"]),
        ("source_archive_sha256", source["source_archive_sha256"]),
        ("asset_sha256", asset["sha256"]),
        ("frozen_transcription_sha256", frozen["sha256"]),
    ):
        if not _valid_sha256(digest):
            raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    if asset["archive_member"] != "6.png":
        raise ValueError("Figure 6 must bind the author-supplied 6.png")
    if [asset["width_pixels"], asset["height_pixels"]] != [823, 534]:
        raise ValueError("unexpected Figure 6 raster dimensions")
    if asset["pdf_embedded_pixel_difference_count"] != 0:
        raise ValueError("PDF-embedded Figure 6 must agree pixelwise")
    if asset["has_recoverable_vector_geometry"]:
        raise ValueError("Figure 6 source is raster rather than vector geometry")
    if document["attachment_assessment"]["status"] != "not fully resolved":
        raise ValueError("crowded raster attachments must remain unresolved")

    image_verified = source_image is not None
    if source_image is not None:
        payload = source_image.read_bytes()
        if hashlib.sha256(payload).hexdigest() != asset["sha256"]:
            raise ValueError("source-image hash mismatch")
        if _png_dimensions(source_image) != (
            asset["width_pixels"],
            asset["height_pixels"],
        ):
            raise ValueError("source-image dimension mismatch")
    return {
        "passed": True,
        "image_verified": image_verified,
        "dimensions": [asset["width_pixels"], asset["height_pixels"]],
        "vector_geometry": asset["has_recoverable_vector_geometry"],
        "attachment_status": document["attachment_assessment"]["status"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--source-image", type=Path)
    args = parser.parse_args()
    result = audit_asset(
        json.loads(args.source.read_text()), source_image=args.source_image
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

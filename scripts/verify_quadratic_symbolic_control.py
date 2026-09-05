#!/usr/bin/env python3
"""Isolate primitive critical cycles of f_mu(x)=1-mu*x*x, without target words.

All polynomial, Sturm, bracket, and itinerary-sign arithmetic is exact over
integers/rationals. This certifies only the declared scalar family, assuming
the implementation and Python integer/Fraction arithmetic are correct. It is
not a proof about another map, a flow, a parameter-plane connection, or a
generating partition. No external symbolic list is an input to this program.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from fractions import Fraction
from functools import reduce
import hashlib
import json
from math import gcd, isfinite
import os
from pathlib import Path
import platform
import subprocess
import time
from typing import Callable


SCHEMA = "butterfly.quadratic-symbolic-control.v1"
MANIFEST_SCHEMA = "butterfly.quadratic-symbolic-control-manifest.v1"
ROOT = Path(__file__).resolve().parents[1]
Polynomial = tuple[int, ...]  # Ascending coefficient order; zero is (0,).


class VerificationFailure(ValueError):
    """A failed mathematical/preflight gate, never a passing certificate."""


class WorkLimit(VerificationFailure):
    """The declared exact-arithmetic budget was exhausted."""


@dataclass
class Budget:
    maximum_operations: int = 2_000_000
    maximum_coefficient_bits: int = 131_072
    maximum_interval_nodes: int = 200_000
    maximum_wall_seconds: float = 300.0
    clock: Callable[[], float] = time.monotonic
    operations: int = 0
    interval_nodes: int = 0
    started: float = field(init=False)
    sturm_cache: dict[Polynomial, tuple[Polynomial, ...]] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        for name in ("maximum_operations", "maximum_coefficient_bits", "maximum_interval_nodes"):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise VerificationFailure(f"{name} must be a positive integer")
        if (type(self.maximum_wall_seconds) not in (int, float)
                or not isfinite(self.maximum_wall_seconds)
                or self.maximum_wall_seconds <= 0):
            raise VerificationFailure("maximum_wall_seconds must be finite and positive")
        self.started = self.clock()

    def tick(self, count: int = 1):
        self.operations += count
        if self.operations > self.maximum_operations:
            raise WorkLimit("exact-arithmetic operation budget exceeded")
        if self.clock() - self.started > self.maximum_wall_seconds:
            raise WorkLimit("exact-arithmetic wall-time budget exceeded")

    def check(self, value):
        self.tick()
        if isinstance(value, Fraction):
            bits = max(value.numerator.bit_length(), value.denominator.bit_length())
        else:
            bits = abs(value).bit_length()
        if bits > self.maximum_coefficient_bits:
            raise WorkLimit("integer/rational bit-size budget exceeded")
        return value

    def visit_interval(self):
        self.tick()
        self.interval_nodes += 1
        if self.interval_nodes > self.maximum_interval_nodes:
            raise WorkLimit("root-isolation interval-node budget exceeded")

    def receipt(self):
        return {
            "operations": self.operations,
            "interval_nodes": self.interval_nodes,
            "elapsed_seconds": self.clock() - self.started,
        }


def trim(poly) -> Polynomial:
    values = list(poly)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values) if values else (0,)


def primitive(poly, budget: Budget) -> Polynomial:
    """Remove positive integer content, preserving the polynomial's sign."""
    poly = trim(poly)
    for value in poly:
        budget.check(value)
    divisor = reduce(gcd, (abs(value) for value in poly), 0)
    return tuple(value // divisor for value in poly) if divisor else (0,)


def derivative(poly: Polynomial, budget: Budget) -> Polynomial:
    return trim(budget.check(index * value) for index, value in enumerate(poly) if index)


def pseudo_remainder(left: Polynomial, right: Polynomial, budget: Budget) -> Polynomial:
    """A POSITIVE multiple of the rational remainder, avoiding denominators.

    Multiplication by abs(lc(right)), not lc(right), preserves signs even
    for negative leading coefficients. Positive content removal at each step
    preserves that property, which is essential to the Sturm sign sequence.
    """
    right = trim(right)
    if right == (0,):
        raise VerificationFailure("polynomial division by zero")
    remainder = trim(left)
    leading = right[-1]
    while remainder != (0,) and len(remainder) >= len(right):
        budget.tick()
        shift = len(remainder) - len(right)
        top = remainder[-1]
        values = [budget.check(abs(leading) * value) for value in remainder]
        direction = 1 if leading > 0 else -1
        for index, value in enumerate(right):
            values[index + shift] = budget.check(
                values[index + shift] - budget.check(top * direction * value)
            )
        remainder = primitive(values, budget)
    return remainder


def polynomial_gcd(left: Polynomial, right: Polynomial, budget: Budget) -> Polynomial:
    left, right = primitive(left, budget), primitive(right, budget)
    while right != (0,):
        budget.tick()
        left, right = right, pseudo_remainder(left, right, budget)
    if left == (0,):
        return left
    return tuple(-value for value in left) if left[-1] < 0 else left


def exact_divide(left: Polynomial, right: Polynomial, budget: Budget) -> Polynomial:
    """Exact Q[x] division, additionally requiring an integer quotient."""
    right = trim(right)
    if right == (0,):
        raise VerificationFailure("polynomial division by zero")
    remainder = list(map(Fraction, trim(left)))
    quotient = [Fraction(0)] * max(1, len(remainder) - len(right) + 1)
    while remainder != [0] and len(remainder) >= len(right):
        shift = len(remainder) - len(right)
        factor = budget.check(remainder[-1] / right[-1])
        quotient[shift] = budget.check(quotient[shift] + factor)
        for index, value in enumerate(right):
            remainder[index + shift] = budget.check(
                remainder[index + shift] - budget.check(factor * value)
            )
        remainder = list(trim(remainder))
    if any(remainder) or any(value.denominator != 1 for value in quotient):
        raise VerificationFailure("primitive factor division is not exact in Z[x]")
    return trim(value.numerator for value in quotient)


def critical_polynomials(maximum_period: int, budget: Budget) -> list[Polynomial]:
    """P_0=0, P_{n+1}=1-mu*P_n^2; degree P_7=63."""
    if type(maximum_period) is not int or not 2 <= maximum_period <= 7:
        raise VerificationFailure("maximum period must be an integer from 2 through 7")
    polynomials = [(0,), (1,)]
    for _period in range(2, maximum_period + 1):
        previous = polynomials[-1]
        square = [0] * (2 * len(previous) - 1)
        for i, left in enumerate(previous):
            for j, right in enumerate(previous):
                square[i + j] = budget.check(square[i + j] + budget.check(left * right))
        current = trim([1] + [-value for value in square])
        if len(current) - 1 > 63:
            raise VerificationFailure("polynomial degree exceeds the frozen maximum of 63")
        polynomials.append(current)
    return polynomials


def primitive_critical_polynomial(period: int, polynomials, budget: Budget):
    """Remove exactly those factors shared with proper-divisor recurrences."""
    current = polynomials[period]
    removed = []
    for divisor in range(1, period):
        if period % divisor:
            continue
        common = polynomial_gcd(current, polynomials[divisor], budget)
        current = exact_divide(current, common, budget)
        removed.append({
            "proper_divisor": divisor,
            "removed_degree": len(common) - 1,
            "factor_coefficients_ascending": list(common),
        })
    for row in removed:
        if len(polynomial_gcd(current, polynomials[row["proper_divisor"]], budget)) != 1:
            raise VerificationFailure("proper-divisor recurrence factor remains")
    return primitive(current, budget), removed


def sturm_sequence(poly: Polynomial, budget: Budget) -> tuple[Polynomial, ...]:
    poly = primitive(poly, budget)
    if len(poly) < 2:
        raise VerificationFailure("Sturm isolation requires a nonconstant polynomial")
    if poly in budget.sturm_cache:
        budget.tick()
        return budget.sturm_cache[poly]
    sequence = [poly, primitive(derivative(poly, budget), budget)]
    while True:
        remainder = pseudo_remainder(sequence[-2], sequence[-1], budget)
        if remainder == (0,):
            break
        sequence.append(tuple(-value for value in remainder))
    if len(sequence[-1]) != 1:
        raise VerificationFailure("polynomial is not square-free; no simple-root certificate")
    result = tuple(sequence)
    budget.sturm_cache[poly] = result
    return result


def evaluate(poly: Polynomial, value: Fraction, budget: Budget) -> Fraction:
    total = Fraction(0)
    for coefficient in reversed(poly):
        total = budget.check(budget.check(total * value) + coefficient)
    return total


def sign(value) -> int:
    return (value > 0) - (value < 0)


def variations(sequence, value: Fraction, budget: Budget) -> int:
    signs = [sign(evaluate(poly, value, budget)) for poly in sequence]
    nonzero = [item for item in signs if item]
    return sum(left != right for left, right in zip(nonzero, nonzero[1:]))


def count_open_roots(sequence, lower: Fraction, upper: Fraction, budget: Budget) -> int:
    """Number of distinct roots in (lower,upper), including neither endpoint.

    Zero-omitting Sturm variations are right-continuous at a simple root, so
    V(lower)-V(upper) includes an upper-endpoint root; explicitly subtract it.
    """
    if lower >= upper:
        raise VerificationFailure("root-count interval must be increasing")
    count = variations(sequence, lower, budget) - variations(sequence, upper, budget)
    count -= evaluate(sequence[0], upper, budget) == 0
    if count < 0:
        raise VerificationFailure("negative Sturm root count")
    return count


def isolate_roots(poly: Polynomial, lower: Fraction, upper: Fraction, *,
                  bits: int, budget: Budget) -> tuple[list[tuple[Fraction, Fraction]], int]:
    """Complete root isolation on a CLOSED rational interval, with exact ties."""
    if type(bits) is not int or not 1 <= bits <= 256:
        raise VerificationFailure("root interval bits must be an integer from 1 through 256")
    sequence = sturm_sequence(poly, budget)
    if lower >= upper:
        raise VerificationFailure("root-count interval must be increasing")
    intervals = []
    for endpoint in (lower, upper):
        if evaluate(poly, endpoint, budget) == 0:
            intervals.append((endpoint, endpoint))
    total_open = count_open_roots(sequence, lower, upper, budget)
    total = total_open + len(intervals)
    pending = [(lower, upper, total_open)]
    width = Fraction(1, 1 << bits)
    while pending:
        budget.visit_interval()
        left, right, count = pending.pop()
        if not count:
            continue
        # Non-singleton certificates must not contain a different root at an
        # endpoint, even though the open-interval Sturm count excludes it.
        endpoints_clear = (evaluate(poly, left, budget) != 0
                           and evaluate(poly, right, budget) != 0)
        if count == 1 and right - left <= width and endpoints_clear:
            intervals.append((left, right))
            continue
        middle = (left + right) / 2
        is_root = evaluate(poly, middle, budget) == 0
        left_count = count_open_roots(sequence, left, middle, budget)
        right_count = count_open_roots(sequence, middle, right, budget)
        if left_count + right_count + is_root != count:
            raise VerificationFailure("Sturm subdivision fails root-count conservation")
        if is_root:
            intervals.append((middle, middle))
        pending.extend(((middle, right, right_count), (left, middle, left_count)))
    intervals.sort()
    if len(intervals) != total:
        raise VerificationFailure("isolated-root count differs from complete Sturm count")
    if any(left[1] >= right[0] for left, right in zip(intervals, intervals[1:])):
        raise VerificationFailure("root certificates are not strictly disjoint")
    return intervals, total


def interval_square(bounds, budget: Budget):
    lower, upper = bounds
    squares = (budget.check(lower * lower), budget.check(upper * upper))
    return (Fraction(0) if lower <= 0 <= upper else min(squares), max(squares))


def interval_product(left, right, budget: Budget):
    products = [budget.check(a * b) for a in left for b in right]
    return min(products), max(products)


def critical_sign_intervals(parameter_interval, period: int, budget: Budget):
    """Rational interval recurrence certifies every noncritical cycle sign."""
    state = (Fraction(0), Fraction(0))
    intervals = []
    for _index in range(1, period):
        product = interval_product(parameter_interval, interval_square(state, budget), budget)
        state = (budget.check(1 - product[1]), budget.check(1 - product[0]))
        intervals.append(state)
    return intervals


def certified_cycle(poly: Polynomial, parameter_interval, period: int, budget: Budget,
                    *, maximum_refinements: int = 256):
    """Refine a unique-root enclosure until intermediate signs exclude zero.

    Closure comes from the exact recurrence polynomial's root certificate,
    not a small floating-point residual. Every intermediate state must be
    strictly nonzero, independently certifying primitive period.
    """
    # Do not trust the caller's polynomial merely because it has a root:
    # every one of its roots must also solve the actual scalar recurrence.
    recurrence = critical_polynomials(period, budget)[period]
    try:
        exact_divide(recurrence, poly, budget)
    except VerificationFailure as error:
        if isinstance(error, WorkLimit):
            raise
        raise VerificationFailure("certificate polynomial is not a factor of the critical recurrence") from error
    lower, upper = parameter_interval
    sequence = sturm_sequence(poly, budget)
    if lower == upper:
        if evaluate(poly, lower, budget) != 0:
            raise VerificationFailure("claimed singleton is not an exact recurrence root")
    elif (count_open_roots(sequence, lower, upper, budget) != 1
          or evaluate(poly, lower, budget) == 0 or evaluate(poly, upper, budget) == 0):
        raise VerificationFailure("cycle enclosure must contain exactly one root")
    for refinement in range(maximum_refinements + 1):
        budget.visit_interval()
        intervals = critical_sign_intervals((lower, upper), period, budget)
        if all(left > 0 or right < 0 for left, right in intervals):
            symbols = ["C"] + ["1" if left > 0 else "0" for left, _right in intervals]
            return {
                "parameter_interval": [str(lower), str(upper)],
                "parameter_interval_width": str(upper - lower),
                "exact_rational_root": lower == upper,
                "unique_root_certified": True,
                "exact_recurrence_factor_verified": True,
                "primitive_period_certified": True,
                "period": period,
                "critical_anchored_word": "".join(symbols),
                "noncritical_sign_intervals": [
                    {"iterate": index, "lower": str(left), "upper": str(right),
                     "sign": 1 if left > 0 else -1}
                    for index, (left, right) in enumerate(intervals, start=1)
                ],
                "additional_sign_refinements": refinement,
            }
        if lower == upper:
            raise VerificationFailure("recurrence root has a lower primitive period")
        middle = (lower + upper) / 2
        if evaluate(poly, middle, budget) == 0:
            lower = upper = middle
        elif count_open_roots(sequence, lower, middle, budget) == 1:
            upper = middle
        else:
            lower = middle
    raise VerificationFailure("noncritical itinerary signs remain unresolved at refinement limit")


def parse_manifest(document: dict) -> dict:
    keys = {"schema", "experiment_id", "periods", "parameter_domain",
            "root_interval_bits", "maximum_sign_refinements", "limits"}
    if not isinstance(document, dict) or set(document) != keys:
        raise VerificationFailure("manifest must have exactly the declared protocol fields")
    if document["schema"] != MANIFEST_SCHEMA:
        raise VerificationFailure("unsupported quadratic-control manifest schema")
    identifier = document["experiment_id"]
    if (not isinstance(identifier, str) or not identifier or len(identifier) > 100
            or any(not (character.isalnum() or character in "-_") for character in identifier)):
        raise VerificationFailure("experiment_id must be a short alphanumeric identifier")
    periods = document["periods"]
    if (not isinstance(periods, list) or not periods
            or any(type(period) is not int or not 2 <= period <= 7 for period in periods)
            or periods != sorted(set(periods))):
        raise VerificationFailure("periods must be distinct increasing integers from 2 through 7")
    if document["parameter_domain"] != ["0", "2"]:
        raise VerificationFailure("only the declared exact parameter domain ['0','2'] is supported")
    bits, refinements = document["root_interval_bits"], document["maximum_sign_refinements"]
    if type(bits) is not int or not 1 <= bits <= 256:
        raise VerificationFailure("root_interval_bits must be an integer from 1 through 256")
    if type(refinements) is not int or not 0 <= refinements <= 256:
        raise VerificationFailure("maximum_sign_refinements must be an integer from 0 through 256")
    limits = document["limits"]
    expected_limits = {"maximum_operations", "maximum_coefficient_bits",
                       "maximum_interval_nodes", "maximum_wall_seconds"}
    if not isinstance(limits, dict) or set(limits) != expected_limits:
        raise VerificationFailure("limits must have exactly the four declared budget fields")
    Budget(**limits)  # Validate without doing any scientific enumeration.
    return document


def verify_control(document: dict, *, budget: Budget | None = None,
                   progress: Callable[[dict], None] | None = None) -> dict:
    manifest = parse_manifest(document)
    budget = budget if budget is not None else Budget(**manifest["limits"])
    rows = []
    result = {
        "schema": SCHEMA,
        "experiment_id": manifest["experiment_id"],
        "family": "f_mu(x)=1-mu*x^2",
        "critical_point": "0",
        "parameter_domain": ["0", "2"],
        "alphabet": {"C": "exact critical point 0", "1": "strictly positive state",
                     "0": "strictly negative state"},
        "word_convention": "time order, anchored at the unique critical point; no reversal or relabeling",
        "method": "exact integer primitive factors, sign-preserving Sturm sequences, rational interval signs",
        "claim_scope": "complete primitive critical-cycle list for the specified periods of this scalar family only",
        "assumptions": ["correctness of this implementation and Python exact integer/rational arithmetic",
                        "Sturm's theorem for square-free real polynomials",
                        "a repeated critical point before return gives a proper-divisor period"],
        "limitations": ["not independently proof-assistant-checked",
                        "does not verify another map, a flow, a symbolic partition, or parameter-plane connections",
                        "root counts are complete only inside the declared parameter domain and periods"],
        "protocol": manifest,
        "period_results": rows,
        "passed": False,
    }
    try:
        polynomials = critical_polynomials(max(manifest["periods"]), budget)
        for period in manifest["periods"]:
            primitive_poly, removed = primitive_critical_polynomial(period, polynomials, budget)
            intervals, count = isolate_roots(
                primitive_poly, Fraction(0), Fraction(2),
                bits=manifest["root_interval_bits"], budget=budget,
            )
            cycles = [certified_cycle(
                primitive_poly, interval, period, budget,
                maximum_refinements=manifest["maximum_sign_refinements"],
            ) for interval in intervals]
            row = {
                "period": period,
                "recurrence_polynomial_coefficients_ascending": list(polynomials[period]),
                "primitive_polynomial_coefficients_ascending": list(primitive_poly),
                "proper_divisor_exclusions": removed,
                "primitive_polynomial_square_free": True,
                "complete_domain_root_count": count,
                "cycles": cycles,
                "passed": len(cycles) == count and all(cycle["primitive_period_certified"] for cycle in cycles),
            }
            rows.append(row)
            if progress is not None:
                progress({"period": period, "root_count": count, "passed": row["passed"]})
        result["passed"] = len(rows) == len(manifest["periods"]) and all(row["passed"] for row in rows)
    except (ValueError, ArithmeticError) as error:
        result["failure"] = {"kind": type(error).__name__, "message": str(error)}
    result["work"] = budget.receipt()
    return result


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def source_provenance() -> dict:
    def git(*arguments):
        completed = subprocess.run(["git", *arguments], cwd=ROOT, capture_output=True,
                                   text=True, check=False, timeout=10)
        if completed.returncode:
            raise VerificationFailure("source provenance requires an accessible Git checkout")
        return completed.stdout.strip()
    return {
        "commit": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "dirty": bool(git("status", "--porcelain", "--untracked-files=normal")),
        "script_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "uv_lock_sha256": sha256_bytes((ROOT / "uv.lock").read_bytes()),
    }


def write_exclusive(path: Path, document: dict):
    """Create one new receipt; never replace an existing file or symlink."""
    payload = (json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    # lexists also rejects dangling symlinks, before any expensive computation.
    if os.path.lexists(args.output):
        parser.error("output already exists; choose a new receipt path")
    receipt = {"schema": SCHEMA, "passed": False}
    try:
        raw_manifest = args.manifest.read_bytes()
        receipt["manifest_sha256"] = sha256_bytes(raw_manifest)
        manifest = json.loads(raw_manifest, parse_constant=lambda _value: (_ for _ in ()).throw(
            VerificationFailure("manifest contains a nonfinite JSON constant")))
        parse_manifest(manifest)
        receipt["source"] = source_provenance()
        receipt["environment"] = {"python": platform.python_version(),
                                  "implementation": platform.python_implementation(),
                                  "arithmetic": "standard-library int and fractions.Fraction; no external dependencies"}
        if receipt["source"]["dirty"]:
            raise VerificationFailure("clean, committed source and protocol required before enumeration")
        result = verify_control(manifest, progress=lambda row: print(json.dumps(row, sort_keys=True), flush=True))
        receipt.update(result)
        receipt["source_after"] = source_provenance()
        if receipt["source_after"] != receipt["source"]:
            raise VerificationFailure("source changed during enumeration; result is not frozen-source evidence")
        if sha256_bytes(args.manifest.read_bytes()) != receipt["manifest_sha256"]:
            raise VerificationFailure("protocol changed during enumeration")
    except (ValueError, ArithmeticError) as error:
        receipt["passed"] = False
        receipt["failure"] = {"kind": type(error).__name__, "message": str(error)}
    except (OSError, subprocess.SubprocessError):
        # Do not put machine paths, process stderr, or endpoint details in public receipts.
        receipt["passed"] = False
        receipt["failure"] = {"kind": "PreflightIOError", "message": "unable to read declared input or source provenance"}
    write_exclusive(args.output, receipt)
    print(json.dumps({"passed": receipt["passed"], "completed_periods": len(receipt.get("period_results", [])),
                      "failure": receipt.get("failure")}, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

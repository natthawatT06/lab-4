from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CASE_DIRS = {
    "normal": ROOT / "1.normal-20260902T030812Z-1-001" / "1.normal",
    "extra": ROOT / "2.Extra-20260902T030835Z-1-001" / "2.Extra",
}


@dataclass(frozen=True)
class Expected:
    optimal_solutions: int
    max_passengers: int


def read_case(path: Path) -> tuple[str, int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2:
        raise ValueError(f"{path.name}: expected two input lines")
    s = lines[0].strip()
    k = int(lines[1].strip())
    if not s or any(ch not in "GP" for ch in s):
        raise ValueError(f"{path.name}: first line must contain only G and P")
    if k < 0:
        raise ValueError(f"{path.name}: k must be non-negative")
    return s, k


def reference_answer(s: str, k: int) -> Expected:
    """Count maximum matchings with a bounded-state dynamic program.

    A state contains unmatched positions from the last k places.  For each new
    G/P, it can remain unmatched or be matched to one compatible opposite item.
    Every matching is generated exactly once, including the empty matching.
    """

    # state -> (number of pairs, number of ways producing that state and score)
    dp: dict[tuple[tuple[int, str], ...], tuple[int, int]] = {(): (0, 1)}

    for position, kind in enumerate(s):
        next_dp: dict[tuple[tuple[int, str], ...], tuple[int, int]] = {}

        def update(
            state: tuple[tuple[int, str], ...], score: int, ways: int
        ) -> None:
            previous = next_dp.get(state)
            if previous is None or score > previous[0]:
                next_dp[state] = (score, ways)
            elif score == previous[0]:
                next_dp[state] = (score, previous[1] + ways)

        for state, (score, ways) in dp.items():
            active = tuple(item for item in state if position - item[0] <= k)

            # Leave the current item unmatched; it may still match a future item.
            update(active + ((position, kind),), score, ways)

            # Or match it with one currently unmatched opposite item.
            for index, (_, prior_kind) in enumerate(active):
                if prior_kind != kind:
                    matched_state = active[:index] + active[index + 1 :]
                    update(matched_state, score + 1, ways)

        dp = next_dp

    best = max(score for score, _ in dp.values())
    ways = sum(ways for score, ways in dp.values() if score == best)
    return Expected(ways, best)


def run_program(program: Path, case_input: str, timeout: float) -> tuple[str, float]:
    started = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, str(program)],
        input=case_input,
        text=True,
        capture_output=True,
        timeout=timeout,
        cwd=ROOT,
        check=False,
    )
    elapsed = time.perf_counter() - started
    if completed.returncode != 0:
        error = completed.stderr.strip() or f"exit code {completed.returncode}"
        return f"ERROR: {error}", elapsed
    return "\n".join(completed.stdout.split()), elapsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Lab 4 Q1/Q2 test cases")
    parser.add_argument(
        "--timeout", type=float, default=3.0, help="seconds allowed per program/case"
    )
    parser.add_argument(
        "--include-extra-q1",
        action="store_true",
        help="also run exponential Q1.py against Extra cases",
    )
    args = parser.parse_args()

    failures = 0
    totals = 0
    print("case       Q1 expected     Q1 result       Q2 expected  Q2 result")
    print("-" * 75)

    for group, directory in CASE_DIRS.items():
        for path in sorted(directory.glob("*.txt")):
            s, k = read_case(path)
            expected = reference_answer(s, k)
            case_input = f"{s}\n{k}\n"
            q1_expected = f"{expected.optimal_solutions}\n{expected.max_passengers}"
            q2_expected = str(expected.max_passengers)

            if group == "extra" and not args.include_extra_q1:
                q1_result = "SKIP (use flag)"
                q1_ok = True
            else:
                try:
                    actual, elapsed = run_program(ROOT / "Q1.py", case_input, args.timeout)
                    q1_ok = actual == q1_expected
                    q1_result = f"{'PASS' if q1_ok else 'FAIL'} {elapsed:.3f}s"
                except subprocess.TimeoutExpired:
                    q1_ok = False
                    q1_result = f"TIMEOUT >{args.timeout:g}s"
                totals += 1
                failures += not q1_ok

            try:
                actual, elapsed = run_program(ROOT / "Q2.py", case_input, args.timeout)
                q2_ok = actual == q2_expected
                q2_result = f"{'PASS' if q2_ok else 'FAIL'} {elapsed:.3f}s"
            except subprocess.TimeoutExpired:
                q2_ok = False
                q2_result = f"TIMEOUT >{args.timeout:g}s"
            totals += 1
            failures += not q2_ok

            print(
                f"{path.stem:<10} "
                f"{expected.optimal_solutions:>7},{expected.max_passengers:<3}     "
                f"{q1_result:<15} "
                f"{expected.max_passengers:>6}       {q2_result}"
            )

    print("-" * 75)
    print(f"Executed: {totals}, passed: {totals - failures}, failed: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

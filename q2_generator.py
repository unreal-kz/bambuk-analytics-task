"""
Question 2 — Control dataset generator
=======================================
Generates N random log lines conforming to the format defined in Q1,
then verifies every line against the LINE regex.

Usage:
    python q2_generator.py          # generates 5 rows (default)
    python q2_generator.py 1000     # generates 1000 rows
"""

import random
import ipaddress
import sys
from datetime import datetime, timedelta

from q1_regex import LINE  # reuse the compiled pattern from Q1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rnd_ipv6() -> str:
    """Return a random, correctly compressed IPv6 address string."""
    return str(ipaddress.IPv6Address(random.randint(0, 2**128 - 1)))


def rnd_coord(max_deg: float) -> str:
    """
    Return a coordinate in the range [-max_deg, max_deg] formatted with a
    comma as the decimal separator and exactly 2 decimal places.
    """
    value = round(random.uniform(-max_deg, max_deg), 2)
    formatted = f"{abs(value):.2f}".replace(".", ",")
    return formatted if value >= 0 else f"-{formatted}"


def rnd_dt(lo: datetime, hi: datetime) -> datetime:
    """Return a random datetime between lo and hi (inclusive)."""
    delta_secs = int((hi - lo).total_seconds())
    return lo + timedelta(seconds=random.randint(0, delta_secs))


# ---------------------------------------------------------------------------
# Row generator
# ---------------------------------------------------------------------------

PAYMENT_LO = datetime(2023, 1, 1)
PAYMENT_HI = datetime(2025, 12, 31, 23, 59, 59)


def generate_row() -> str:
    """Build one valid log line."""
    bid      = random.randint(100_000_000, 999_999_999)
    ip       = rnd_ipv6()
    paid_at  = rnd_dt(PAYMENT_LO, PAYMENT_HI)
    lon      = rnd_coord(180)
    lat      = rnd_coord(90)
    checkin  = paid_at.date() + timedelta(days=random.randint(1, 90))
    checkout = checkin + timedelta(days=random.randint(1, 14))
    return f"{bid};{ip};{paid_at:%Y-%m-%d %H:%M:%S};{lon};{lat};{checkin};{checkout}"


def generate_dataset(n: int = 5, seed: int | None = None) -> list[str]:
    if seed is not None:
        random.seed(seed)
    return [generate_row() for _ in range(n)]


# ---------------------------------------------------------------------------
# Main — generate, print, and verify
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    rows = generate_dataset(n, seed=42)

    print("Generated rows:")
    print("-" * 80)
    for row in rows:
        print(row)

    print()
    print("Verification against LINE regex:")
    failures = 0
    for i, row in enumerate(rows, 1):
        if LINE.fullmatch(row):
            print(f"  Row {i:>4}: OK")
        else:
            print(f"  Row {i:>4}: FAIL  ← {row}")
            failures += 1

    print()
    if failures == 0:
        print(f"All {n} rows matched the pattern.")
    else:
        print(f"{failures}/{n} rows FAILED.")

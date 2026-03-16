"""
Question 1 — RegExp
===================
Parse and validate log lines with the following semicolon-separated fields:
  1. Booking ID   : 9-digit integer starting with 1-9  (100000000–999999999)
  2. IPv6 address : full RFC-5952 compressed form
  3. Payment datetime: YYYY-MM-DD hh:mm:ss
  4. Longitude    : −180,00 … 180,00  (comma as decimal separator)
  5. Latitude     : −90,00 … 90,00   (comma as decimal separator)
  6. Check-in date : YYYY-MM-DD
  7. Check-out date: YYYY-MM-DD
"""

import re

# ---------------------------------------------------------------------------
# IPv6 pattern — covers every valid compressed form per RFC 5952
# ---------------------------------------------------------------------------
_IPV6 = (
    r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}'            # full 8-group
    r'|(?:[0-9a-fA-F]{1,4}:){1,7}:'                          # trailing ::  (e.g. 1:: … 7::)
    r'|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}'
    r'|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}'
    r'|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}'
    r'|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}'
    r'|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}'
    r'|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){1,6}'
    r'|::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}'        # leading ::
    r'|::'                                                     # loopback / unspecified
)

# ---------------------------------------------------------------------------
# Full line pattern
# ---------------------------------------------------------------------------
LINE = re.compile(
    r'^([1-9]\d{8})'                                    # 1 — booking ID
    r';(' + _IPV6 + r')'                                # 2 — IPv6
    r';(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'          # 3 — payment datetime
    r';(-?(?:180|1[0-7]\d|\d{1,2}),\d{2})'             # 4 — longitude
    r';(-?(?:90|[0-8]\d|\d),\d{2})'                    # 5 — latitude
    r';(\d{4}-\d{2}-\d{2})'                             # 6 — check-in date
    r';(\d{4}-\d{2}-\d{2})$'                            # 7 — check-out date
)

# ---------------------------------------------------------------------------
# Verification — 5 hand-crafted sample rows (used in Q2 as well)
# ---------------------------------------------------------------------------
SAMPLE_ROWS = [
    "423871956;2001:db8:85a3::8a2e:370:7334;2024-06-12 11:32:17;37,62;55,75;2024-07-01;2024-07-07",
    "857234190;fe80::d8e4:3ff:fe56:c2a1;2023-12-20 08:45:00;2,35;48,85;2023-12-27;2024-01-03",
    "193847265;2600:1f18:4a1:2300::1;2025-01-15 20:12:33;-43,18;-22,91;2025-02-01;2025-02-05",
    "674839201;fd12:3456:789a:0001::0001;2024-03-08 15:55:44;139,69;35,69;2024-04-10;2024-04-15",
    "312984756;2a02:6b8:0:1::242;2024-09-22 07:30:00;18,06;59,33;2024-10-05;2024-10-12",
]

if __name__ == "__main__":
    print("Verifying sample rows against LINE pattern:\n")
    all_ok = True
    for row in SAMPLE_ROWS:
        m = LINE.fullmatch(row)
        status = "OK" if m else "FAIL"
        if not m:
            all_ok = False
        print(f"  [{status}] {row[:60]}...")
        if m:
            fields = ["booking_id", "ipv6", "paid_at", "lon", "lat", "checkin", "checkout"]
            for name, val in zip(fields, m.groups()):
                print(f"         {name:12s} = {val}")
        print()
    print("All rows matched!" if all_ok else "Some rows FAILED — check the regex.")

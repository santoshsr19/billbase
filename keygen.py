"""
keygen.py — Sudev's Billing System · License Key Generator
Run this script whenever you need to issue a new key.

Usage:
    python3 keygen.py
    python3 keygen.py 2027-06-07   ← custom expiry date
"""

import sys
import hashlib
from datetime import datetime, timedelta

# ── SECRET SALT — never share this ──────────────────────
# If you change this, all old keys stop working.
SECRET = "SUDEV_BILLING_S3CR3T_2024"
# ────────────────────────────────────────────────────────

def make_checksum(expiry_str: str) -> str:
    raw = f"{SECRET}:{expiry_str}"
    h   = hashlib.sha256(raw.encode()).hexdigest().upper()
    return h[:6]   # 6-char checksum

def generate_key(expiry_date: datetime) -> str:
    expiry_str = expiry_date.strftime("%Y%m%d")
    checksum   = make_checksum(expiry_str)
    return f"SUDEV-{expiry_str}-{checksum}"

def main():
    if len(sys.argv) > 1:
        try:
            expiry = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        except ValueError:
            print("❌  Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        # Default: 6 months from today
        today  = datetime.today()
        # Add ~6 months (183 days)
        expiry = today + timedelta(days=183)

    key = generate_key(expiry)

    print()
    print("=" * 50)
    print("  Sudev's Billing System — License Key")
    print("=" * 50)
    print(f"  Key     : {key}")
    print(f"  Expires : {expiry.strftime('%d %b %Y')}")
    print(f"  Valid   : {183} days from today")
    print("=" * 50)
    print()
    print("📋  Send this key to the customer.")
    print("    They paste it into:  license.txt")
    print()

if __name__ == "__main__":
    main()

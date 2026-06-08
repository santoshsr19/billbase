"""
license.py — License key validator for Sudev's Billing System
"""

import hashlib
import os
from datetime import datetime, timedelta
from typing import Tuple

# ── Must match keygen.py exactly ────────────────────────
SECRET       = "SUDEV_BILLING_S3CR3T_2024"
GRACE_DAYS   = 15          # warn but allow for 15 days after expiry
LICENSE_FILE = os.path.join(os.path.dirname(__file__), "license.txt")
# ────────────────────────────────────────────────────────

# Status constants
STATUS_VALID   = "valid"
STATUS_GRACE   = "grace"      # expired but within grace period
STATUS_EXPIRED = "expired"    # fully blocked
STATUS_INVALID = "invalid"    # bad key / tampered
STATUS_MISSING = "missing"    # no license.txt


def _checksum(expiry_str: str) -> str:
    raw = f"{SECRET}:{expiry_str}"
    return hashlib.sha256(raw.encode()).hexdigest().upper()[:6]


def validate_key(key: str) -> Tuple[str, str, str]:
    """
    Returns (status, expiry_display, message)
    status: one of STATUS_* constants above
    """
    key = key.strip().upper()

    # Expected format: SUDEV-YYYYMMDD-XXXXXX
    parts = key.split("-")
    if len(parts) != 3 or parts[0] != "SUDEV":
        return STATUS_INVALID, "", "Invalid key format."

    expiry_str, given_checksum = parts[1], parts[2]

    # Validate date part
    try:
        expiry_date = datetime.strptime(expiry_str, "%Y%m%d")
    except ValueError:
        return STATUS_INVALID, "", "Invalid date in key."

    # Validate checksum
    expected = _checksum(expiry_str)
    if given_checksum != expected:
        return STATUS_INVALID, "", "Key checksum mismatch — key may be tampered."

    expiry_display = expiry_date.strftime("%d %b %Y")
    today          = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    grace_end      = expiry_date + timedelta(days=GRACE_DAYS)
    days_left      = (expiry_date - today).days

    if today <= expiry_date:
        return STATUS_VALID, expiry_display, f"License valid. Expires {expiry_display} ({days_left} days left)."

    elif today <= grace_end:
        grace_left = (grace_end - today).days
        return STATUS_GRACE, expiry_display, (
            f"License expired on {expiry_display}. "
            f"Grace period: {grace_left} day(s) remaining. Please renew."
        )
    else:
        return STATUS_EXPIRED, expiry_display, (
            f"License expired on {expiry_display}. Grace period also over. "
            f"Contact Sudev to renew."
        )


def check_license() -> Tuple[str, str, str]:
    """Read license.txt and validate. Returns (status, expiry, message)."""
    if not os.path.exists(LICENSE_FILE):
        return STATUS_MISSING, "", "license.txt not found. Contact Sudev for a license key."

    with open(LICENSE_FILE, "r") as f:
        key = f.read().strip()

    if not key:
        return STATUS_MISSING, "", "license.txt is empty. Paste your license key into it."

    return validate_key(key)

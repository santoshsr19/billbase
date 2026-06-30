from datetime import datetime
from database import get_conn

STATUS_VALID = "valid"
STATUS_EXPIRED = "expired"


def check_license():
    conn = get_conn()
    row = conn.execute(
        "SELECT expiry_date FROM settings WHERE id=1"
    ).fetchone()
    conn.close()

    expiry = row["expiry_date"]

    if not expiry:
        return STATUS_VALID, None, "No expiry set"

    expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()

    if datetime.today().date() > expiry_date:
        return STATUS_EXPIRED, expiry, "License expired"

    return STATUS_VALID, expiry, "License active"
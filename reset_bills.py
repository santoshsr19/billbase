"""
reset_bills.py
---------------
Clears all bill data (bills, bill_items, bill_counter) so billing
starts fresh from INV2026-0001 next time the server runs.

Catalogue, settings, and everything else are left untouched.

HOW TO USE:
1. Stop your billing server first.
2. Place this file in the same folder as billease.db
   (or edit DB_PATH below to point to it).
3. Run:  python reset_bills.py
"""

import sqlite3
import os

DB_PATH = "billease.db"   # change this if your db file is elsewhere

if not os.path.exists(DB_PATH):
    print(f"ERROR: '{DB_PATH}' not found. Edit DB_PATH in this script.")
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("DELETE FROM bill_items")
cur.execute("DELETE FROM bills")
cur.execute("DROP TABLE IF EXISTS bill_counter")
cur.execute("DELETE FROM sqlite_sequence WHERE name IN ('bills','bill_items')")

conn.commit()
conn.close()

print("Done.")
print(" - bills: cleared")
print(" - bill_items: cleared")
print(" - bill_counter: dropped (will be recreated fresh on next server start)")
print(" - catalogue, settings: untouched")
print("\nStart your server now. First new bill will be INV2026-0001.")

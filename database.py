import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "billease.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # safe concurrent reads
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables and seed defaults on first run."""
    conn = get_conn()
    cur = conn.cursor()

    # ── Settings (single row, id=1 always)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id          INTEGER PRIMARY KEY DEFAULT 1,
            biz_name    TEXT    DEFAULT '',
            biz_addr    TEXT    DEFAULT '',
            biz_phone   TEXT    DEFAULT '',
            biz_email   TEXT    DEFAULT '',
            biz_gstin   TEXT    DEFAULT '',
            bill_prefix TEXT    DEFAULT 'INV',
            CHECK (id = 1)
        )
    """)
    cur.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")

    # ── Bill counter (atomic, transaction-safe)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bill_counter (
            id      INTEGER PRIMARY KEY DEFAULT 1,
            counter INTEGER NOT NULL DEFAULT 1,
            CHECK (id = 1)
        )
    """)
    cur.execute("INSERT OR IGNORE INTO bill_counter (id, counter) VALUES (1, 1)")

    # ── Catalogue
    cur.execute("""
        CREATE TABLE IF NOT EXISTS catalogue (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
	    hsn_code   TEXT    DEFAULT '',
            unit       TEXT    NOT NULL DEFAULT 'pcs',
            price      REAL    NOT NULL DEFAULT 0,
            gst_rate   REAL    NOT NULL DEFAULT 18,
            created_at TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Bills
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no     TEXT    NOT NULL UNIQUE,
            bill_date   TEXT,
            due_date    TEXT,
            cust_name   TEXT    NOT NULL,
            cust_addr   TEXT    DEFAULT '',
            cust_phone  TEXT    DEFAULT '',
            cust_gstin  TEXT    DEFAULT '',
            notes       TEXT    DEFAULT '',
            subtotal    REAL    DEFAULT 0,
            total_gst   REAL    DEFAULT 0,
            grand_total REAL    DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now','localtime')),
            updated_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Bill line items
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id    INTEGER NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
            name       TEXT    NOT NULL,
            unit       TEXT    DEFAULT 'pcs',
            qty        REAL    NOT NULL DEFAULT 1,
            price      REAL    NOT NULL DEFAULT 0,
            gst_rate   REAL    NOT NULL DEFAULT 0,
            hsn_code   TEXT    DEFAULT '',
            gst_amt    REAL    NOT NULL DEFAULT 0,
            total      REAL    NOT NULL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    print(f"[DB] Initialised → {DB_PATH}")

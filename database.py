import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "billease.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def add_column_if_missing(conn, table, column, definition):
    cols = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def current_fiscal_year() -> int:
    today = date.today()
    return today.year if today.month <= 3 else today.year + 1


def init_db():
    """Create all tables and seed defaults on first run."""
    conn = get_conn()
    cur = conn.cursor()

    # ── Settings
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

    # ── Bill counter
    cur.execute("""
		CREATE TABLE IF NOT EXISTS bill_counter (
    		fiscal_year INTEGER PRIMARY KEY,
    		counter     INTEGER NOT NULL DEFAULT 1
		)
            """)

    counter_cols = [row["name"] for row in cur.execute("PRAGMA table_info(bill_counter)")]
    if "fiscal_year" not in counter_cols:
        old_counter = cur.execute("SELECT counter FROM bill_counter LIMIT 1").fetchone()
        old_value = old_counter["counter"] if old_counter else 1
        cur.execute("ALTER TABLE bill_counter RENAME TO bill_counter_old")
        cur.execute("""
            CREATE TABLE bill_counter (
                fiscal_year INTEGER PRIMARY KEY,
                counter     INTEGER NOT NULL DEFAULT 1
            )
        """)
        cur.execute(
            "INSERT OR IGNORE INTO bill_counter (fiscal_year, counter) VALUES (?, ?)",
            (current_fiscal_year(), old_value),
        )
        cur.execute("DROP TABLE bill_counter_old")
    else:
        cur.execute(
            "INSERT OR IGNORE INTO bill_counter (fiscal_year, counter) VALUES (?, 1)",
            (current_fiscal_year(),),
        )

    # ── Catalogue
    cur.execute("""
        CREATE TABLE IF NOT EXISTS catalogue (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            hsn_code   TEXT    DEFAULT '',
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
            qty        REAL    NOT NULL DEFAULT 1,
            price      REAL    NOT NULL DEFAULT 0,
            gst_rate   REAL    NOT NULL DEFAULT 0,

            cgst_rate  REAL    NOT NULL DEFAULT 0,
            sgst_rate  REAL    NOT NULL DEFAULT 0,

            hsn_code   TEXT    DEFAULT '',

            cgst_amt   REAL    NOT NULL DEFAULT 0,
            sgst_amt   REAL    NOT NULL DEFAULT 0,

            gst_amt    REAL    NOT NULL DEFAULT 0,
            total      REAL    NOT NULL DEFAULT 0
        )
    """)

    # Migration for old databases
    add_column_if_missing(conn, "bill_items", "cgst_rate", "REAL DEFAULT 0")
    add_column_if_missing(conn, "bill_items", "sgst_rate", "REAL DEFAULT 0")
    add_column_if_missing(conn, "bill_items", "cgst_amt", "REAL DEFAULT 0")
    add_column_if_missing(conn, "bill_items", "sgst_amt", "REAL DEFAULT 0")
    add_column_if_missing(conn, "settings", "expiry_date", "TEXT DEFAULT NULL")

    conn.commit()
    conn.close()
    print(f"[DB] Initialised -> {DB_PATH}")

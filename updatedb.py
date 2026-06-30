import sqlite3

conn = sqlite3.connect("billease.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("""
    SELECT id, gst_rate, gst_amt
    FROM bill_items
    WHERE cgst_rate = 0 AND sgst_rate = 0
""").fetchall()

for row in rows:
    gst_rate = row["gst_rate"] or 0
    gst_amt = row["gst_amt"] or 0

    cur.execute("""
        UPDATE bill_items
        SET cgst_rate=?,
            sgst_rate=?,
            cgst_amt=?,
            sgst_amt=?
        WHERE id=?
    """, (
        gst_rate / 2,
        gst_rate / 2,
        gst_amt / 2,
        gst_amt / 2,
        row["id"]
    ))

conn.commit()
conn.close()

print("Updated old bill_items successfully.")
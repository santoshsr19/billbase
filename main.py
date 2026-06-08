from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sqlite3
import os

from database import get_conn, init_db, DB_PATH
from models import (
    SettingsIn, SettingsOut,
    CatalogueItemIn, CatalogueItemOut,
    BillIn, BillOut, BillSummary, BillItemOut,
)
from license import check_license, STATUS_EXPIRED, STATUS_INVALID, STATUS_MISSING

# ── App ───────────────────────────────────────────────
app = FastAPI(title="Sudev's Billing System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend/index.html at root
FRONTEND = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


@app.on_event("startup")
def startup():
    init_db()
    status, expiry, msg = check_license()
    print(f"\n[LICENSE] Status: {status.upper()} — {msg}\n")


@app.get("/", response_class=HTMLResponse)
def root():
    return FileResponse(os.path.join(FRONTEND, "index.html"))


@app.get("/favicon.ico")
def favicon():
    # Return empty response to silence 404 errors
    return {"detail": "No favicon"}


# ── License status endpoint ───────────────────────────
@app.get("/api/license")
def get_license_status():
    status, expiry, message = check_license()
    return {
        "status":  status,
        "expiry":  expiry,
        "message": message,
        "blocked": status in (STATUS_EXPIRED, STATUS_INVALID, STATUS_MISSING),
    }


# ── License guard — blocks writes when expired ────────
def require_valid_license():
    status, _, message = check_license()
    if status in (STATUS_EXPIRED, STATUS_INVALID, STATUS_MISSING):
        raise HTTPException(status_code=403, detail=f"License error: {message}")


# ══════════════════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════════════════

def _next_bill_no(conn) -> str:
    row = conn.execute("SELECT bill_prefix, counter FROM settings s JOIN bill_counter bc ON 1=1").fetchone()
    return f"{row['bill_prefix']}-{str(row['counter']).zfill(4)}"


@app.get("/api/settings", response_model=SettingsOut)
def get_settings():
    conn = get_conn()
    row = conn.execute("""
        SELECT s.*, bc.counter
        FROM settings s JOIN bill_counter bc ON 1=1
    """).fetchone()
    conn.close()
    d = dict(row)
    next_no = f"{d['bill_prefix']}-{str(d['counter']).zfill(4)}"
    return SettingsOut(**{k: d[k] for k in SettingsOut.__fields__ if k in d and k != 'next_bill_no'},
                       next_bill_no=next_no)


@app.put("/api/settings", response_model=SettingsOut)
def update_settings(data: SettingsIn):
    conn = get_conn()
    conn.execute("""
        UPDATE settings SET
            biz_name=?, biz_addr=?, biz_phone=?, biz_email=?,
            biz_gstin=?, bill_prefix=?
        WHERE id=1
    """, (data.biz_name, data.biz_addr, data.biz_phone,
          data.biz_email, data.biz_gstin, data.bill_prefix))
    conn.commit()
    row = conn.execute("SELECT s.*, bc.counter FROM settings s JOIN bill_counter bc ON 1=1").fetchone()
    conn.close()
    d = dict(row)
    next_no = f"{d['bill_prefix']}-{str(d['counter']).zfill(4)}"
    return SettingsOut(**{k: d[k] for k in SettingsOut.__fields__ if k in d and k != 'next_bill_no'},
                       next_bill_no=next_no)


# ══════════════════════════════════════════════════════
#  BILL NUMBER  (atomic – guaranteed no duplicates)
# ══════════════════════════════════════════════════════

@app.get("/api/bills/next-number")
def next_bill_number():
    conn = get_conn()
    row = conn.execute("SELECT s.bill_prefix, bc.counter FROM settings s JOIN bill_counter bc ON 1=1").fetchone()
    conn.close()
    return {"bill_no": f"{row['bill_prefix']}-{str(row['counter']).zfill(4)}"}


# ══════════════════════════════════════════════════════
#  CATALOGUE
# ══════════════════════════════════════════════════════

@app.get("/api/catalogue", response_model=List[CatalogueItemOut])
def list_catalogue():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/catalogue", response_model=CatalogueItemOut, status_code=201)
def add_catalogue(item: CatalogueItemIn):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO catalogue (name, hsn_code, unit, price, gst_rate) VALUES (?,?,?,?,?)",
        (item.name, item.hsn_code, item.unit, item.price, item.gst_rate)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM catalogue WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


@app.put("/api/catalogue/{item_id}", response_model=CatalogueItemOut)
def update_catalogue(item_id: int, item: CatalogueItemIn):
    conn = get_conn()
    conn.execute(
        "UPDATE catalogue SET name=?, hsn_code=?, unit=?, price=?, gst_rate=? WHERE id=?",
        (item.name, item.hsn_code, item.unit, item.price, item.gst_rate, item_id)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM catalogue WHERE id=?", (item_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Item not found")
    return dict(row)


@app.delete("/api/catalogue/{item_id}")
def delete_catalogue(item_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM catalogue WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ══════════════════════════════════════════════════════
#  BILLS
# ══════════════════════════════════════════════════════

def _calc_item(item) -> dict:
    # Price entered by user is GST-INCLUSIVE
    # Calculate: base = price / (1 + gst% / 100)
    # gst_amt = price - base
    total = item.qty * item.price
    if item.gst_rate > 0:
        base = round(total / (1 + item.gst_rate / 100), 2)
        gst_amt = round(total - base, 2)
    else:
        base = total
        gst_amt = 0
    return {
        "name": item.name, "unit": item.unit, "hsn_code": item.hsn_code,
        "qty": item.qty, "price": item.price,
        "gst_rate": item.gst_rate,
        "gst_amt": gst_amt,
        "total": total,
    }


@app.get("/api/bills", response_model=List[BillSummary])
def list_bills(
    search: Optional[str] = Query(None),
    limit:  int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    conn = get_conn()
    q = f"%{search}%" if search else "%"
    rows = conn.execute("""
        SELECT b.id, b.bill_no, b.bill_date, b.cust_name, b.grand_total, b.created_at,
               COUNT(i.id) as item_count
        FROM bills b
        LEFT JOIN bill_items i ON i.bill_id = b.id
        WHERE b.bill_no LIKE ? OR b.cust_name LIKE ?
        GROUP BY b.id
        ORDER BY b.id DESC
        LIMIT ? OFFSET ?
    """, (q, q, limit, offset)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/bills/{bill_id}", response_model=BillOut)
def get_bill(bill_id: int):
    conn = get_conn()
    bill = conn.execute("SELECT * FROM bills WHERE id=?", (bill_id,)).fetchone()
    if not bill:
        conn.close()
        raise HTTPException(404, "Bill not found")
    items = conn.execute("SELECT * FROM bill_items WHERE bill_id=? ORDER BY id", (bill_id,)).fetchall()
    conn.close()
    d = dict(bill)
    d["items"] = [dict(i) for i in items]
    return d


@app.post("/api/bills", response_model=BillOut, status_code=201)
def create_bill(data: BillIn):
    require_valid_license()
    if not data.items:
        raise HTTPException(400, "Bill must have at least one item")

    conn = get_conn()
    try:
        # ── Atomic bill number: lock counter row, increment, use
        conn.execute("BEGIN EXCLUSIVE")
        row = conn.execute("SELECT s.bill_prefix, bc.counter FROM settings s JOIN bill_counter bc ON 1=1").fetchone()
        bill_no = f"{row['bill_prefix']}-{str(row['counter']).zfill(4)}"
        conn.execute("UPDATE bill_counter SET counter = counter + 1 WHERE id=1")

        # ── Compute totals
        calced = [_calc_item(i) for i in data.items]
        subtotal  = round(sum(i["total"] - i["gst_amt"] for i in calced), 2)
        total_gst = round(sum(i["gst_amt"] for i in calced), 2)
        grand     = round(subtotal + total_gst, 2)

        # ── Insert bill
        cur = conn.execute("""
            INSERT INTO bills (bill_no, bill_date, due_date, cust_name, cust_addr,
                               cust_phone, cust_gstin, notes, subtotal, total_gst, grand_total)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (bill_no, data.bill_date, data.due_date, data.cust_name, data.cust_addr,
              data.cust_phone, data.cust_gstin, data.notes, subtotal, total_gst, grand))
        bill_id = cur.lastrowid

        # ── Insert items
        for item in calced:
            conn.execute("""
                INSERT INTO bill_items (bill_id, name, unit, qty, price, gst_rate, hsn_code, gst_amt, total)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (bill_id, item["name"], item["unit"], item["qty"], item["price"],
                  item["gst_rate"], item["hsn_code"], item["gst_amt"], item["total"]))

        conn.commit()
        bill = conn.execute("SELECT * FROM bills WHERE id=?", (bill_id,)).fetchone()
        items = conn.execute("SELECT * FROM bill_items WHERE bill_id=?", (bill_id,)).fetchall()
        conn.close()
        d = dict(bill)
        d["items"] = [dict(i) for i in items]
        return d

    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(500, str(e))


@app.put("/api/bills/{bill_id}", response_model=BillOut)
def update_bill(bill_id: int, data: BillIn):
    require_valid_license()
    conn = get_conn()
    existing = conn.execute("SELECT id FROM bills WHERE id=?", (bill_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(404, "Bill not found")
    try:
        conn.execute("BEGIN")
        calced    = [_calc_item(i) for i in data.items]
        subtotal  = round(sum(i["total"] - i["gst_amt"] for i in calced), 2)
        total_gst = round(sum(i["gst_amt"] for i in calced), 2)
        grand     = round(subtotal + total_gst, 2)

        conn.execute("""
            UPDATE bills SET
                bill_date=?, due_date=?, cust_name=?, cust_addr=?,
                cust_phone=?, cust_gstin=?, notes=?,
                subtotal=?, total_gst=?, grand_total=?,
                updated_at=datetime('now','localtime')
            WHERE id=?
        """, (data.bill_date, data.due_date, data.cust_name, data.cust_addr,
              data.cust_phone, data.cust_gstin, data.notes,
              subtotal, total_gst, grand, bill_id))

        conn.execute("DELETE FROM bill_items WHERE bill_id=?", (bill_id,))
        for item in calced:
            conn.execute("""
                INSERT INTO bill_items (bill_id, name, unit, qty, price, gst_rate, hsn_code, gst_amt, total)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (bill_id, item["name"], item["unit"], item["qty"], item["price"],
                  item["gst_rate"], item["hsn_code"], item["gst_amt"], item["total"]))

        conn.commit()
        bill  = conn.execute("SELECT * FROM bills WHERE id=?", (bill_id,)).fetchone()
        items = conn.execute("SELECT * FROM bill_items WHERE bill_id=?", (bill_id,)).fetchall()
        conn.close()
        d = dict(bill)
        d["items"] = [dict(i) for i in items]
        return d

    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(500, str(e))


@app.delete("/api/bills/{bill_id}")
def delete_bill(bill_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM bills WHERE id=?", (bill_id,))
    conn.commit()
    conn.close()
    return {"ok": True}


# ══════════════════════════════════════════════════════
#  REPORTS
# ══════════════════════════════════════════════════════

@app.get("/api/reports/summary")
def report_summary(month: Optional[str] = Query(None, description="YYYY-MM")):
    conn = get_conn()
    if month:
        rows = conn.execute("""
            SELECT COUNT(*) as total_bills,
                   SUM(grand_total) as total_revenue,
                   SUM(total_gst) as total_gst,
                   SUM(subtotal) as total_subtotal
            FROM bills
            WHERE strftime('%Y-%m', bill_date) = ?
        """, (month,)).fetchone()
    else:
        rows = conn.execute("""
            SELECT COUNT(*) as total_bills,
                   SUM(grand_total) as total_revenue,
                   SUM(total_gst) as total_gst,
                   SUM(subtotal) as total_subtotal
            FROM bills
        """).fetchone()
    conn.close()
    return dict(rows)
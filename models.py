from pydantic import BaseModel
from typing import Optional, List


# ── Settings ──────────────────────────────────────────
class SettingsIn(BaseModel):
    biz_name: str = ""
    biz_addr: str = ""
    biz_phone: str = ""
    biz_email: str = ""
    biz_gstin: str = ""
    bill_prefix: str = "INV"


class SettingsOut(SettingsIn):
    next_bill_no: str = ""


# ── Catalogue ─────────────────────────────────────────
class CatalogueItemIn(BaseModel):
    name: str
    hsn_code: str = ""
    price: float = 0
    gst_rate: float = 18


class CatalogueItemOut(CatalogueItemIn):
    id: int
    created_at: Optional[str] = None


# ── Bill items ────────────────────────────────────────
class BillItemIn(BaseModel):
    name: str
    qty: float = 1
    price: float = 0
    gst_rate: float = 0
    hsn_code: str = ""


class BillItemOut(BillItemIn):
    id: int
    bill_id: int

    cgst_rate: float = 0
    sgst_rate: float = 0

    cgst_amt: float = 0
    sgst_amt: float = 0

    gst_amt: float
    total: float


# ── Bills ─────────────────────────────────────────────
class BillIn(BaseModel):
    bill_date: Optional[str] = None
    due_date: Optional[str] = None
    cust_name: str
    cust_addr: str = ""
    cust_phone: str = ""
    cust_gstin: str = ""
    notes: str = ""
    items: List[BillItemIn]


class BillOut(BaseModel):
    id: int
    bill_no: str
    bill_date: Optional[str]
    due_date: Optional[str]
    cust_name: str
    cust_addr: str
    cust_phone: str
    cust_gstin: str
    notes: str
    subtotal: float
    total_gst: float
    grand_total: float
    created_at: Optional[str]
    updated_at: Optional[str]
    items: List[BillItemOut] = []


class BillSummary(BaseModel):
    id: int
    bill_no: str
    bill_date: Optional[str]
    cust_name: str
    grand_total: float
    item_count: int
    created_at: Optional[str]
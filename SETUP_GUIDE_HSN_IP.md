# Sudev's Billing System — Complete Setup Guide

## What Changed

### 1. HSN Code Support
- Each item now has an HSN (Harmonized System of Nomenclature) code
- HSN displays in invoices
- Optional field (can be blank)

### 2. Smart Startup (No Repeated Installs)
- First run: Creates venv + installs requirements (~30 seconds)
- Next runs: Uses existing venv, skips pip install (~5 seconds)
- Only reinstalls if you manually delete venv folder

### 3. IP Display + Hostname
- Shows your PC's local IP address when server starts
- Also shows `sudev-pc.local` (works on any WiFi - no IP needed)
- Staff can scan QR code or type the URL

---

## Critical: Delete Old Database

**IMPORTANT:** The database structure changed to add HSN column.

### Do This FIRST:

1. **Stop the server** (Ctrl+C if running)
2. **Go to billease folder**
3. **Delete `billease.db` file** (if it exists)
   - This forces recreation with new HSN column
   - If you need old bills, backup `billease.db` first
4. **Proceed with file updates below**

---

## How to Update

### Option A: Replace Individual Files (Quickest)

1. **Stop server** (Ctrl+C)
2. **Download these 6 files:**
   - `main.py`
   - `models.py`
   - `database.py`
   - `index.html`
   - `start.bat` (Windows)
   - `start.sh` (Mac/Linux)

3. **Replace in billease folder:**
   ```
   billease/
   ├── main.py              ← Replace
   ├── models.py            ← Replace
   ├── database.py          ← Replace
   ├── start.bat            ← Replace (Windows)
   ├── start.sh             ← Replace (Mac/Linux)
   └── frontend/
       └── index.html       ← Replace
   ```

4. **Delete `billease.db`** (if exists)

5. **Restart server** (double-click `start.bat` or `./start.sh`)

### Option B: Extract Fresh Zip

1. Delete old billease folder completely
2. Extract new billease.zip
3. Double-click `start.bat`

---

## When You Start the Server

**You will see:**

```
=====================================================
 Sudev's Billing System
=====================================================

[OK] Virtual environment exists - using existing installation
[STARTUP] Starting server...

=====================================================
[OK] Server running
=====================================================

COPY THIS URL AND SEND TO STAFF:

   http://192.168.1.100:8000

OR use this (works on any WiFi):

   http://sudev-pc.local:8000

To generate QR code, visit:
   https://qr-code-generator.com/
   Paste: http://192.168.1.100:8000

=====================================================

Press Ctrl+C to stop the server
```

---

## For Your Staff Member

### Option 1: Use Hostname (Recommended - No IP Changes)
1. **Tell them once:** "Use this URL: `http://sudev-pc.local:8000`"
2. **This works forever** - even if your IP changes
3. They just bookmark it

### Option 2: Use IP Address (Changes Daily)
1. Each morning when you start server, the IP displays
2. Send them the IP in WhatsApp/message
3. They type: `http://YOUR_IP:8000` (e.g., `http://192.168.1.100:8000`)

### Option 3: Use QR Code
1. When server starts, see the IP address
2. Go to: https://qr-code-generator.com/
3. Paste the URL: `http://YOUR_IP:8000`
4. Generate QR code
5. Staff scans it with phone camera
6. Click the link in the notification

---

## Using HSN Code

### Adding HSN to Products

**In the bill form, you'll now see:**
```
Item Name | HSN Code | Unit | Qty | Price | GST% | Delete
```

**Example:**
```
Rice 1kg    | 1001  | kg | 1 | 118 | 5% | ✕
Cotton      | 5208  | m  | 5 | 200 | 12%| ✕
```

### In Invoice

Invoice will display:
```
#  Item      HSN    Unit  Qty  Rate   GST%  GST Amt  Total
1  Rice 1kg  1001   kg    1    100    5%    5        105
2  Cotton    5208   m     5    190    12%   38       228
```

### Where to Find HSN Codes

Common Indian HSN codes:
- **1001** - Rice
- **1005** - Wheat/Flour
- **1201** - Soybeans
- **5208** - Cotton fabric
- **2106** - Food supplements
- **9999** - Other

Ask your accountant or check: https://www.cbic.gov.in/

---

## Troubleshooting

### "Unprocessable Entity" Error
**Cause:** Old database format incompatible with HSN changes
**Fix:** Delete `billease.db` and restart server (it recreates fresh)

### Form Fields Are Compressed
**Cause:** Browser cached old CSS
**Fix:** Hard refresh (Ctrl+F5 or Cmd+Shift+R on Mac)

### Server Still Installing Dependencies
**Cause:** First run takes longer
**Fix:** Wait 30 seconds, it only happens once

### Next Runs Are Slow (IP Takes 5 Seconds)
**Cause:** Getting IP address from system
**Fix:** Normal - just let it finish

### "sudev-pc.local" Doesn't Work
**Cause:** mDNS not available on network
**Fix:** Use the IP address instead (shown in terminal)

---

## Daily Workflow

### Morning
1. Double-click `start.bat`
2. Wait for server to start
3. See the IP/URL displayed
4. Send to staff or they use `sudev-pc.local:8000`

### During Day
- Staff creates bills on their phone
- All saved to your PC's database

### Evening
1. Close the `start.bat` window (Ctrl+C)
2. Server stops
3. All data is saved in `billease.db`

### Backup
1. Copy `billease.db` to USB/Google Drive weekly
2. That's your complete backup

---

## Complete List of Files (What Changed)

| File | What Changed |
|---|---|
| `main.py` | Added HSN code handling in database inserts |
| `models.py` | Added `hsn_code` field to BillItemIn/Out |
| `database.py` | Added `hsn_code` column to bill_items table |
| `index.html` | Added HSN field to form + invoice + IP display logic |
| `start.bat` | Skip pip if venv exists + show IP address |
| `start.sh` | Skip pip if venv exists + show IP address |

---

## Support

- Delete old `billease.db` if you get errors
- Hard refresh browser (Ctrl+F5) if UI looks wrong
- First startup is slow (~30 sec), next ones are fast (~5 sec)

You're good to go! 🎯

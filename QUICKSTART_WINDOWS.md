# Sudev's Billing System — Quick Start (Windows)

## One-Time Setup

### 1. Download & Extract
- Download `billease.zip`
- Right-click → Extract All
- Open the extracted `billease` folder

### 2. Install Python (if not already done)
- Go to https://www.python.org/downloads
- Download **Python 3.9 or higher**
- Run installer
- ⭐ **IMPORTANT**: Check "Add Python to PATH" 
- Click Install

### 3. Start the Server
- Inside the `billease` folder, double-click **`start.bat`**
- Wait ~30 seconds (first time takes longer)
- A browser window opens automatically
- Done! ✅

That's it. The script handles:
- ✅ Creating virtual environment
- ✅ Installing all dependencies
- ✅ Starting the server
- ✅ Opening your browser

---

## On Your Phone (Same WiFi)

### First Time:
1. Open phone browser (Chrome, Safari, etc.)
2. Find your PC's IP:
   - Press `Windows + R`
   - Type: `cmd`
   - Type: `ipconfig`
   - Look for "IPv4 Address" (e.g., `192.168.1.100`)

3. In phone browser, type: `http://192.168.1.100:8000`
4. **Bookmark it** for next time

### Next Times:
- Just open the bookmark and start billing!

---

## If Something Goes Wrong

### "Python not found"
- You skipped Python installation
- Go to https://python.org and install it
- **During install, check "Add Python to PATH"**
- Restart your PC
- Try `start.bat` again

### "Port already in use"
- Another app is using port 8000
- Open `start.bat` in a text editor
- Change `--port 8000` to `--port 8080`
- Save and run again
- On phone, use: `http://192.168.x.x:8080`

### "Requirements installation fails"
- Your internet might be slow
- The script will auto-retry
- Be patient, first run can take 2–3 minutes

---

## Daily Usage

**Every day, just:**
1. Double-click `start.bat` in the morning
2. Open phone browser to `http://192.168.x.x:8000`
3. Billing app is ready
4. Close the `start.bat` window at night to stop server

---

## License Key

First time you run it, you'll see:
```
license.txt not found. Contact Sudev for a license key.
```

- You'll receive a key from Sudev (looks like: `SUDEV-20261207-A1A5AF`)
- Open `license.txt` in the `billease` folder
- Paste the key there
- Save and reload browser
- Done! ✅

---

## Backup Your Data

Your data is in: `billease.db` (in the billease folder)

**Weekly, copy `billease.db` to:**
- USB drive
- Google Drive
- OneDrive

If something breaks, just copy the backup back and you're good!

---

**Questions?** Contact Sudev.

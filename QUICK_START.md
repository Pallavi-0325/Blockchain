# Quick Start - Data Persistence Setup

## 🚀 Get Started in 2 Steps

### Step 1: Initialize Database (First Time Only)
```bash
python setup_database.py
```
**What this does:**
- Creates database tables (patients, doctors, consents, documents, access_logs)
- Verifies database connection
- Adds sample data for testing
- Shows success status

**Expected Output:**
```
✓ Database schema initialized successfully!
✓ Table 'patients' exists
✓ Table 'doctors' exists
✓ Table 'consents' exists
✓ Table 'documents' exists
✓ Table 'access_logs' exists
✓ Sample data population complete!
```

### Step 2: Run the Application
```bash
python app.py
```
**What happens:**
- Flask automatically initializes database on startup
- All user operations will persist to database
- Server runs on http://localhost:5001

---

## ✅ What's Now Permanently Stored

### Patient Actions
- ✓ Consent grants/revokes (in `consents` table)
- ✓ Document uploads (in `documents` table)
- ✓ Profile updates (in `patients` table)

### Doctor Actions
- ✓ Document access (in `access_logs` table)
- ✓ Patient data retrieval logged

### System Data
- ✓ Login history (in blockchain + Flask logs)
- ✓ Access audit trail (in `access_logs` table)

---

## 🔍 Verify Data Persistence

### In Database
```sql
-- Check stored consents
SELECT * FROM consents;

-- Check uploaded documents
SELECT * FROM documents;

-- Check access logs
SELECT * FROM access_logs;
```

### In Application
1. **Patient Dashboard** → Grant consent to doctor → Data saved ✓
2. **Upload Document** → File + metadata stored ✓
3. **Doctor Dashboard** → Access logs recorded ✓

---

## ⚙️ Database Connection Details
**File:** `db_utils.py`
- Host: sdb-a.hosting.stackcp.net
- Port: 41884
- Database: pallavi-3136370892
- User: pallavi

---

## ❓ Common Issues & Solutions

### Issue: "Unknown database" error
**Solution:**
```bash
python setup_database.py
```

### Issue: Tables not created
**Solution:** Check MySQL is running, then run setup script again

### Issue: Data not saving
**Solution:** Verify MySQL connection in `db_utils.py` has correct credentials

---

## 📚 For More Details
See: `DATABASE_SETUP_GUIDE.md` for complete documentation

---

**Status:** ✅ Data persistence is now fully implemented and ready to use!

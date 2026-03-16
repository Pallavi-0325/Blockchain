# Healthcare Blockchain Consent Management System - Setup Guide

## Overview
This application implements a blockchain-based healthcare consent management system with permanent data storage in MySQL. All operations are logged and persisted to ensure data durability.

## Database Architecture

### Tables Created
1. **patients** - Patient information and medical history
2. **doctors** - Doctor profiles and specializations
3. **consents** - Consent records between patients and healthcare providers
4. **documents** - Uploaded medical documents metadata
5. **access_logs** - Audit trail for all document access and operations

### Data Persistence Features
- ✓ Automatic database initialization on Flask app startup
- ✓ Consent operations (grant/revoke) stored permanently
- ✓ Document uploads tracked with metadata
- ✓ Access logs maintain audit trail
- ✓ Patient and doctor data synchronized with blockchain

## Quick Start

### 1. First-Time Setup
Run the database initialization script **before** starting the app:

```bash
python setup_database.py
```

This will:
- Create all required database tables
- Verify database connectivity
- Populate sample data for testing
- Display setup completion status

### 2. Run the Flask Application
The app will automatically initialize the database tables on startup:

```bash
python app.py
```

The Flask server will:
- Verify database connection
- Create tables if they don't exist
- Be ready to accept requests on `http://localhost:5001`

## What Gets Stored

### Patient Operations
- **Profile Updates** - Stored in `patients` table
- **Consent Grants** - Recorded in `consents` table with status='granted'
- **Consent Revocations** - Recorded in `consents` table with status='revoked'
- **Document Uploads** - Metadata stored in `documents` table

### Doctor Operations
- **Access Requests** - Timestamp and status in blockchain
- **Document Access** - Logged in `access_logs` table
- **Patient Records** - Stored in database for quick retrieval

### Audit Trail
- **Access Logs** - All document views recorded with:
  - Doctor address
  - Patient address
  - Resource ID
  - Timestamp
  - Action type

## Database Configuration

The database credentials are configured in `db_utils.py`:

```python
connection = mysql.connector.connect(
    host='sdb-a.hosting.stackcp.net',
    port=41884,
    user='pallavi',
    password='S@i85t@run',
    database='pallavi-3136370892'
)
```

**To use a different database:**
1. Edit the connection parameters in `db_utils.py`
2. Run `python setup_database.py` to initialize the new database
3. Start the app with `python app.py`

## Troubleshooting

### Database Connection Issues
```
Error: Unknown database
```
**Solution:** Ensure the database name exists in your MySQL server, or the script will attempt to create it automatically.

### Tables Not Created
**Solution:** Run `python setup_database.py` manually to initialize the schema.

### Data Not Persisting
**Solution:** 
1. Verify MySQL server is running
2. Check database credentials in `db_utils.py`
3. Ensure your database user has CREATE, INSERT, UPDATE permissions
4. Check Flask application logs for database errors

### Permission Denied
**Solution:** Grant necessary privileges to your database user:
```sql
GRANT ALL PRIVILEGES ON pallavi-3136370892.* TO 'pallavi'@'host';
FLUSH PRIVILEGES;
```

## Data Flow

```
User Action (Web UI)
        ↓
    Flask Route Handler
        ↓
    Blockchain Transaction (Smart Contract)
        ↓
    Database Insert/Update
        ↓
    ✓ Data Persisted (Dual Storage)
```

## Backup & Maintenance

### Regular Backups
Export your database regularly:

```bash
mysqldump -h sdb-a.hosting.stackcp.net -P 41884 -u pallavi -p pallavi-3136370892 > backup.sql
```

### Check Database Size
```sql
SELECT TABLE_NAME, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS SIZE_MB 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'pallavi-3136370892';
```

## API Endpoints & Data Persistence

### Patient Dashboard
- `POST /patient` (grant consent) → Stored in `consents` table
- `POST /patient` (revoke consent) → Updated in `consents` table
- `POST /patient` (upload document) → Metadata in `documents` table
- `POST /patient` (update profile) → Updated in `patients` table

### Doctor Dashboard
- `POST /doctor/view_documents/<patient>` → Logged in `access_logs` table
- `POST /api/access_record` → Audit trail recorded

### Admin Dashboard
- `POST /admin` (upload for patient) → Document stored

## Sample Database Queries

### View all consents for a patient
```sql
SELECT doctor_address, status, timestamp 
FROM consents 
WHERE patient_address = '0x2' 
ORDER BY timestamp DESC;
```

### Check access history for a patient
```sql
SELECT doctor_address, action, access_timestamp 
FROM access_logs 
WHERE patient_address = '0x2' 
ORDER BY access_timestamp DESC;
```

### List all documents uploaded by a patient
```sql
SELECT document_name, file_path, upload_timestamp 
FROM documents 
WHERE patient_address = '0x2' 
ORDER BY upload_timestamp DESC;
```

### Verify data persistence
```sql
SELECT 
  (SELECT COUNT(*) FROM patients) as patient_count,
  (SELECT COUNT(*) FROM doctors) as doctor_count,
  (SELECT COUNT(*) FROM consents) as consent_count,
  (SELECT COUNT(*) FROM documents) as document_count,
  (SELECT COUNT(*) FROM access_logs) as access_log_count;
```

## Important Notes

⚠️ **Data Synchronization**: The application maintains data in both:
1. **Blockchain** (Smart Contract) - For immutability and trust
2. **MySQL Database** - For quick queries and indexing

⚠️ **Blockchain is Source of Truth**: In case of conflicts, blockchain records are the authoritative source. Database serves as a cache/index.

⚠️ **Backups**: Always backup your MySQL database regularly. Smart contract data is immutable but database data requires traditional backup procedures.

## Support & Debugging

Enable debug mode in Flask to see detailed database operations:
```python
# In app.py
app.run(debug=True)
```

Check Flask logs for:
- Database connection issues
- Query execution errors
- Transaction failures
- Data insertion/update problems

All database operations will print success/failure messages to the console.

---

**Last Updated:** February 2026

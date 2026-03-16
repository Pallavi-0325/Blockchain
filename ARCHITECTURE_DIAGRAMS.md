# Data Persistence Architecture - Visual Diagrams

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WEB APPLICATION LAYER                        │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐   │
│  │   Patient    │  │    Doctor    │  │  Admin & Other Users   │   │
│  │  Dashboard   │  │  Dashboard   │  │     Dashboards         │   │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬───────────┘   │
│         │                 │                       │                │
└──────────────────────────┼───────────────────────┼────────────────┘
          │                 │                       │
          └─────────────────┼───────────────────────┘
                            │
          ┌─────────────────▼──────────────────────┐
          │      FLASK APPLICATION (app.py)        │
          │  - Route handling                      │
          │  - Business logic                      │
          │  - Data validation                     │
          └────┬───────────────────────┬───────────┘
               │                       │
       ┌───────▼─────────┐     ┌───────▼──────────┐
       │   BLOCKCHAIN    │     │  MYSQL DATABASE  │
       │  (Smart         │     │  (Storage        │
       │   Contract)     │     │   & Cache)       │
       │                 │     │                  │
       │ ✓ Immutable     │     │ ✓ Indexed        │
       │ ✓ Trust         │     │ ✓ Queryable      │
       │ ✓ Auditable     │     │ ✓ Persistent     │
       └─────────────────┘     └──────────────────┘
```

---

## 2. Data Flow - Patient Grants Consent

```
PATIENT DASHBOARD
        │
        ├─→ User clicks "Grant Consent"
        │
    POST /patient
        │
        └─→ Flask route handler
            │
            ├─→ Blockchain: contract.functions.grantConsent(doctor)
            │   └─→ Execute transaction
            │   └─→ Wait for receipt
            │
            ├─→ Database: INSERT INTO consents
            │   (patient_address, doctor_address, 'granted', NOW())
            │
            └─→ Redirect to dashboard
                │
                ✓ Data persisted in BOTH systems
                ✓ Blockchain transaction hash stored
                ✓ Database record with timestamp
```

---

## 3. Data Flow - Document Upload

```
PATIENT DASHBOARD
        │
        ├─→ User uploads file
        │
    POST /patient (upload_document)
        │
        └─→ Flask route handler
            │
            ├─→ Save file locally
            │   (static/uploads/filename.pdf)
            │
            ├─→ Blockchain: contract.functions.uploadDocument(...)
            │   └─→ Record document metadata on chain
            │
            ├─→ Database: INSERT INTO documents
            │   (patient_address, document_name, file_path, 
            │    uploader, NOW())
            │
            └─→ Redirect to dashboard
                │
                ✓ File stored on server
                ✓ Blockchain record created
                ✓ Database metadata stored
                ✓ Three-tier storage system active
```

---

## 4. Data Flow - Doctor Accesses Records

```
DOCTOR DASHBOARD
        │
        ├─→ Doctor views patient documents
        │
    GET /doctor/view_documents/<patient>
        │
        └─→ Flask route handler
            │
            ├─→ Check consent in blockchain
            │   └─→ contract.functions.checkConsent(patient, doctor)
            │
            ├─→ If consented:
            │   ├─→ Fetch documents from blockchain
            │   │
            │   ├─→ Log access to blockchain
            │   │   └─→ contract.functions.logAccess(patient, resource)
            │   │
            │   ├─→ Database: INSERT INTO access_logs
            │   │   (doctor_address, patient_address, resource_id, 
            │   │    action, NOW())
            │   │
            │   └─→ Render template with documents
            │
            └─→ If not consented: Access Denied
                │
                ✓ Consent verified on blockchain
                ✓ Access logged on blockchain
                ✓ Access logged to database (audit trail)
```

---

## 5. Database Schema Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   MYSQL DATABASE                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │   patients   │  │    doctors   │  │    consents    │   │
│  ├──────────────┤  ├──────────────┤  ├────────────────┤   │
│  │ id (PK)      │  │ id (PK)      │  │ id (PK)        │   │
│  │ name         │  │ name         │  │ patient_addr ✓│   │
│  │ age          │  │ specialization│ │ doctor_addr  ✓│   │
│  │ gender       │  │ phone        │  │ status         │   │
│  │ address      │  │ blockchain_..│  │ timestamp   ✓ │   │
│  │ phone        │  │              │  │ UNIQUE (p,d)  │   │
│  │ medical_hist │  │              │  └────────────────┘   │
│  │ blockchain_..│  │              │                       │
│  └──────────────┘  └──────────────┘                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │  documents   │  │ access_logs  │                       │
│  ├──────────────┤  ├──────────────┤                       │
│  │ id (PK)      │  │ id (PK)      │                       │
│  │ patient_addr ✓  │ doctor_addr  │                       │
│  │ doc_name     │  │ patient_addr ✓                       │
│  │ file_path    │  │ resource_id  │                       │
│  │ uploader     │  │ action       │                       │
│  │ upload_ts ✓ │  │ access_ts  ✓ │                       │
│  └──────────────┘  └──────────────┘                       │
│                                                              │
│  Legend: PK = Primary Key, ✓ = Indexed                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Dual Storage Strategy

```
                    USER ACTION
                        │
                        ▼
                  ┌────────────┐
                  │Flask Route │
                  └────┬───────┘
                       │
         ┌─────────────┴──────────────┐
         │                            │
         ▼                            ▼
    ┌─────────────┐            ┌──────────────┐
    │ BLOCKCHAIN  │            │ MYSQL DB     │
    ├─────────────┤            ├──────────────┤
    │ • Immutable │            │ • Indexed    │
    │ • Auditable │            │ • Queryable  │
    │ • Trust     │            │ • Fast       │
    │ • Permanent │            │ • Backupable │
    │ • Smart     │            │ • Scalable   │
    │   Contract  │            │ • Reports    │
    └─────────────┘            └──────────────┘
         │                            │
         └─────────────┬──────────────┘
                       │
                    ✓ Data Persisted
                   (Both Systems)
                       │
              ┌────────┴────────┐
              │                 │
        ✓ Security      ✓ Performance
        ✓ Trust         ✓ Queries
        ✓ Immutability  ✓ Analytics
```

---

## 7. Request Lifecycle

```
                    ┌─────────────────┐
                    │   HTTP Request  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Flask Route    │
                    │  Handler        │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
      ┌─────▼─────┐    ┌─────▼─────┐   ┌────▼─────┐
      │ Validate  │    │ Blockchain│   │Database  │
      │ Request   │    │ Operation │   │Operation │
      └─────┬─────┘    └─────┬─────┘   └────┬─────┘
            │                │              │
            └────────────────┼──────────────┘
                             │
                    ┌────────▼────────┐
                    │ Commit Changes  │
                    │ • Blockchain TX │
                    │ • DB INSERT     │
                    │ • Timestamps    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  HTTP Response  │
                    │  ✓ Success      │
                    └─────────────────┘
```

---

## 8. Consent Management Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  CONSENT LIFECYCLE                          │
└─────────────────────────────────────────────────────────────┘

Initial State:
    Patient    Doctor
      ●         ○  (No connection)

Step 1: Patient Grants Consent
    ┌────────────────────┐
    │ INSERT INTO consents│
    │ status='granted'    │
    │ timestamp=NOW()     │
    └────────────────────┘
        Patient    Doctor
         ●——●——●—●—○  (Consent granted)

Step 2: Doctor Accesses Records
    ┌────────────────────┐
    │ INSERT INTO        │
    │ access_logs        │
    │ action='ACCESS'    │
    │ timestamp=NOW()    │
    └────────────────────┘
        Patient    Doctor
         ●—●—●—●—●—●—○  (Recorded access)

Step 3: Patient Revokes Consent
    ┌────────────────────┐
    │ UPDATE consents    │
    │ status='revoked'   │
    │ timestamp=NOW()    │
    └────────────────────┘
        Patient    Doctor
         ●///●///●——○  (Revoked, access denied)

Database Records:
    consents table:
    | id | patient | doctor | status   | timestamp         |
    |----|---------|--------|----------|-------------------|
    | 1  | 0x2     | 0x3    | granted  | 2026-02-10 10:00 |
    | 2  | 0x2     | 0x3    | revoked  | 2026-02-10 11:30 |

    access_logs table:
    | id | doctor | patient | action  | access_timestamp  |
    |----|--------|---------|---------|-------------------|
    | 1  | 0x3    | 0x2     | VIEW    | 2026-02-10 10:05 |
    | 2  | 0x3    | 0x2     | VIEW    | 2026-02-10 10:15 |
```

---

## 9. Indexing Strategy

```
                    QUERY PERFORMANCE OPTIMIZATION
                              │
                ┌─────────────┼─────────────┐
                │             │             │
          ┌─────▼────┐  ┌────▼──────┐  ┌──▼────────┐
          │ consents  │  │ documents │  │access_logs│
          │  TABLE    │  │  TABLE    │  │  TABLE    │
          └─────┬────┘  └────┬──────┘  └──┬────────┘
                │             │            │
           ┌────┴─────┐   ┌───┴────┐  ┌───┴──────┐
           │           │   │        │  │          │
        idx_patient  idx_  idx_     idx_        idx_
           _address    doctor_patient timestamp   doctor
           
           Creates:
           ✓ Fast lookups by patient
           ✓ Fast lookups by doctor
           ✓ Fast date range queries
           ✓ Unique constraint checks
           ✓ JOIN performance boost
```

---

## 10. Setup & Initialization Flow

```
┌──────────────────────────────────────────────────────┐
│         APPLICATION STARTUP SEQUENCE                 │
└──────────────────────────────────────────────────────┘

Developer:
    python setup_database.py  (First time only)
           │
           ├─→ Create all tables
           ├─→ Add indexes
           ├─→ Insert sample data
           └─→ Verify success
                   │
                   ✓ Ready for use

            python app.py  (Every time)
           │
           ├─→ Initialize Flask
           ├─→ Check database connection
           ├─→ Run init_db() (auto-create tables)
           ├─→ Load blockchain connection
           └─→ Start server on :5001
                   │
                   ✓ Ready to accept requests

User:
            Browser: http://localhost:5001
           │
           ├─→ Login
           ├─→ Perform actions
           │   ├─→ Grant consent
           │   ├─→ Upload document
           │   └─→ Access records
           │
           └─→ Data saved to:
               ├─→ Blockchain (immutable)
               └─→ Database (queryable)
```

---

## 11. Error Handling & Recovery

```
ERROR SCENARIOS & HANDLING

Scenario 1: Database Connection Fails
    │
    ├─→ Try to connect
    ├─→ Connection fails
    ├─→ Log error
    ├─→ Flask app starts anyway (with warning)
    └─→ Operations fail gracefully with error messages

Scenario 2: Blockchain Transaction Fails
    │
    ├─→ Initiate transaction
    ├─→ Transaction reverts
    ├─→ Log error
    ├─→ Skip database insert (stay in sync)
    └─→ Notify user of failure

Scenario 3: Database Insert Fails
    │
    ├─→ Blockchain transaction succeeds
    ├─→ Database insert fails
    ├─→ Log error for manual recovery
    ├─→ Data available from blockchain
    └─→ Manual database sync possible via SQL
```

---

## 12. Complete Data Lifecycle

```
┌────────────────────────────────────────────────────────────┐
│              DATA LIFECYCLE VISUALIZATION                  │
└────────────────────────────────────────────────────────────┘

CREATE:
    User Action → Blockchain TX → DB INSERT → ✓ Stored

READ:
    User Request → Blockchain Call → DB Query → Display

UPDATE:
    User Action → Blockchain TX → DB UPDATE → ✓ Persisted

DELETE:
    User Action → Blockchain (immutable) → DB DELETE → Archived

ARCHIVE:
    Old Records → Backup → Storage → Compliance

AUDIT:
    Every Action → Blockchain Record → DB Timestamp → Trail
```

---

## Summary of Architecture Benefits

```
┌─────────────────────────────────────────────────────────────┐
│                        BENEFITS                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  BLOCKCHAIN:              DATABASE:                         │
│  ✓ Immutable              ✓ Queryable                      │
│  ✓ Auditable              ✓ Indexed                        │
│  ✓ Distributed            ✓ Fast retrieval                 │
│  ✓ Trustless              ✓ Backup/restore                 │
│  ✓ Smart contracts        ✓ Analytics ready                │
│                                                              │
│  COMBINED:                                                  │
│  ✓ Complete audit trail                                    │
│  ✓ High performance                                        │
│  ✓ Trust + speed                                           │
│  ✓ Redundancy                                              │
│  ✓ Compliance ready                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Visual diagrams complete. Refer to these for understanding the architecture.**

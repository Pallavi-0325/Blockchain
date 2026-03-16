-- ============================================================================
-- HEALTHCARE BLOCKCHAIN DATABASE - USEFUL SQL QUERIES
-- ============================================================================

-- Database: pallavi-3136370892

-- ============================================================================
-- 1. DATA VERIFICATION QUERIES
-- ============================================================================

-- Check all table row counts
SELECT 
  (SELECT COUNT(*) FROM patients) as patients_count,
  (SELECT COUNT(*) FROM doctors) as doctors_count,
  (SELECT COUNT(*) FROM consents) as consents_count,
  (SELECT COUNT(*) FROM documents) as documents_count,
  (SELECT COUNT(*) FROM access_logs) as access_logs_count;

-- List all tables in database
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'pallavi-3136370892';

-- ============================================================================
-- 2. PATIENT QUERIES
-- ============================================================================

-- View all patients
SELECT id, name, age, gender, address, phone, blockchain_account 
FROM patients 
ORDER BY name;

-- Get specific patient by address
SELECT * FROM patients 
WHERE blockchain_account = '0x2';

-- Get patient by name
SELECT * FROM patients 
WHERE name LIKE '%John%';

-- ============================================================================
-- 3. DOCTOR QUERIES
-- ============================================================================

-- View all doctors
SELECT id, name, specialization, phone, blockchain_account 
FROM doctors 
ORDER BY name;

-- Get doctors by specialization
SELECT * FROM doctors 
WHERE specialization = 'Cardiologist';

-- Get specific doctor
SELECT * FROM doctors 
WHERE blockchain_account = '0x2';

-- ============================================================================
-- 4. CONSENT QUERIES
-- ============================================================================

-- View all active consents for a patient
SELECT doctor_address, status, timestamp 
FROM consents 
WHERE patient_address = '0x2' 
AND status = 'granted'
ORDER BY timestamp DESC;

-- View all consents (granted and revoked) for a patient
SELECT doctor_address, status, timestamp 
FROM consents 
WHERE patient_address = '0x2' 
ORDER BY timestamp DESC;

-- Get consent status between specific patient and doctor
SELECT status, timestamp 
FROM consents 
WHERE patient_address = '0x2' 
AND doctor_address = '0x3';

-- View all doctors who have consent from a patient
SELECT DISTINCT doctor_address, status 
FROM consents 
WHERE patient_address = '0x2' 
AND status = 'granted';

-- View consent history (latest action for each doctor pair)
SELECT patient_address, doctor_address, status, MAX(timestamp) as last_action
FROM consents 
GROUP BY patient_address, doctor_address
ORDER BY last_action DESC;

-- ============================================================================
-- 5. DOCUMENT QUERIES
-- ============================================================================

-- View all documents uploaded by a patient
SELECT document_name, file_path, uploader, upload_timestamp 
FROM documents 
WHERE patient_address = '0x2' 
ORDER BY upload_timestamp DESC;

-- Get document by name
SELECT * FROM documents 
WHERE document_name LIKE '%Lab%'
ORDER BY upload_timestamp DESC;

-- View documents uploaded in last 7 days
SELECT patient_address, document_name, upload_timestamp 
FROM documents 
WHERE upload_timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY upload_timestamp DESC;

-- Get count of documents per patient
SELECT patient_address, COUNT(*) as document_count 
FROM documents 
GROUP BY patient_address 
ORDER BY document_count DESC;

-- Find documents uploaded by specific person
SELECT * FROM documents 
WHERE uploader = '0x2' 
ORDER BY upload_timestamp DESC;

-- ============================================================================
-- 6. ACCESS LOG QUERIES
-- ============================================================================

-- View all access to a patient's data
SELECT doctor_address, action, access_timestamp 
FROM access_logs 
WHERE patient_address = '0x2' 
ORDER BY access_timestamp DESC;

-- Get access logs for specific doctor
SELECT patient_address, action, access_timestamp 
FROM access_logs 
WHERE doctor_address = '0x3' 
ORDER BY access_timestamp DESC;

-- View access history for last 30 days
SELECT doctor_address, patient_address, action, access_timestamp 
FROM access_logs 
WHERE access_timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY access_timestamp DESC;

-- Get access count per doctor
SELECT doctor_address, COUNT(*) as access_count 
FROM access_logs 
GROUP BY doctor_address 
ORDER BY access_count DESC;

-- Find all accesses to specific patient on specific date
SELECT * FROM access_logs 
WHERE patient_address = '0x2' 
AND DATE(access_timestamp) = '2026-02-10'
ORDER BY access_timestamp DESC;

-- Get access frequency by action type
SELECT action, COUNT(*) as count 
FROM access_logs 
GROUP BY action 
ORDER BY count DESC;

-- ============================================================================
-- 7. COMPLIANCE & AUDIT QUERIES
-- ============================================================================

-- Audit trail: All activities for a patient
SELECT 'consent' as activity_type, doctor_address as actor, patient_address, status as details, timestamp
FROM consents
WHERE patient_address = '0x2'
UNION ALL
SELECT 'document', uploader, patient_address, document_name, upload_timestamp
FROM documents
WHERE patient_address = '0x2'
UNION ALL
SELECT 'access', doctor_address, patient_address, action, access_timestamp
FROM access_logs
WHERE patient_address = '0x2'
ORDER BY 5 DESC;

-- Who accessed patient data (without consent)
SELECT 
    l.doctor_address,
    l.patient_address,
    l.action,
    l.access_timestamp,
    CASE WHEN c.status = 'granted' THEN 'With Consent' ELSE 'NO CONSENT' END as consent_status
FROM access_logs l
LEFT JOIN consents c ON 
    l.patient_address = c.patient_address 
    AND l.doctor_address = c.doctor_address 
    AND c.status = 'granted'
WHERE l.patient_address = '0x2'
ORDER BY l.access_timestamp DESC;

-- ============================================================================
-- 8. STATISTICS & ANALYTICS
-- ============================================================================

-- Get total active consents in system
SELECT COUNT(*) as total_active_consents 
FROM consents 
WHERE status = 'granted';

-- Get average documents per patient
SELECT AVG(doc_count) as avg_documents_per_patient
FROM (
    SELECT patient_address, COUNT(*) as doc_count
    FROM documents
    GROUP BY patient_address
) as subquery;

-- Get most accessed patients
SELECT patient_address, COUNT(*) as access_count 
FROM access_logs 
GROUP BY patient_address 
ORDER BY access_count DESC 
LIMIT 10;

-- Get most active doctors (by access count)
SELECT doctor_address, COUNT(*) as access_count 
FROM access_logs 
GROUP BY doctor_address 
ORDER BY access_count DESC 
LIMIT 10;

-- ============================================================================
-- 9. DATABASE MAINTENANCE QUERIES
-- ============================================================================

-- Get database size
SELECT 
    TABLE_NAME,
    ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS size_mb
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'pallavi-3136370892'
ORDER BY size_mb DESC;

-- Check table integrity
CHECK TABLE patients;
CHECK TABLE doctors;
CHECK TABLE consents;
CHECK TABLE documents;
CHECK TABLE access_logs;

-- ============================================================================
-- 10. DATA CLEANUP QUERIES (USE WITH CAUTION!)
-- ============================================================================

-- Delete all data and reset auto-increment (WARNING: IRREVERSIBLE)
-- TRUNCATE TABLE patients;
-- TRUNCATE TABLE doctors;
-- TRUNCATE TABLE consents;
-- TRUNCATE TABLE documents;
-- TRUNCATE TABLE access_logs;

-- Delete specific consent record
-- DELETE FROM consents 
-- WHERE patient_address = '0x2' 
-- AND doctor_address = '0x3';

-- Delete old access logs (older than 90 days)
-- DELETE FROM access_logs 
-- WHERE access_timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- ============================================================================
-- 11. USER PERMISSION MANAGEMENT
-- ============================================================================

-- Grant all permissions to user (run as admin)
-- GRANT ALL PRIVILEGES ON pallavi-3136370892.* TO 'pallavi'@'localhost';

-- Grant specific permissions (read-only)
-- GRANT SELECT ON pallavi-3136370892.* TO 'readonly_user'@'localhost';

-- Grant insert/update permissions
-- GRANT SELECT, INSERT, UPDATE ON pallavi-3136370892.* TO 'app_user'@'localhost';

-- ============================================================================
-- 12. BACKUP & EXPORT QUERIES
-- ============================================================================

-- Export patients to CSV (run from command line):
-- SELECT * INTO OUTFILE '/tmp/patients.csv'
-- FIELDS TERMINATED BY ','
-- FROM patients;

-- Export access logs to CSV:
-- SELECT * INTO OUTFILE '/tmp/access_logs.csv'
-- FIELDS TERMINATED BY ','
-- FROM access_logs
-- WHERE access_timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY);

-- ============================================================================
-- 13. SAMPLE DATA INSERTION (FOR TESTING)
-- ============================================================================

-- Add test patient
INSERT INTO patients (name, age, gender, address, phone, medical_history, blockchain_account)
VALUES ('Test Patient', 40, 'Male', '999 Test St', '555-9999', 'Test', '0xTEST');

-- Add test doctor
INSERT INTO doctors (name, specialization, phone, blockchain_account)
VALUES ('Dr. Test', 'Internal Medicine', '555-8888', '0xDOCTEST');

-- Add test consent
INSERT INTO consents (patient_address, doctor_address, status, timestamp)
VALUES ('0xTEST', '0xDOCTEST', 'granted', NOW());

-- Add test document
INSERT INTO documents (patient_address, document_name, file_path, uploader, upload_timestamp)
VALUES ('0xTEST', 'test_doc.pdf', '/uploads/test_doc.pdf', '0xTEST', NOW());

-- Add test access log
INSERT INTO access_logs (doctor_address, patient_address, resource_id, action, access_timestamp)
VALUES ('0xDOCTEST', '0xTEST', 'DOC-001', 'VIEW_DOCUMENTS', NOW());

-- ============================================================================
-- 14. BULK OPERATIONS
-- ============================================================================

-- Update all consent status (be careful!)
UPDATE consents SET status = 'granted' WHERE status = 'pending';

-- Update patient information by blockchain address
UPDATE patients 
SET age = 45 
WHERE blockchain_account = '0x2';

-- Add phone number to all doctors (if null)
UPDATE doctors 
SET phone = '555-0000' 
WHERE phone IS NULL;

-- ============================================================================
-- END OF QUERIES
-- ============================================================================

-- For more information, see DATABASE_SETUP_GUIDE.md

import mysql.connector
from mysql.connector import Error
import sqlite3
from sqlite3 import Error as SQLiteError
import os

# If MySQL is unreachable, fall back to a local SQLite DB for development/testing.
USE_BACKEND = None  # 'mysql' or 'sqlite'
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'local_data.db')


def create_connection():
    """Create a database connection to the MySQL server or fallback to SQLite.

    Returns a tuple (backend, connection) where backend is 'mysql' or 'sqlite'.
    """
    global USE_BACKEND
    # Try MySQL first if not explicitly decided
    if USE_BACKEND is None or USE_BACKEND == 'mysql':
        try:
            conn = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='Pallavi@4005',
                database='pallavi-3136370892'
            )
            USE_BACKEND = 'mysql'
            return ('mysql', conn)
        except Error as e:
            print(f"MySQL connection error: {e}")
            print("Falling back to local SQLite database for development.")
            USE_BACKEND = 'sqlite'

    # SQLite fallback
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
        # Enable foreign key constraints
        conn.execute('PRAGMA foreign_keys = ON;')
        USE_BACKEND = 'sqlite'
        return ('sqlite', conn)
    except SQLiteError as e:
        print(f"SQLite connection error: {e}")
        return (None, None)

def execute_query(query, params=None):
    """Execute a single query (INSERT, UPDATE, DELETE, CREATE).

    This function supports both MySQL and SQLite backends.
    """
    backend, connection = create_connection()
    if backend is None or connection is None:
        print("No database connection available to execute query.")
        return

    try:
        if backend == 'mysql':
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            cursor.close()
        else:  # sqlite
            cursor = connection.cursor()
            # Convert %s placeholders to ? for sqlite if present
            if '%s' in query and params:
                q = query.replace('%s', '?')
                cursor.execute(q, params)
            else:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            connection.commit()
            cursor.close()
        print("Query executed successfully")
    except (Error, SQLiteError) as e:
        print(f"The error '{e}' occurred")
    finally:
        try:
            connection.close()
        except Exception:
            pass

def execute_read_query(query, params=None):
    """Execute a read query (SELECT). Returns list of rows or None."""
    backend, connection = create_connection()
    if backend is None or connection is None:
        print("No database connection available to execute read query.")
        return None

    try:
        cursor = connection.cursor()
        if backend == 'mysql':
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        else:  # sqlite
            # Convert %s placeholders to ? for sqlite if present
            if '%s' in query and params:
                q = query.replace('%s', '?')
                cursor.execute(q, params)
            else:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            result = cursor.fetchall()
        return result
    except (Error, SQLiteError) as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            connection.close()
        except Exception:
            pass

def init_db():
    """Initialize the database tables."""
    
    # Define backend-specific CREATE statements
    backend, _ = create_connection()
    if backend == 'mysql':
        create_patients_table = """
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT,
            gender VARCHAR(10),
            address VARCHAR(255),
            phone VARCHAR(20),
            medical_history TEXT,
            blockchain_account VARCHAR(42),
            INDEX idx_blockchain_account (blockchain_account)
        ) ENGINE=InnoDB;
        """

        create_doctors_table = """
        CREATE TABLE IF NOT EXISTS doctors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            specialization VARCHAR(100),
            phone VARCHAR(20),
            blockchain_account VARCHAR(42)
        ) ENGINE=InnoDB;
        """

        create_consents_table = """
        CREATE TABLE IF NOT EXISTS consents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_address VARCHAR(42) NOT NULL,
            doctor_address VARCHAR(42) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_consent (patient_address, doctor_address),
            INDEX idx_patient (patient_address),
            INDEX idx_doctor (doctor_address)
        ) ENGINE=InnoDB;
        """

        create_documents_table = """
        CREATE TABLE IF NOT EXISTS documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_address VARCHAR(42) NOT NULL,
            document_name VARCHAR(255) NOT NULL,
            file_path VARCHAR(500),
            uploader VARCHAR(42),
            upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_patient (patient_address),
            INDEX idx_timestamp (upload_timestamp)
        ) ENGINE=InnoDB;
        """

        create_access_logs_table = """
        CREATE TABLE IF NOT EXISTS access_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            doctor_address VARCHAR(42),
            patient_address VARCHAR(42),
            resource_id VARCHAR(255),
            action VARCHAR(100),
            access_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_patient (patient_address),
            INDEX idx_doctor (doctor_address),
            INDEX idx_timestamp (access_timestamp)
        ) ENGINE=InnoDB;
        """

        create_patient_relationships_table = """
        CREATE TABLE IF NOT EXISTS patient_relationships (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient1_address VARCHAR(42) NOT NULL,
            patient2_address VARCHAR(42) NOT NULL,
            relationship_type VARCHAR(50) NOT NULL,
            description VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_patient1 (patient1_address),
            INDEX idx_patient2 (patient2_address)
        ) ENGINE=InnoDB;
        """
    else:
        # SQLite-compatible table definitions
        create_patients_table = """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            address TEXT,
            phone TEXT,
            medical_history TEXT,
            blockchain_account TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_patients_blockchain_account ON patients(blockchain_account);
        """

        create_doctors_table = """
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT,
            phone TEXT,
            blockchain_account TEXT
        );
        """

        create_consents_table = """
        CREATE TABLE IF NOT EXISTS consents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_address TEXT NOT NULL,
            doctor_address TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_documents_table = """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_address TEXT NOT NULL,
            document_name TEXT NOT NULL,
            file_path TEXT,
            uploader TEXT,
            upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_access_logs_table = """
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_address TEXT,
            patient_address TEXT,
            resource_id TEXT,
            action TEXT,
            access_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_patient_relationships_table = """
        CREATE TABLE IF NOT EXISTS patient_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient1_address TEXT NOT NULL,
            patient2_address TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_patient_relationships_patient1 ON patient_relationships(patient1_address);
        CREATE INDEX IF NOT EXISTS idx_patient_relationships_patient2 ON patient_relationships(patient2_address);
        """

    # Use backend-specific CREATE statements
    backend, conn = create_connection()
    if backend is None:
        print("No DB backend available for init_db")
        return

    if backend == 'mysql':
        execute_query(create_patients_table)
        execute_query(create_doctors_table)
        execute_query(create_consents_table)
        execute_query(create_documents_table)
        execute_query(create_access_logs_table)
        execute_query(create_patient_relationships_table)
        print("MySQL tables initialized.")

    else:
        execute_query(create_patients_table)
        execute_query(create_doctors_table)
        execute_query(create_consents_table)
        execute_query(create_documents_table)
        execute_query(create_access_logs_table)
        execute_query(create_patient_relationships_table)
        print("SQLite tables initialized at: {}".format(SQLITE_DB_PATH))

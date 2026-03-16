#!/usr/bin/env python3
"""
Database Setup and Initialization Script
This script initializes the database schema and populates sample data.
Run this script once at the start before running the Flask app.
"""

from db_utils import init_db, execute_query, execute_read_query

def populate_sample_data():
    """Populate the database with sample data."""
    
    print("\n" + "="*60)
    print("POPULATING SAMPLE DATA")
    print("="*60)
    
    # Sample Patients
    patients = [
        ("John Doe", 35, "Male", "123 Maple St", "555-0101", "Hypertension, Allergy to Penicillin", "0x2"),
        ("Jane Smith", 28, "Female", "456 Oak Ave", "555-0102", "Asthma", "0x3"),
        ("Alice Johnson", 62, "Female", "789 Pine Rd", "555-0103", "Diabetes Type 2", "0x4"),
        ("Bob Brown", 45, "Male", "321 Elm St", "555-0104", "None", "0x5"),
        ("Charlie Davis", 50, "Male", "654 Cedar Ln", "555-0105", "High Cholesterol", "0x6")
    ]
    
    insert_patient_query = """
    INSERT INTO patients (name, age, gender, address, phone, medical_history, blockchain_account) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    print("\nInserting sample patients...")
    for p in patients:
        # Check if exists to avoid duplicates (based on name for simplicity)
        check_query = "SELECT * FROM patients WHERE name = %s"
        if not execute_read_query(check_query, (p[0],)):
            execute_query(insert_patient_query, p)
            print(f"  ✓ Added patient: {p[0]}")
        else:
            print(f"  - Patient {p[0]} already exists (skipped)")

    # Sample Doctors
    doctors = [
        ("Dr. Emily White", "Cardiologist", "555-0201", "0x2"),
        ("Dr. Michael Green", "General Practitioner", "555-0202", "0x3"),
        ("Dr. Sarah Black", "Neurologist", "555-0203", "0x4")
    ]
    
    insert_doctor_query = """
    INSERT INTO doctors (name, specialization, phone, blockchain_account)
    VALUES (%s, %s, %s, %s)
    """

    print("\nInserting sample doctors...")
    for d in doctors:
        check_query = "SELECT * FROM doctors WHERE name = %s"
        if not execute_read_query(check_query, (d[0],)):
            execute_query(insert_doctor_query, d)
            print(f"  ✓ Added doctor: {d[0]}")
        else:
            print(f"  - Doctor {d[0]} already exists (skipped)")
    
    print("\n✓ Sample data population complete!")

def verify_tables():
    """Verify that all tables were created successfully."""
    print("\n" + "="*60)
    print("VERIFYING DATABASE TABLES")
    print("="*60)
    
    tables = ['patients', 'doctors', 'consents', 'documents', 'access_logs']
    
    for table in tables:
        try:
            result = execute_read_query(f"SELECT COUNT(*) FROM {table}")
            print(f"  ✓ Table '{table}' exists")
        except Exception as e:
            print(f"  ✗ Table '{table}' - Error: {e}")
    
    print("\n✓ All tables verified!")

def main():
    """Main setup function."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║      Healthcare Blockchain Database Setup & Initialization  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        print("\n" + "="*60)
        print("INITIALIZING DATABASE SCHEMA")
        print("="*60)
        print("\nCreating database tables...")
        init_db()
        print("✓ Database schema initialized successfully!")
        
        # Verify tables
        verify_tables()
        
        # Populate sample data
        populate_sample_data()
        
        print("\n" + "="*60)
        print("SETUP COMPLETE!")
        print("="*60)
        print("\n✓ Database is ready for use!")
        print("\nYou can now run the Flask app with:")
        print("  python app.py")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n✗ Setup failed with error: {e}")
        print("\nPlease ensure:")
        print("  1. MySQL server is running")
        print("  2. Database credentials in db_utils.py are correct")
        print("  3. You have the required permissions")
        print("\nSetup incomplete. Please fix the error and try again.")
        return False
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

from db_utils import init_db, execute_query, execute_read_query
from blockchain_utils import get_accounts

def populate_sample_data():
    """Populate the database with sample data."""
    
    accounts = get_accounts()
    
    # Sample Patients
    patients = [
        ("Patient Zero", 30, "Male", "000 Zero St", "555-0000", "No known conditions", accounts[0]),
        ("John Doe", 35, "Male", "123 Maple St", "555-0101", "Hypertension, Allergy to Penicillin", accounts[1]),
        ("Jane Smith", 28, "Female", "456 Oak Ave", "555-0102", "Asthma", accounts[2]),
        ("Alice Johnson", 62, "Female", "789 Pine Rd", "555-0103", "Diabetes Type 2", accounts[3]),
        ("Bob Brown", 45, "Male", "321 Elm St", "555-0104", "None", accounts[4]),
        ("Charlie Davis", 50, "Male", "654 Cedar Ln", "555-0105", "High Cholesterol", accounts[5])
    ]
    
    insert_patient_query = """
    INSERT INTO patients (name, age, gender, address, phone, medical_history, blockchain_account) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    print("Inserting sample patients...")
    for p in patients:
        # Check if exists to avoid duplicates (based on name for simplicity)
        check_query = "SELECT * FROM patients WHERE name = %s"
        if not execute_read_query(check_query, (p[0],)):
            execute_query(insert_patient_query, p)
        else:
            print(f"Patient {p[0]} already exists.")

    # Sample Doctors
    doctors = [
        ("Dr. Emily White", "Cardiologist", "555-0201", accounts[6]),
        ("Dr. Michael Green", "General Practitioner", "555-0202", accounts[7])
    ]
    
    insert_doctor_query = """
    INSERT INTO doctors (name, specialization, phone, blockchain_account)
    VALUES (%s, %s, %s, %s)
    """

    print("Inserting sample doctors...")
    for d in doctors:
        check_query = "SELECT * FROM doctors WHERE name = %s"
        if not execute_read_query(check_query, (d[0],)):
            execute_query(insert_doctor_query, d)
        else:
             print(f"Doctor {d[0]} already exists.")

    # Sample Patient Relationships
    relationships = [
        (accounts[0], accounts[1], 'family', 'Sibling'),
        (accounts[1], accounts[0], 'family', 'Sibling'),
        (accounts[1], accounts[2], 'family', 'Spouse'),
        (accounts[1], accounts[3], 'family', 'Mother'),
        (accounts[2], accounts[1], 'family', 'Spouse'),
        (accounts[2], accounts[3], 'family', 'Mother-in-law'),
        (accounts[3], accounts[1], 'family', 'Son'),
        (accounts[3], accounts[2], 'family', 'Daughter-in-law')
    ]
    
    insert_relationship_query = """
    INSERT INTO patient_relationships (patient1_address, patient2_address, relationship_type, description) 
    VALUES (%s, %s, %s, %s)
    """
    
    print("Inserting sample relationships...")
    for r in relationships:
        # Check if exists
        check_query = "SELECT * FROM patient_relationships WHERE patient1_address = %s AND patient2_address = %s AND relationship_type = %s"
        if not execute_read_query(check_query, (r[0], r[1], r[2])):
            execute_query(insert_relationship_query, r)
        else:
            print(f"Relationship {r[0]} -> {r[1]} already exists.")

if __name__ == "__main__":
    print("Initializing Database...")
    init_db()
    print("Populating Sample Data...")
    populate_sample_data()
    print("Done!")

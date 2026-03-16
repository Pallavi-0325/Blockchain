from db_utils import execute_query, execute_read_query
from web3 import Web3

p1 = Web3.to_checksum_address('0xeA6aB78cE1C88E20B94b7a1a1CB1835657C8F52F')
p2 = Web3.to_checksum_address('0x15fd4f6bada5016ee31825d7253436d096fc9378')

print(f"Checking for patients {p1} and {p2}")

# Ensure P1 exists
res1 = execute_read_query("SELECT id FROM patients WHERE blockchain_account=%s", (p1,))
if not res1:
    execute_query("INSERT INTO patients (name, age, blockchain_account) VALUES (%s, %s, %s)", ("First Patient", 30, p1))
    print(f"Inserted patient 1: {p1}")
else:
    print(f"Patient 1 already exists: {p1}")

# Ensure P2 exists
res2 = execute_read_query("SELECT id FROM patients WHERE blockchain_account=%s", (p2,))
if not res2:
    execute_query("INSERT INTO patients (name, age, blockchain_account) VALUES (%s, %s, %s)", ("Second Patient", 25, p2))
    print(f"Inserted patient 2: {p2}")
else:
    print(f"Patient 2 already exists: {p2}")

# Check relationship
rel = execute_read_query("SELECT id FROM patient_relationships WHERE patient1_address=%s AND patient2_address=%s", (p1, p2))
if not rel:
    execute_query("INSERT INTO patient_relationships (patient1_address, patient2_address, relationship_type, description) VALUES (%s, %s, %s, %s)", (p1, p2, 'family', 'Shared Patient Portal Access'))
    print(f"Inserted relationship between {p1} and {p2}")
else:
    print(f"Relationship already exists between {p1} and {p2}")

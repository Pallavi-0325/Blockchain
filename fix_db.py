from db_utils import execute_query, execute_read_query
from web3 import Web3

p1_raw = '0xeA6aB78cE1C88E20B94b7a1a1CB1835657C8F52F'
p2_raw = '0x15fd4f6bada5016ee31825d7253436d096fc9378'

p1 = Web3.to_checksum_address(p1_raw)
p2 = Web3.to_checksum_address(p2_raw)

print(f"Checksum P1: {p1}")
print(f"Checksum P2: {p2}")

# Delete old relationships with these to start fresh
execute_query("DELETE FROM patient_relationships WHERE patient1_address=%s OR patient2_address=%s", (p1, p1))
execute_query("DELETE FROM patient_relationships WHERE patient1_address=%s OR patient2_address=%s", (p2, p2))

# Ensure they exist in patients
res1 = execute_read_query("SELECT id FROM patients WHERE blockchain_account=%s", (p1,))
if not res1:
    execute_query("INSERT INTO patients (name, age, blockchain_account) VALUES (%s, %s, %s)", ("First Patient", 30, p1))
res2 = execute_read_query("SELECT id FROM patients WHERE blockchain_account=%s", (p2,))
if not res2:
    execute_query("INSERT INTO patients (name, age, blockchain_account) VALUES (%s, %s, %s)", ("Second Patient", 25, p2))

# Insert relationship
execute_query("INSERT INTO patient_relationships (patient1_address, patient2_address, relationship_type, description) VALUES (%s, %s, %s, %s)", (p1, p2, 'family', 'Shared Portal'))
print("Relationship inserted successfully:")
for row in execute_read_query("SELECT * FROM patient_relationships WHERE patient1_address=%s", (p1,)):
    print(row)

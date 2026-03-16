from db_utils import execute_read_query
from web3 import Web3

patient_address = Web3.to_checksum_address('0xeA6aB78cE1C88E20B94b7a1a1CB1835657C8F52F')

relationships_query = """
SELECT pr.patient2_address, pr.relationship_type, pr.description, p.name, p.age, p.medical_history
FROM patient_relationships pr
JOIN patients p ON pr.patient2_address = p.blockchain_account
WHERE pr.patient1_address = %s
"""

relationships_data = execute_read_query(relationships_query, (patient_address,))

print(f"Data for {patient_address}:")
print(relationships_data)

print("\nAll patients in DB:")
all_p = execute_read_query("SELECT blockchain_account FROM patients")
for p in all_p:
    print(p[0])

print("\nAll patient relationships in DB:")
all_pr = execute_read_query("SELECT patient1_address, patient2_address FROM patient_relationships")
for pr in all_pr:
    print(f"{pr[0]} -> {pr[1]}")


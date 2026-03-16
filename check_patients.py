from db_utils import execute_read_query

patients = execute_read_query("SELECT * FROM patients")

print("Patients in DB:")
for p in patients:
    print(p)
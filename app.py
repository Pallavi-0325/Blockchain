from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from blockchain_utils import get_contract, get_accounts, w3
import datetime
from db_utils import execute_query, execute_read_query, init_db
from web3 import Web3

def maintain_continuous_hierarchy():
    """Automatically maintain continuous hierarchy when patients are added"""
    try:
        # Get all patients ordered by when they were added (or by name for consistency)
        patients = execute_read_query('SELECT name, blockchain_account FROM patients ORDER BY name')
        
        if len(patients) < 2:
            return  # Need at least 2 patients for hierarchy
        
        # Clear existing hierarchy relationships
        execute_query('DELETE FROM patient_relationships WHERE relationship_type=%s', ('hierarchy',))
        
        # Create continuous hierarchy chain
        for i, (current_name, current_addr) in enumerate(patients):
            current_level = i + 1
            
            # Each patient sees all patients after them in the chain
            for j in range(i + 1, len(patients)):
                next_name, next_addr = patients[j]
                next_level = j + 1
                
                # Add hierarchy relationship
                execute_query('''
                    INSERT INTO patient_relationships 
                    (patient1_address, patient2_address, relationship_type, description, hierarchy_order) 
                    VALUES (%s, %s, %s, %s, %s)
                ''', (current_addr, next_addr, 'hierarchy', f'Patient {next_level}', next_level))
        
        print(f"Continuous hierarchy updated for {len(patients)} patients")
        
    except Exception as e:
        print(f"Error maintaining continuous hierarchy: {e}")

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Initialize database tables on app startup
try:
    print("Initializing database tables...")
    init_db()
    print("Database initialized successfully!")
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")
    print("Some features may not work properly. Please run 'python init_db.py' manually.")

# Accounts mappings (Simulated for initial load, but now using contract)
# Admin: Accounts[0] (Fixed)

# In a real app, this would be a real auth system.
# Here we just map indices to roles for demonstration.
# Accounts[0]: Deployer/Admin
# Accounts[1]: Patient 1
# Accounts[2]: Doctor 1
# Accounts[3]: Pharmacist 1
# Accounts[4]: Lab Tech 1
# Accounts[5]: Insurance Agent 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    role = request.form.get('role')
    wallet_address = (request.form.get('wallet_address') or "").strip()
    
    # Simple role mapping for demo purpose (In real app, we check if address has role in contract)
    accounts = get_accounts()
    user_address = None
    
    # For demo simplicity, we still map roles to specific accounts initially, 
    # but actual validation should happen against the contract lists.
    # Here we just assume the user is selecting who they are.
    if role == 'patient':
        # Always require and use the connected wallet as the patient identifier.
        # This guarantees that different MetaMask accounts are treated as
        # completely separate patients, never falling back to the same demo wallet.
        if not wallet_address:
            # No wallet connected – send back to home so the user reconnects.
            return redirect(url_for('index'))
        user_address = wallet_address
    elif role == 'doctor':
        user_address = accounts[2]
    elif role == 'pharmacy':
        user_address = accounts[3]
    elif role == 'lab':
        user_address = accounts[4]
    elif role == 'insurance':
        user_address = accounts[5]
    elif role == 'admin':
        user_address = accounts[0]
        
    # Log to blockchain if user identified
    if user_address:
        try:
            contract = get_contract()
            user_agent = request.headers.get('User-Agent') or "Unknown Device"
            # Log login
            tx_hash = contract.functions.logLogin(user_agent).transact({'from': user_address, 'gas': 1000000})
            w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Login logged for {role} ({user_address}) on {user_agent}")
        except Exception as e:
            print(f"Failed to log login: {e}")

    if role == 'patient':
        return redirect(url_for('patient_dashboard', patient_address=user_address))
    elif role == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    elif role == 'pharmacy':
        return redirect(url_for('pharmacy_dashboard'))
    elif role == 'lab':
        return redirect(url_for('lab_dashboard'))
    elif role == 'insurance':
        return redirect(url_for('insurance_dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('index'))

@app.route('/patient_dashboard/<patient_address>', methods=['GET', 'POST'])
def patient_dashboard(patient_address):
    from web3 import Web3
    patient_address = Web3.to_checksum_address(patient_address)
    contract = get_contract()
    accounts = get_accounts()
    
    # In a real app, use session. Here hardcoded for demo.
    # We'll assume the user is the one logged in via the mock login
    # For simplicity, we just use Accounts[1] if no session logic is strict, 
    # but let's try to infer from a global or passed param if possible.
    # The existing code uses query param or hardcoded.
    # Ensure we have *some* address; if none provided, use demo patient.
    # Do not overwrite arbitrary wallet addresses, so that each wallet
    # sees its own (initially empty) data.
    if not patient_address:
        patient_address = accounts[1]
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'grant':
            doctor_address = request.form.get('doctor_address')
            try:
                tx_hash = contract.functions.grantConsent(doctor_address).transact({'from': patient_address})
                w3.eth.wait_for_transaction_receipt(tx_hash)
                
                # Store consent in database
                try:
                    check_q = "SELECT * FROM consents WHERE patient_address=%s AND doctor_address=%s"
                    exists = execute_read_query(check_q, (patient_address, doctor_address))
                    
                    if exists:
                        update_q = "UPDATE consents SET status='granted', timestamp=NOW() WHERE patient_address=%s AND doctor_address=%s"
                        execute_query(update_q, (patient_address, doctor_address))
                    else:
                        insert_q = "INSERT INTO consents (patient_address, doctor_address, status, timestamp) VALUES (%s, %s, 'granted', NOW())"
                        execute_query(insert_q, (patient_address, doctor_address))
                    print(f"Consent stored in database for {patient_address} -> {doctor_address}")
                except Exception as db_e:
                    print(f"DB consent store failed: {db_e}")
            except Exception as e:
                print(e)
                
        elif action == 'revoke':
            doctor_address = request.form.get('doctor_address')
            try:
                tx_hash = contract.functions.revokeConsent(doctor_address).transact({'from': patient_address})
                w3.eth.wait_for_transaction_receipt(tx_hash)
                
                # Store revocation in database
                try:
                    check_q = "SELECT * FROM consents WHERE patient_address=%s AND doctor_address=%s"
                    exists = execute_read_query(check_q, (patient_address, doctor_address))
                    
                    if exists:
                        update_q = "UPDATE consents SET status='revoked', timestamp=NOW() WHERE patient_address=%s AND doctor_address=%s"
                        execute_query(update_q, (patient_address, doctor_address))
                    else:
                        insert_q = "INSERT INTO consents (patient_address, doctor_address, status, timestamp) VALUES (%s, %s, 'revoked', NOW())"
                        execute_query(insert_q, (patient_address, doctor_address))
                    print(f"Revocation stored in database for {patient_address} -> {doctor_address}")
                except Exception as db_e:
                    print(f"DB revocation store failed: {db_e}")
            except Exception as e:
                print(e)
        
        elif action == 'update_profile':
            name = request.form.get('name')
            email = request.form.get('email')
            try:
                age = int(request.form.get('age'))
                # Blockchain Update
                tx_hash = contract.functions.setProfile(name, email, age).transact({'from': patient_address})
                w3.eth.wait_for_transaction_receipt(tx_hash)
                
                flash('Profile updated successfully!', 'success')
                
                # MySQL Update
                try:
                    query = "UPDATE patients SET name=%s, age=%s, gender=%s, address=%s, phone=%s WHERE blockchain_account=%s"
                    # Note: form might not have all fields yet, using simple update for now or fallback insert
                    # Lets check if exists first
                    check_q = "SELECT * FROM patients WHERE blockchain_account=%s"
                    exists = execute_read_query(check_q, (patient_address,))
                    
                    if exists:
                         execute_query(query, (name, age, "Unknown", "Unknown", "Unknown", patient_address))
                    else:
                         ins_query = "INSERT INTO patients (name, age, blockchain_account) VALUES (%s, %s, %s)"
                         execute_query(ins_query, (name, age, patient_address))
                         
                         # New patient added - maintain continuous hierarchy
                         maintain_continuous_hierarchy()
                         
                except Exception as db_e:
                    print(f"DB Update failed: {db_e}")
                    flash('Profile updated on blockchain but database sync failed.', 'warning')

            except Exception as e:
                print(f"Profile update error: {e}")
                flash(f'Failed to update profile: {str(e)}', 'error')

        elif action == 'upload_document':
            file = request.files.get('document')
            if file:
                filename = file.filename
                # Save locally (simulating IPFS)
                upload_dir = "static/uploads"
                import os
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                filepath = f"{upload_dir}/{filename}"
                file.save(filepath)
                
                try:
                    tx_hash = contract.functions.uploadDocument(patient_address, filename, filepath).transact({'from': patient_address})
                    w3.eth.wait_for_transaction_receipt(tx_hash)
                    
                    # Store document metadata in database
                    try:
                        insert_doc_q = "INSERT INTO documents (patient_address, document_name, file_path, uploader, upload_timestamp) VALUES (%s, %s, %s, %s, NOW())"
                        execute_query(insert_doc_q, (patient_address, filename, filepath, patient_address))
                        print(f"Document metadata stored for {filename}")
                    except Exception as db_e:
                        print(f"DB document store failed: {db_e}")
                except Exception as e:
                    print(f"Upload error: {e}")

        elif action == 'add_hierarchy':
            patient2_address = request.form.get('patient2_address')
            hierarchy_order = request.form.get('hierarchy_order', 1)
            description = request.form.get('description', f'Hierarchy Level {hierarchy_order}')
            
            try:
                # Check if patient2 exists in database
                check_patient_q = "SELECT * FROM patients WHERE blockchain_account=%s"
                patient2_exists = execute_read_query(check_patient_q, (patient2_address,))
                
                if not patient2_exists:
                    flash('Patient not found in database. Please check the wallet address.', 'error')
                else:
                    # Insert hierarchy relationship
                    insert_hierarchy_q = """
                    INSERT INTO patient_relationships (patient1_address, patient2_address, relationship_type, description, hierarchy_order) 
                    VALUES (%s, %s, 'hierarchy', %s, %s)
                    ON DUPLICATE KEY UPDATE description=%s, hierarchy_order=%s
                    """
                    execute_query(insert_hierarchy_q, (patient_address, patient2_address, description, int(hierarchy_order), description, int(hierarchy_order)))
                    
                    # Auto-maintain continuous hierarchy
                    maintain_continuous_hierarchy()
                    
                    flash(f'Hierarchy relationship established successfully!', 'success')
            except Exception as e:
                print(f"Error adding hierarchy relationship: {e}")
                flash(f'Failed to add hierarchy relationship: {str(e)}', 'error')

        return redirect(url_for('patient_dashboard', patient_address=patient_address))

    # Fetch Data for View
    doctors = []
    doctors = []
    # Get list of doctors from MySQL
    try:
        db_doctors = execute_read_query("SELECT name, specialization, blockchain_account FROM doctors")
        if db_doctors:
            # Format: (name, spec, address)
            # We will use this list. But we also need to check consent from blockchain.
            for d in db_doctors:
                doc_addr = d[2]
                has_consent = contract.functions.checkConsent(patient_address, doc_addr).call()
                req_status = contract.functions.getRequestStatus(patient_address, doc_addr).call()
                doctors.append({
                    'name': d[0],
                    'specialization': d[1],
                    'address': doc_addr,
                    'has_consent': has_consent,
                    'request_status': req_status
                })
    except Exception as e:
        print(f"Error fetching doctors from DB: {e}")

    # Fallback to Blockchain if DB empty or failed
    if not doctors:
        doctor_addresses = contract.functions.getDoctors().call() 
        if not doctor_addresses:
            doctor_addresses = [accounts[2]]
        
        for doc_addr in doctor_addresses:
            has_consent = contract.functions.checkConsent(patient_address, doc_addr).call()
            req_status = contract.functions.getRequestStatus(patient_address, doc_addr).call()
            doctors.append({
                'name': "Doctor (No DB)",
                'specialization': "General",
                'address': doc_addr,
                'has_consent': has_consent,
                'request_status': req_status
            })

    other_providers = [
        {'role': 'Pharmacy', 'address': accounts[3], 'has_consent': contract.functions.checkConsent(patient_address, accounts[3]).call()},
        {'role': 'Lab', 'address': accounts[4], 'has_consent': contract.functions.checkConsent(patient_address, accounts[4]).call()},
        {'role': 'Insurance', 'address': accounts[5], 'has_consent': contract.functions.checkConsent(patient_address, accounts[5]).call()},
    ]

    # Access Logs
    # Function in contract: getAccessLogs() returns ALL logs. We need to filter for this patient.
    all_logs = contract.functions.getAccessLogs().call()
    patient_logs = []
    for log in all_logs:
        # Log struct: doctor, patient, resourceId, timestamp, action
        if log[1] == patient_address:
            patient_logs.append({
                'doctor': log[0],
                'resource_id': log[2],
                'timestamp': datetime.datetime.fromtimestamp(log[3]),
                'action': log[4]
            })
    patient_logs.reverse()

    # Concerns
    all_concerns = contract.functions.getConcerns().call()
    my_concerns = []
    for c in all_concerns:
        if c[0] == patient_address:
             my_concerns.append({
                 'recorder': c[1],
                 'description': c[2],
                 'timestamp': datetime.datetime.fromtimestamp(c[3])
             })
    my_concerns.reverse()

    # Profile & Documents
    profile_data = contract.functions.getProfile(patient_address).call()
    # Profile struct: name, email, age, exists
    profile = None
    if profile_data[3]: # exists
        profile = {
            'name': profile_data[0],
            'email': profile_data[1],
            'age': profile_data[2]
        }
    
    docs_data = contract.functions.getDocuments(patient_address).call()
    documents = []
    for d in docs_data:
        # name, path, timestamp, uploader
        documents.append({
            'name': d[0],
            'path': d[1],
            'timestamp': datetime.datetime.fromtimestamp(d[2]),
            'uploader': d[3],
            'source': 'blockchain'
        })
    
    # Also fetch documents from database
    try:
        db_docs = execute_read_query(
            "SELECT document_name, file_path, upload_timestamp, uploader FROM documents WHERE patient_address=%s ORDER BY upload_timestamp DESC",
            (patient_address,)
        )
        if db_docs:
            for doc in db_docs:
                # Check if not already in blockchain docs
                doc_exists = any(d['name'] == doc[0] for d in documents)
                if not doc_exists:
                    documents.append({
                        'name': doc[0],
                        'path': doc[1],
                        'timestamp': doc[2] if isinstance(doc[2], datetime.datetime) else datetime.datetime.fromisoformat(str(doc[2])),
                        'uploader': doc[3],
                        'source': 'database'
                    })
    except Exception as e:
        print(f"Error fetching documents from database: {e}")

    # Fetch Patient Relationships with Full Details (including hierarchy)
    connected_patients = []
    try:
        # Get relationships where current patient is patient1, prioritizing hierarchy relationships
        relationships_query = """
        SELECT pr.patient2_address, pr.relationship_type, pr.description, pr.hierarchy_order, 
               p.name, p.age, p.medical_history
        FROM patient_relationships pr
        JOIN patients p ON pr.patient2_address = p.blockchain_account
        WHERE pr.patient1_address = %s
        ORDER BY 
            CASE WHEN pr.relationship_type = 'hierarchy' THEN 1 ELSE 2 END,
            pr.hierarchy_order ASC,
            pr.created_at DESC
        """
        relationships_data = execute_read_query(relationships_query, (patient_address,))
        if relationships_data:
            for rel in relationships_data:
                connected_patient_address = rel[0]
                
                # Get blockchain profile for connected patient
                connected_profile = None
                try:
                    connected_profile_data = contract.functions.getProfile(connected_patient_address).call()
                    if connected_profile_data[3]: # exists
                        connected_profile = {
                            'name': connected_profile_data[0],
                            'email': connected_profile_data[1],
                            'age': connected_profile_data[2]
                        }
                    else:
                        connected_profile = {
                            'name': rel[4],
                            'email': 'patient@example.com',
                            'age': rel[5]
                        }
                except Exception as e:
                    print(f"Failed to fetch profile from blockchain for {connected_patient_address}: {e}")
                    connected_profile = {
                        'name': rel[4],
                        'email': 'patient@example.com',
                        'age': rel[5]
                    }
                
                # Get documents for connected patient
                connected_documents = []
                try:
                    connected_docs_data = contract.functions.getDocuments(connected_patient_address).call()
                    for d in connected_docs_data:
                        # name, path, timestamp, uploader
                        connected_documents.append({
                            'name': d[0],
                            'path': d[1],
                            'timestamp': datetime.datetime.fromtimestamp(d[2]),
                            'uploader': d[3],
                            'source': 'blockchain'
                        })
                except Exception as e:
                    print(f"Failed to fetch documents from blockchain for {connected_patient_address}: {e}")
                
                # Fetch connected patient docs from database
                try:
                    conn_db_docs = execute_read_query(
                        "SELECT document_name, file_path, upload_timestamp, uploader FROM documents WHERE patient_address=%s ORDER BY upload_timestamp DESC",
                        (connected_patient_address,)
                    )
                    if conn_db_docs:
                        for doc in conn_db_docs:
                            doc_exists = any(d['name'] == doc[0] for d in connected_documents)
                            if not doc_exists:
                                connected_documents.append({
                                    'name': doc[0],
                                    'path': doc[1],
                                    'timestamp': doc[2] if isinstance(doc[2], datetime.datetime) else datetime.datetime.fromisoformat(str(doc[2])),
                                    'uploader': doc[3],
                                    'source': 'database'
                                })
                except Exception as e:
                    print(f"Error fetching docs for connected patient {connected_patient_address}: {e}")
                
                # Get access logs for connected patient
                connected_logs = []
                for log in all_logs:
                    if log[1] == connected_patient_address:
                        connected_logs.append({
                            'doctor': log[0],
                            'resource_id': log[2],
                            'timestamp': datetime.datetime.fromtimestamp(log[3]),
                            'action': log[4]
                        })
                connected_logs.reverse()
                
                # Get concerns for connected patient
                connected_concerns = []
                for c in all_concerns:
                    if c[0] == connected_patient_address:
                         connected_concerns.append({
                             'recorder': c[1],
                             'description': c[2],
                             'timestamp': datetime.datetime.fromtimestamp(c[3])
                         })
                connected_concerns.reverse()
                
                connected_patients.append({
                    'address': connected_patient_address,
                    'relationship_type': rel[1],
                    'relationship_description': rel[2],
                    'hierarchy_order': rel[3],
                    'name': rel[4],
                    'age': rel[5],
                    'medical_history': rel[6],
                    'profile': connected_profile,
                    'documents': connected_documents,
                    'access_logs': connected_logs,
                    'concerns': connected_concerns
                })
    except Exception as e:
        print(f"Error fetching connected patient details: {e}")

    print("Connected Patients Data:", connected_patients)

    return render_template('patient_dashboard.html', 
                           patient_address=patient_address,
                           doctors=doctors,
                           other_providers=other_providers,
                           access_logs=patient_logs,
                           concerns=my_concerns,
                           profile=profile,
                           documents=documents,
                           connected_patients=connected_patients)

@app.route('/doctor', methods=['GET', 'POST'])
def doctor_dashboard():
    try:
        accounts = get_accounts()
        current_doctor = accounts[2]
        contract = get_contract()
        
        # Initialize doctor_info - this is always available
        doctor_info = {
            'name': 'Dr. Michael Green',
            'specialization': 'General Practitioner',
            'phone': '555-0202',
            'address': current_doctor
        }

        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'request_access':
                patient_address = request.form.get('patient_address')
                try:
                    tx_hash = contract.functions.requestAccess(patient_address).transact({'from': current_doctor})
                    w3.eth.wait_for_transaction_receipt(tx_hash)
                except Exception as e:
                    print(f"Request access error: {e}")
            return redirect(url_for('doctor_dashboard'))
        
        # Fetch patients list dynamically
        patients = []
        
        # Try MySQL first
        try:
            db_patients = execute_read_query("SELECT name, age, blockchain_account FROM patients")
            if db_patients:
                for p in db_patients:
                    p_name = p[0]
                    p_age = p[1]
                    p_addr = p[2]
                    
                    has_consent = contract.functions.checkConsent(p_addr, current_doctor).call()
                    req_status = contract.functions.getRequestStatus(p_addr, current_doctor).call()
                    
                    patients.append({
                        'address': p_addr,
                        'name': f"{p_name} (Age: {p_age})",
                        'has_consent': has_consent,
                        'request_status': req_status
                    })
        except Exception as e:
             print(f"Error fetching patients from DB: {e}")

        # Fallback/Merge if empty (don't duplicate if already added? simple fallback for now)
        if not patients:
            try:
                patients_addrs = contract.functions.getPatients().call()
                if not patients_addrs:
                     patients_addrs = [accounts[1]] # Fallback
                
                for p_addr in patients_addrs:
                    has_consent = contract.functions.checkConsent(p_addr, current_doctor).call()
                    req_status = contract.functions.getRequestStatus(p_addr, current_doctor).call()
                    
                    # Get profile name if available
                    profile_data = contract.functions.getProfile(p_addr).call()
                    p_name = profile_data[0] if profile_data[3] else "Unknown"

                    patients.append({
                        'address': p_addr,
                        'name': p_name,
                        'has_consent': has_consent,
                        'request_status': req_status
                    })
            except Exception as e:
                print(f"Error fetching patients from blockchain: {e}")
                patients = []

        return render_template('doctor_dashboard.html', 
                               doctor_address=current_doctor,
                               doctor_info=doctor_info if doctor_info else {
                                   'name': 'Dr. Michael Green',
                                   'specialization': 'General Practitioner',
                                   'phone': '555-0202',
                                   'address': current_doctor
                               },
                               patients=patients if patients else [])
    except Exception as e:
        print(f"ERROR in doctor_dashboard: {e}")
        import traceback
        traceback.print_exc()
        # Return with default doctor_info
        return render_template('doctor_dashboard.html',
                               doctor_address='Unknown',
                               doctor_info={
                                   'name': 'Dr. Michael Green',
                                   'specialization': 'General Practitioner',
                                   'phone': '555-0202',
                                   'address': 'Unknown'
                               },
                               patients=[])

@app.route('/doctor/view_documents/<patient_address>')
def doctor_view_documents(patient_address):
    accounts = get_accounts()
    current_doctor = accounts[2] # In real app, from session
    contract = get_contract()
    
    try:
        # 1. Check Consent
        has_consent = contract.functions.checkConsent(patient_address, current_doctor).call()
        
        if not has_consent:
            # Return a JSON error response instead of HTML
            return jsonify({
                'error': 'Access Denied',
                'message': 'You do not have consent to view documents for this patient. Please request access first.',
                'patient_address': patient_address
            }), 403
        
        # 2. Get Documents
        docs_data = contract.functions.getDocuments(patient_address).call()
        documents = []
        for d in docs_data:
            # name, path, timestamp, uploader
            documents.append({
                'name': d[0],
                'path': d[1],
                'timestamp': datetime.datetime.fromtimestamp(d[2]).strftime('%Y-%m-%d %H:%M:%S'),
                'uploader': d[3]
            })
            
        # 3. Log Access (Optional but good for audit)
        try:
             tx_hash = contract.functions.logAccess(patient_address, "VIEW_DOCUMENTS").transact({'from': current_doctor, 'gas': 1000000})
             w3.eth.wait_for_transaction_receipt(tx_hash)
             
             # Store access log in database
             try:
                 insert_log_q = "INSERT INTO access_logs (doctor_address, patient_address, resource_id, action, access_timestamp) VALUES (%s, %s, %s, %s, NOW())"
                 execute_query(insert_log_q, (current_doctor, patient_address, "DOCUMENTS", "VIEW_DOCUMENTS"))
                 print(f"Access log stored for {current_doctor} -> {patient_address}")
             except Exception as db_e:
                 print(f"DB access log store failed: {db_e}")
        except Exception as e:
             print(f"Log access failed: {e}")

        # 4. Get Patient Name (Optional)
        profile_data = contract.functions.getProfile(patient_address).call()
        patient_name = profile_data[0] if profile_data[3] else patient_address

        return render_template('doctor_view_documents.html', 
                               documents=documents, 
                               patient_name=patient_name,
                               patient_address=patient_address)
    
    except Exception as e:
        # Handle blockchain errors gracefully
        error_message = str(e)
        if 'Access Denied' in error_message or 'revert' in error_message:
            return jsonify({
                'error': 'Access Denied',
                'message': 'You do not have consent to view documents for this patient. Please request access first.',
                'patient_address': patient_address
            }), 403
        else:
            return jsonify({
                'error': 'System Error',
                'message': f'An error occurred while accessing patient records: {error_message}',
                'patient_address': patient_address
            }), 500

@app.route('/pharmacy', methods=['GET', 'POST'])
def pharmacy_dashboard():
    accounts = get_accounts()
    current_pharmacy = accounts[3] 
    contract = get_contract()
    
    # Logic: Search for a patient to fulfill prescription
    patients = []
    search_query = ""
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'search_patient':
            search_query = request.form.get('search_query', '').strip()
            
            if search_query:
                # Search in MySQL first
                try:
                    q = "SELECT name, age, blockchain_account FROM patients WHERE name LIKE %s OR blockchain_account LIKE %s"
                    db_results = execute_read_query(q, (f"%{search_query}%", f"%{search_query}%"))
                    if db_results:
                        for r in db_results:
                            patients.append({'name': r[0], 'age': r[1], 'address': r[2]})
                        print(f"Found {len(patients)} patients in database")
                except Exception as e:
                    print(f"Error searching patients in DB: {e}")
                
                # If no DB results, fallback to blockchain
                if not patients:
                    try:
                        patients_addrs = contract.functions.getPatients().call()
                        if patients_addrs:
                            for p_addr in patients_addrs:
                                profile_data = contract.functions.getProfile(p_addr).call()
                                if profile_data[3]:  # Check if profile exists
                                    p_name = profile_data[0]
                                    if search_query.lower() in p_name.lower() or search_query in p_addr:
                                        patients.append({'name': p_name, 'age': 'N/A', 'address': p_addr})
                        print(f"Found {len(patients)} patients in blockchain")
                    except Exception as e:
                        print(f"Error fetching patients from blockchain: {e}")

    return render_template('pharmacy_dashboard.html', 
                           pharmacy_address=current_pharmacy,
                           patients=patients,
                           search_query=search_query)

@app.route('/lab', methods=['GET', 'POST'])
def lab_dashboard():
    accounts = get_accounts()
    current_lab = accounts[4] 
    contract = get_contract()
    
    message = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'upload_result':
             patient_address = request.form.get('patient_address')
             test_name = request.form.get('test_name')
             file = request.files.get('result_file')
             
             if file:
                 filename = f"LAB_{test_name}_{file.filename}"
                 filepath = f"static/uploads/{filename}"
                 file.save(filepath)
                 
                 try:
                     # Upload as document to blockchain
                     tx_hash = contract.functions.uploadDocument(patient_address, f"Lab Result: {test_name}", filepath).transact({'from': current_lab})
                     w3.eth.wait_for_transaction_receipt(tx_hash)
                     message = "Lab result uploaded successfully!"
                 except Exception as e:
                     message = f"Error uploading: {e}"

    # List recent patients (Mock or DB)
    patients = [accounts[1]] 
    
    return render_template('lab_dashboard.html', 
                           lab_address=current_lab,
                           patients=patients,
                           message=message)

@app.route('/insurance', methods=['GET', 'POST'])
def insurance_dashboard():
    accounts = get_accounts()
    current_insurance = accounts[5] 
    contract = get_contract()
    
    message = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'process_claim':
            patient_address = request.form.get('patient_address')
            status = request.form.get('status') # Approved/Rejected
            
            # Log as a concern/note for now on blockchain
            try:
                 tx_hash = contract.functions.logConcern(patient_address, f"Insurance Claim {status} by {current_insurance}").transact({'from': current_insurance, 'gas': 1000000})
                 w3.eth.wait_for_transaction_receipt(tx_hash)
                 message = f"Claim {status} recorded."
            except Exception as e:
                 message = f"Error: {e}"

    patients = [accounts[1]] 
    
    return render_template('insurance_dashboard.html', 
                           insurance_address=current_insurance,
                           patients=patients,
                           message=message)

@app.route('/submit_concern', methods=['POST'])
def submit_concern():
    contract = get_contract()
    patient = request.form.get('patient')
    description = request.form.get('description')
    
    user_address = patient # In this route, patient submits for themselves
    
    # Transact
    tx_hash = contract.functions.logConcern(patient, description).transact({'from': user_address, 'gas': 1000000})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return redirect(url_for('patient_dashboard', patient_address=user_address))

@app.route('/submit_doctor_concern', methods=['POST'])
def submit_doctor_concern():
    contract = get_contract()
    patient = request.form.get('patient')
    description = request.form.get('description')
    doctor = request.form.get('doctor')
    
    # Transact from doctor's account
    tx_hash = contract.functions.logConcern(patient, description).transact({'from': doctor, 'gas': 1000000})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return redirect(url_for('doctor_dashboard'))

@app.route('/admin/add_user', methods=['POST'])
def admin_add_user():
    contract = get_contract()
    accounts = get_accounts()
    admin_account = accounts[0]
    
    new_user = request.form.get('address')
    role = request.form.get('role')
    
    try:
        tx_hash = contract.functions.registerUser(new_user, role).transact({'from': admin_account, 'gas': 1000000})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({'status': 'success', 'message': f'User {new_user} added as {role}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/grant', methods=['POST'])
def grant_consent():
    contract = get_contract()
    patient = request.json.get('patient')
    doctor = request.json.get('doctor')
    
    # Transact from patient's account
    tx_hash = contract.functions.grantConsent(doctor).transact({'from': patient, 'gas': 1000000})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return jsonify({'status': 'success', 'message': 'Consent Granted'})

@app.route('/api/revoke', methods=['POST'])
def revoke_consent():
    contract = get_contract()
    patient = request.json.get('patient')
    doctor = request.json.get('doctor')
    
    # Transact from patient's account
    tx_hash = contract.functions.revokeConsent(doctor).transact({'from': patient, 'gas': 1000000})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return jsonify({'status': 'success', 'message': 'Consent Revoked'})

@app.route('/api/access_record', methods=['POST'])
def access_record():
    contract = get_contract()
    patient = request.json.get('patient')
    doctor = request.json.get('doctor')
    resource_id = "EHR-RECORD-12345" # valid resource ID
    
    try:
        # Transact from doctor's account
        tx_hash = contract.functions.logAccess(patient, resource_id).transact({'from': doctor, 'gas': 1000000})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Store access log in database
        try:
            insert_log_q = "INSERT INTO access_logs (doctor_address, patient_address, resource_id, action, access_timestamp) VALUES (%s, %s, %s, %s, NOW())"
            execute_query(insert_log_q, (doctor, patient, resource_id, "ACCESS_RECORD"))
            print(f"Access log stored for {doctor} -> {patient} (resource: {resource_id})")
        except Exception as db_e:
            print(f"DB access log store failed: {db_e}")
        
        return jsonify({'status': 'success', 'message': 'Record Accessed Successfully', 'data': 'Patient Vitals: Normal, History: Clean'})
    except Exception as e:
        # The contract will revert if no consent
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    contract = get_contract()
    accounts = get_accounts()
    admin_addr = accounts[0] # Assuming 0 is admin/deployer

    if request.method == 'POST':
        if 'document' in request.files:
            file = request.files['document']
            patient_address = request.form.get('patient_address')
            
            if file and patient_address:
                filename = file.filename
                filepath = f"static/uploads/{filename}"
                file.save(filepath)
                
                try:
                    # Admin uploading for patient
                    tx_hash = contract.functions.uploadDocument(patient_address, filename, filepath).transact({'from': admin_addr})
                    w3.eth.wait_for_transaction_receipt(tx_hash)
                except Exception as e:
                    print(f"Admin upload error: {e}")
        return redirect(url_for('admin_dashboard'))

    # Fetch login logs from blockchain
    # Sol returns list of tuples/structs. 
    # LoginLog: (user, deviceId, timestamp)
    raw_logs = contract.functions.getLoginLogs().call()
    
    formatted_logs = []
    for log in raw_logs:
        formatted_logs.append({
            'user': log[0],
            'device_id': log[1],
            'timestamp': datetime.datetime.fromtimestamp(log[2]),
            'type': 'login'
        })
    
    # Fetch access logs from database
    try:
        access_logs = execute_read_query(
            "SELECT doctor_address, patient_address, resource_id, action, access_timestamp FROM access_logs ORDER BY access_timestamp DESC LIMIT 50"
        )
        if access_logs:
            for log in access_logs:
                formatted_logs.append({
                    'user': log[0],
                    'device_id': f"Patient: {log[1]} | Action: {log[3]}",
                    'timestamp': log[4],
                    'type': 'access'
                })
    except Exception as e:
        print(f"Error fetching access logs from database: {e}")
    
    # Fetch consent records from database
    try:
        consents = execute_read_query(
            "SELECT patient_address, doctor_address, status, timestamp FROM consents ORDER BY timestamp DESC LIMIT 50"
        )
        if consents:
            for record in consents:
                formatted_logs.append({
                    'user': record[1],  # doctor address
                    'device_id': f"Patient: {record[0]} | Status: {record[2]}",
                    'timestamp': record[3],
                    'type': 'consent'
                })
    except Exception as e:
        print(f"Error fetching consents from database: {e}")
    
    # Fetch document uploads from database
    try:
        documents = execute_read_query(
            "SELECT uploader, patient_address, document_name, upload_timestamp FROM documents ORDER BY upload_timestamp DESC LIMIT 50"
        )
        if documents:
            for doc in documents:
                formatted_logs.append({
                    'user': doc[0],  # uploader
                    'device_id': f"Patient: {doc[1]} | Document: {doc[2]}",
                    'timestamp': doc[3],
                    'type': 'document'
                })
    except Exception as e:
        print(f"Error fetching documents from database: {e}")
    
    # Sort all logs by timestamp desc
    formatted_logs.sort(key=lambda x: x['timestamp'], reverse=True)
    formatted_logs = formatted_logs[:100]  # Keep top 100 logs

    # Get patients for upload dropdown
    patients = contract.functions.getPatients().call()
    if not patients:
        patients = [accounts[1]]
    
    # Also get patients from database
    try:
        db_patients = execute_read_query("SELECT blockchain_account FROM patients")
        if db_patients:
            for p in db_patients:
                if p[0] not in patients:
                    patients.append(p[0])
    except:
        pass

    return render_template('admin_dashboard.html', logs=formatted_logs, patients=patients)

if __name__ == '__main__':
    print("Starting Flask Server on Port 5001...")
    app.run(debug=True, use_reloader=False, port=5001)
import json
from web3 import Web3
from solcx import compile_source, install_solc

# Install specific solidity compiler version
try:
    install_solc('0.8.0')
except Exception as e:
    print(f"Solc install check: {e}")

# Initialize Web3 with Ethereum Tester Provider (in-memory blockchain)
w3 = Web3(Web3.EthereumTesterProvider())

def compile_contract():
    """Compiles the Solidity contract and returns the interface."""
    with open('contracts/ConsentManager.sol', 'r') as file:
        contract_source_code = file.read()

    compiled_sol = compile_source(contract_source_code, output_values=['abi', 'bin'], solc_version='0.8.0')
    contract_id, contract_interface = next(iter(compiled_sol.items())) # Get the first contract
    
    return contract_interface['abi'], contract_interface['bin']

# Compile once
abi, bytecode = compile_contract()

# Global variable to hold deployment address
deployed_contract_address = None

def deploy_contract():
    """Deploys the contract to the local testnet."""
    global deployed_contract_address
    
    # Get the first account as deployer
    deployer_account = w3.eth.accounts[0]
    
    # Instantiate
    ConsentManager = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Submit transaction
    # Increased gas limit to accommodate larger contract
    tx_hash = ConsentManager.constructor().transact({'from': deployer_account, 'gas': 6000000})
    
    # Wait for receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    deployed_contract_address = tx_receipt.contractAddress
    
    print(f"Contract Deployed at: {deployed_contract_address}")
    return deployed_contract_address

def get_contract():
    """Returns the contract instance."""
    global deployed_contract_address
    if not deployed_contract_address:
         deployed_contract_address = deploy_contract()
    
    if not deployed_contract_address:
        raise ValueError("Failed to deploy contract, address is None")

    return w3.eth.contract(address=deployed_contract_address, abi=abi)

def get_accounts():
    """Returns available test accounts."""
    return w3.eth.accounts

# Initial deployment
deploy_contract()
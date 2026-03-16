-- Database Schema and Sample Data for Healthcare App

-- Create Database (Optional, if you haven't created it yet)
-- CREATE DATABASE `pallavi-3136370892`;
-- USE `pallavi-3136370892`;

-- Table: Patients
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(10),
    address VARCHAR(255),
    phone VARCHAR(20),
    medical_history TEXT,
    blockchain_account VARCHAR(42)
) ENGINE=InnoDB;

-- Table: Doctors
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    phone VARCHAR(20),
    blockchain_account VARCHAR(42)
) ENGINE=InnoDB;

-- Table: Patient Relationships
CREATE TABLE IF NOT EXISTS patient_relationships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient1_address VARCHAR(42) NOT NULL,
    patient2_address VARCHAR(42) NOT NULL,
    relationship_type VARCHAR(50) NOT NULL, -- 'family', 'emergency_contact', 'guardian', 'hierarchy', etc.
    description VARCHAR(255),
    hierarchy_order INT DEFAULT 0, -- Order in hierarchy (1, 2, 3, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient1_address) REFERENCES patients(blockchain_account) ON DELETE CASCADE,
    FOREIGN KEY (patient2_address) REFERENCES patients(blockchain_account) ON DELETE CASCADE,
    UNIQUE KEY unique_relationship (patient1_address, patient2_address, relationship_type)
) ENGINE=InnoDB;

-- Sample Data: Patients
INSERT INTO patients (name, age, gender, address, phone, medical_history, blockchain_account) VALUES 
('John Doe', 35, 'Male', '123 Maple St', '555-0101', 'Hypertension, Allergy to Penicillin', '0x15fD4f6BaDA5016EE31825D7253436d096Fc9378'),
('Jane Smith', 28, 'Female', '456 Oak Ave', '555-0102', 'Asthma', '0x07801d112b09284b4Ad3f70354e8f52490B26eB2'),
('Alice Johnson', 62, 'Female', '789 Pine Rd', '555-0103', 'Diabetes Type 2', '0x2CBF1801230d9DBD6B4C3678bdC351520105c7C7'),
('Bob Brown', 45, 'Male', '321 Elm St', '555-0104', 'None', '0xb22D49373A4b526899A74b1190886E0caF36CCce'),
('Charlie Davis', 50, 'Male', '654 Cedar Ln', '555-0105', 'High Cholesterol', '0xE1b5A2cD8F7E6d5B4a3C2b1A9f8E7d6C5b4A3f2');

-- Sample Data: Doctors
INSERT INTO doctors (name, specialization, phone, blockchain_account) VALUES 
('Dr. Emily White', 'Cardiologist', '555-0201', '0x07801d112b09284b4Ad3f70354e8f52490B26eB2'),
('Dr. Michael Green', 'General Practitioner', '555-0202', '0x2CBF1801230d9DBD6B4C3678bdC351520105c7C7');

-- Sample Data: Patient Relationships
INSERT INTO patient_relationships (patient1_address, patient2_address, relationship_type, description, hierarchy_order) VALUES
('0x15fD4f6BaDA5016EE31825D7253436d096Fc9378', '0x07801d112b09284b4Ad3f70354e8f52490B26eB2', 'family', 'Spouse', 0),
('0x15fD4f6BaDA5016EE31825D7253436d096Fc9378', '0x2CBF1801230d9DBD6B4C3678bdC351520105c7C7', 'family', 'Mother', 0),
('0x07801d112b09284b4Ad3f70354e8f52490B26eB2', '0x15fD4f6BaDA5016EE31825D7253436d096Fc9378', 'family', 'Spouse', 0),
('0x07801d112b09284b4Ad3f70354e8f52490B26eB2', '0x2CBF1801230d9DBD6B4C3678bdC351520105c7C7', 'family', 'Mother-in-law', 0),
('0x2CBF1801230d9DBD6B4C3678bdC351520105c7C7', '0x15fD4f6BaDA5016EE31825D7253436d096Fc9378', 'family', 'Son', 0),
('0x2CBF1801230d9DBD6B4C3678bdC351520105c7C7', '0x07801d112b09284b4Ad3f70354e8f52490B26eB2', 'family', 'Daughter-in-law', 0);

-- Sample Data: Patient Hierarchy (Patient 1 sees Patient 2, 3, 4, 5)
INSERT INTO patient_relationships (patient1_address, patient2_address, relationship_type, description, hierarchy_order) VALUES
('0x15fD4f6BaDA5016EE31825D7253436d096Fc9378', '0x07801d112b09284b4Ad3f70354e8f52490B26eB2', 'hierarchy', 'Patient 2', 2),
('0x15fD4f6BaDA5016EE31825D7253436d096Fc9378', '0x2CBF1801230d9DBD6B4C3678bdC351520105c7C7', 'hierarchy', 'Patient 3', 3),
('0x15fD4f6BaDA5016EE31825D7253436d096Fc9378', '0xb22D49373A4b526899A74b1190886E0caF36CCce', 'hierarchy', 'Patient 4', 4),
('0x15fD4f6BaDA5016EE31825D7253436d096Fc9378', '0xE1b5A2cD8F7E6d5B4a3C2b1A9f8E7d6C5b4A3f2', 'hierarchy', 'Patient 5', 5);

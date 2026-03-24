DROP DATABASE hospital_management;
CREATE DATABASE hospital_management;
USE hospital_management;

-- USERS TABLE (Admin, Doctor, Patient)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(50),
    role ENUM('Admin','Doctor','Patient')
);

-- DOCTORS TABLE
CREATE TABLE doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    specialization VARCHAR(100),
    phone VARCHAR(20)
);

-- PATIENTS TABLE
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    phone VARCHAR(20)
);

-- APPOINTMENTS TABLE
CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    appointment_date DATE,
    status ENUM('Scheduled','Completed','Cancelled'),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- PAYMENTS TABLE
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT,
    amount DECIMAL(10,2),
    payment_status ENUM('Paid','Pending'),
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);
USE hospital_management;

INSERT INTO users (name, email, password, role) VALUES
('Admin Kumar', 'admin@gmail.com', 'admin123', 'Admin'),
('Dr. Ravi', 'ravi@gmail.com', 'doc123', 'Doctor'),
('Dr. Anita', 'anita@gmail.com', 'doc456', 'Doctor'),
('Meena', 'meena@gmail.com', 'pat123', 'Patient'),
('Suresh', 'suresh@gmail.com', 'pat456', 'Patient');

INSERT INTO doctors (name, specialization, phone) VALUES
('Dr. Ravi', 'Cardiologist', '9876543210'),
('Dr. Anita', 'Dermatologist', '9876543222'),
('Dr. Karthik', 'Neurologist', '9876543333'),
('Dr. Priya', 'Orthopedic', '9876544444'),
('Dr. Arjun', 'Pediatrician', '9876545555');

INSERT INTO patients (name, age, gender, phone) VALUES
('Meena', 25, 'Female', '9000001111'),
('Suresh', 30, 'Male', '9000002222'),
('Rani', 40, 'Female', '9000003333'),
('Kumar', 35, 'Male', '9000004444'),
('Lakshmi', 28, 'Female', '9000005555');

INSERT INTO appointments (patient_id, doctor_id, appointment_date, status) VALUES
(1, 1, '2026-04-10', 'Scheduled'),
(2, 2, '2026-04-11', 'Completed'),
(3, 3, '2026-04-12', 'Scheduled'),
(4, 4, '2026-04-13', 'Cancelled'),
(5, 5, '2026-04-14', 'Scheduled');

INSERT INTO payments (appointment_id, amount, payment_status) VALUES
(1, 500.00, 'Paid'),
(2, 700.00, 'Paid'),
(3, 600.00, 'Pending'),
(4, 450.00, 'Paid'),
(5, 550.00, 'Pending');
SELECT * FROM users;
SELECT * FROM doctors;
SELECT * FROM patients;
SELECT * FROM appointments;
SELECT * FROM payments;

    

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS cifdb;
USE cifdb;

-- Step 2: Create Tables
CREATE TABLE Vendors (
    vendor_id VARCHAR(10) PRIMARY KEY,
    vendor_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    bank_account VARCHAR(20) NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL
);

CREATE TABLE Equipment (
    equipment_id VARCHAR(10) PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    remarks TEXT
);

CREATE TABLE LabVisits (
    visit_id VARCHAR(10) PRIMARY KEY,
    visitor_id VARCHAR(10) NOT NULL,
    visitor_name VARCHAR(100) NOT NULL,
    visitor_designation ENUM('PhD', 'Post Doc', 'MTech', 'B.Tech', 'Professor', 'NA') NOT NULL,
    visit_duration VARCHAR(20),
    equipment_id VARCHAR(10),
    visitor_contact VARCHAR(15),
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE MaintenanceVisits (
    visit_id VARCHAR(10) PRIMARY KEY,
    vendor_id VARCHAR(10),
    equipment_id VARCHAR(10),
    visit_time DATETIME,
    next_maintenance_date DATE,
    expenditure DECIMAL(10, 2),
    FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE ConsumableInventory (
    item_id VARCHAR(10) PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    quantity_in_stock INT NOT NULL,
    vendor_id VARCHAR(10),
    price_per_item DECIMAL(10, 2),
    reorder_level INT,
    FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Software (
    software_id VARCHAR(10) PRIMARY KEY,
    software_name VARCHAR(100) NOT NULL,
    version VARCHAR(20),
    license_type VARCHAR(50),
    license_key VARCHAR(100),
    license_expiry DATE,
    vendor_id VARCHAR(10),
    max_installations INT,
    usage_location VARCHAR(100),
    FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Step 3: Insert Data
-- Vendors
INSERT INTO Vendors VALUES
('V001', 'NanoTech Solutions', 'contact@nanotech.in', '123456789012', 'State Bank of India', '9876543210'),
('V002', 'Spectra Instruments', 'info@spectrainst.com', '987654321098', 'Bank of Baroda', '8765432109'),
('V003', 'Quantum Equipments', 'sales@quantumeq.com', '456789123456', 'Canara Bank', '8899776655'),
('V004', 'MicroVision Labs', 'support@microvision.com', '654321789012', 'HDFC Bank', '9112233445'),
('V005', 'Analytica Pvt Ltd', 'service@analytica.co.in', '789123456789', 'ICICI Bank', '9123456780'),
('V006', 'TechLab Systems', 'info@techlab.io', '321654987012', 'Union Bank of India', '9988776655'),
('V007', 'VisionX Instruments', 'contact@visionx.net', '998877665544', 'Bank of India', '9001122334'),
('V008', 'UltraSpec Corp', 'hello@ultraspec.in', '887766554433', 'Dena Bank', '9090909090'),
('V009', 'CoreAnalytix', 'support@coreanalytix.org', '776655443322', 'Gujarat State Co-op Bank', '9345612789'),
('V010', 'LabTech Supplies', 'contact@labtechsupplies.in', '112233445566', 'Axis Bank', '9123001122');

-- Equipment
INSERT INTO Equipment VALUES
('E001', 'FE-SEM', 'Lab 202, Materials Bldg', 1, 'Operational'),
('E002', 'XRD', 'Lab 203, Materials Bldg', 1, 'Requires alignment'),
('E003', 'Confocal Microscope', 'Lab 204, Bio Block', 2, 'Operational'),
('E004', 'LC-MS', 'Lab 205, Chemistry Block', 1, 'Under maintenance'),
('E005', 'MALDI-ToF', 'Lab 206, Chemistry Block', 1, 'Operational'),
('E006', 'Probe Station', 'Lab 207, EE Block', 1, 'Operational'),
('E007', 'NMR Spectrometer', 'Lab 208, Physics Block', 1, 'Operational'),
('E008', 'Micro XCT', 'Lab 209, Materials Bldg', 1, 'Operational'),
('E009', 'PPMS', 'Lab 210, Physics Block', 1, 'Temperature unstable'),
('E010', 'CD Spectrometer', 'Lab 211, Chemistry Block', 2, 'Operational');

-- Lab Visits
INSERT INTO LabVisits VALUES
('LV001', 'VST00001', 'Rohan Mehta', 'PhD', '2 hrs', 'E001', '9123456789'),
('LV002', 'VST00002', 'Priya Sharma', 'Post Doc', '1.5 hrs', 'E002', '9011223344'),
('LV003', 'VST00003', 'Akash Nair', 'MTech', '1 hr', 'E003', '9887766554'),
('LV004', 'VST00004', 'Neha Patel', 'PhD', '2.5 hrs', 'E004', '9087654321'),
('LV005', 'VST00005', 'Karthik Rao', 'B.Tech', '1.5 hrs', 'E005', '9876543210'),
('LV006', 'VST00006', 'Vikram Singh', 'Professor', '3 hrs', 'E006', '9001122334'),
('LV007', 'VST00007', 'Sneha Iyer', 'NA', '1 hr', 'E007', '9112233445'),
('LV008', 'VST00008', 'Anjali Saxena', 'Post Doc', '2 hrs', 'E008', '9123456788'),
('LV009', 'VST00009', 'Deepak Tiwari', 'MTech', '1.25 hrs', 'E009', '9101010101'),
('LV010', 'VST00010', 'Tanya Kapoor', 'B.Tech', '1 hr', 'E010', '9022334455');

-- Maintenance Visits
INSERT INTO MaintenanceVisits VALUES
('MV001', 'V001', 'E001', '2025-03-10 09:00:00', '2025-09-10', 5500.00),
('MV002', 'V002', 'E002', '2025-03-12 11:00:00', '2025-10-12', 7200.00),
('MV003', 'V003', 'E003', '2025-03-15 14:30:00', '2025-09-15', 4500.00),
('MV004', 'V004', 'E004', '2025-03-18 10:00:00', '2025-08-18', 9000.00),
('MV005', 'V005', 'E005', '2025-03-19 15:00:00', '2025-09-19', 5200.00),
('MV006', 'V006', 'E006', '2025-03-21 09:45:00', '2025-09-21', 4700.00),
('MV007', 'V007', 'E007', '2025-03-23 12:30:00', '2025-09-23', 8000.00),
('MV008', 'V008', 'E008', '2025-03-25 13:00:00', '2025-09-25', 6100.00),
('MV009', 'V009', 'E009', '2025-03-26 14:00:00', '2025-09-26', 7100.00),
('MV010', 'V010', 'E010', '2025-03-28 16:00:00', '2025-09-28', 4300.00);

-- Consumable Inventory
INSERT INTO ConsumableInventory VALUES
('CI01', 'SEM Sample Holders', 50, 'V001', 250.00, 10),
('CI02', 'XRD Slides', 20, 'V002', 180.00, 5),
('CI03', 'NMR Tubes', 40, 'V003', 100.00, 15),
('CI04', 'LC-MS Solvents', 25, 'V004', 600.00, 10),
('CI05', 'Probe Needles', 15, 'V005', 350.00, 5),
('CI06', 'PPMS Test Samples', 30, 'V006', 500.00, 8),
('CI07', 'DLS Cuvettes', 60, 'V007', 90.00, 12),
('CI08', 'CD Sample Plates', 35, 'V008', 200.00, 7),
('CI09', 'ToF Matrix Reagents', 18, 'V009', 800.00, 6),
('CI10', 'XPS Reference Samples', 22, 'V010', 300.00, 8);

-- Software
INSERT INTO Software VALUES
('SW001', 'OriginPro', '2023', 'Academic Site License', 'ORG-XYZ-9999-AAAA', '2025-09-30', 'V001', 10, 'Lab PCs (201–210)'),
('SW002', 'COMSOL Multiphysics', '6.0', 'Annual Subscription', 'COMSOL-ABCD-1234', '2026-03-31', 'V002', 5, 'HPC Cluster, Lab 210'),
('SW003', 'MATLAB', 'R2025a', 'Academic Site License', 'MTLB-2025-XXXX', '2025-12-31', 'V003', 20, 'Institute-Wide'),
('SW004', 'XPS Control Suite', '1.2.3', 'Perpetual + Maintenance', 'XPS-0001-CTRL-SOFT', '2026-06-01', 'V004', 2, 'Attached to XPS'),
('SW005', 'Avizo', '2022', 'Floating License', 'AVIZO-1234-FLOAT', '2025-10-15', 'V005', 3, 'Lab 209 (XCT Analysis)'),
('SW006', 'ImageJ Pro', '1.53', 'Free Academic', 'N/A', NULL, 'V006', NULL, 'Institute PCs'),
('SW007', 'Thermo Xcalibur', '4.3', 'OEM License', 'THX-2025-7890', '2027-01-01', 'V007', 2, 'LC-MS Station (Lab 204)'),
('SW008', 'LabVIEW', '2023', 'Perpetual License', 'LV-2023-CTRL-LAB', '2028-12-31', 'V008', 6, 'EE Block, Lab 207'),
('SW009', 'TopSpin', '4.1', 'Academic License', 'TS-9876-3210', '2026-05-30', 'V009', 4, 'NMR Spectrometer Setup'),
('SW010', 'ChemDraw', '22.0', 'Annual Site License', 'CD-2025-INST', '2026-02-28', 'V010', 15, 'Chemistry Dept Labs');

DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL
);

INSERT INTO Users (name, email, password, role) VALUES
    ('Deepanjali Kumari', 'deepanjali.kumari@iitgn.ac.in', '22110069', 'Visitor'),
    ('Harshita Singh', 'harshita.singh@iitgn.ac.in', '22110140', 'Staff'),
    ('Anushika Mishra', 'anushika.mishra@iitgn.ac.in', '22110029', 'Staff'),
    ('Yash Kokane', 'yash.kokane@iitgn.ac.in', '20110237', 'Admin'),
    ('Ajay Verma', 'ajay.verma@gmail.com', '123456', 'patient'),
    ('Meera Nair', 'meera.nair@gmail.com', '123456', 'doctor'),
    ('Siddharth Rao', 'siddharth.rao@gmail.com', '123456', 'admin');

-- Step 4: Enhance Software table for better license management
ALTER TABLE Software 
ADD COLUMN total_seats INT DEFAULT 1,
ADD COLUMN used_seats INT DEFAULT 0,
ADD COLUMN license_model ENUM('Node-locked', 'Floating', 'Subscription', 'Site') NOT NULL DEFAULT 'Floating',
ADD COLUMN maintenance_expiry DATE,
ADD COLUMN purchase_date DATE,
ADD COLUMN purchase_cost DECIMAL(10, 2);

-- Step 5: Create License Management Tables

-- Create License Pool table to track license assignments
CREATE TABLE LicensePool (
    id INT AUTO_INCREMENT PRIMARY KEY,
    software_id VARCHAR(10) NOT NULL,
    total_seats INT NOT NULL DEFAULT 1,
    available_seats INT NOT NULL DEFAULT 1,
    license_key VARCHAR(255),
    license_model ENUM('Node-locked', 'Floating', 'Subscription', 'Site') NOT NULL,
    activation_date DATE,
    expiry_date DATE,
    maintenance_expiry DATE,
    vendor_id VARCHAR(10),
    purchase_cost DECIMAL(10, 2),
    purchase_order_ref VARCHAR(50),
    notes TEXT,
    FOREIGN KEY (software_id) REFERENCES Software(software_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- Create License Usage table to track active checkouts
CREATE TABLE LicenseUsage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    software_id VARCHAR(10) NOT NULL,
    user_id INT NOT NULL,
    checkout_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    host_name VARCHAR(100),
    checkout_location VARCHAR(100),
    expected_checkin DATETIME,
    FOREIGN KEY (software_id) REFERENCES Software(software_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create License Audit Log
CREATE TABLE LicenseAudit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    software_id VARCHAR(10) NOT NULL,
    user_id INT NOT NULL,
    action ENUM('checkout', 'checkin', 'deny', 'expire', 'admin_override') NOT NULL,
    action_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    session_id VARCHAR(255),
    details TEXT,
    FOREIGN KEY (software_id) REFERENCES Software(software_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create License Rules table for enforcing policy
CREATE TABLE LicenseRules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    software_id VARCHAR(10) NOT NULL,
    rule_type ENUM('time_limit', 'ip_range', 'user_group', 'department', 'hours') NOT NULL,
    rule_value TEXT NOT NULL,
    priority INT DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (software_id) REFERENCES Software(software_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (created_by) REFERENCES Users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- Create Software-User Group mapping for access control
CREATE TABLE UserGroups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE UserGroupMembers (
    group_id INT NOT NULL,
    user_id INT NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    added_by INT,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES UserGroups(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (added_by) REFERENCES Users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE SoftwareGroupAccess (
    software_id VARCHAR(10) NOT NULL,
    group_id INT NOT NULL,
    access_level ENUM('view', 'use', 'admin') NOT NULL DEFAULT 'use',
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    granted_by INT,
    PRIMARY KEY (software_id, group_id),
    FOREIGN KEY (software_id) REFERENCES Software(software_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (group_id) REFERENCES UserGroups(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES Users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- Step 6: Insert sample data for license management

-- Update existing software with license information
UPDATE Software SET 
    total_seats = 20,
    used_seats = 12,
    license_model = 'Site',
    maintenance_expiry = '2026-09-30',
    purchase_date = '2023-09-30',
    purchase_cost = 250000.00
WHERE software_id = 'SW001';

UPDATE Software SET 
    total_seats = 10,
    used_seats = 5,
    license_model = 'Floating',
    maintenance_expiry = '2026-03-31',
    purchase_date = '2024-03-31',
    purchase_cost = 180000.00
WHERE software_id = 'SW002';

UPDATE Software SET 
    total_seats = 50,
    used_seats = 25,
    license_model = 'Site',
    maintenance_expiry = '2026-12-31',
    purchase_date = '2023-12-31',
    purchase_cost = 500000.00
WHERE software_id = 'SW003';

-- Insert User Groups
INSERT INTO UserGroups (id, group_name, description) VALUES
(1, 'Materials Science', 'Faculty and students from Materials Science department'),
(2, 'Chemistry Lab', 'Chemistry department laboratory users'),
(3, 'Physics Researchers', 'Physics department research group'),
(4, 'Engineering', 'Engineering department staff and students'),
(5, 'License Administrators', 'Users with admin rights on licenses');

-- Insert Group Members
INSERT INTO UserGroupMembers (group_id, user_id, added_by) VALUES
(1, 1, 4), -- Deepanjali in Materials Science, added by Yash
(2, 2, 4), -- Harshita in Chemistry Lab, added by Yash
(3, 3, 4), -- Anushika in Physics Researchers, added by Yash
(4, 1, 4), -- Deepanjali also in Engineering
(5, 4, 4); -- Yash in License Administrators

-- Insert Software Group Access
INSERT INTO SoftwareGroupAccess (software_id, group_id, access_level, granted_by) VALUES
('SW001', 1, 'use', 4), -- OriginPro for Materials Science
('SW002', 1, 'use', 4), -- COMSOL for Materials Science
('SW003', 1, 'use', 4), -- MATLAB for Materials Science
('SW003', 2, 'use', 4), -- MATLAB for Chemistry Lab
('SW003', 3, 'use', 4), -- MATLAB for Physics Researchers
('SW003', 4, 'use', 4), -- MATLAB for Engineering
('SW005', 3, 'use', 4), -- Avizo for Physics Researchers
('SW007', 2, 'use', 4), -- Thermo Xcalibur for Chemistry Lab
('SW010', 2, 'use', 4); -- ChemDraw for Chemistry Lab

-- Insert License Pools
INSERT INTO LicensePool (software_id, total_seats, available_seats, license_key, license_model, activation_date, expiry_date, maintenance_expiry, vendor_id, purchase_cost, purchase_order_ref) VALUES
('SW001', 20, 8, 'ORG-XYZ-9999-AAAA', 'Site', '2023-09-30', '2025-09-30', '2026-09-30', 'V001', 250000.00, 'PO2023-456'),
('SW002', 10, 5, 'COMSOL-ABCD-1234', 'Floating', '2024-03-31', '2026-03-31', '2026-03-31', 'V002', 180000.00, 'PO2024-123'),
('SW003', 50, 25, 'MTLB-2025-XXXX', 'Site', '2023-12-31', '2025-12-31', '2026-12-31', 'V003', 500000.00, 'PO2023-789'),
('SW004', 2, 2, 'XPS-0001-CTRL-SOFT', 'Node-locked', '2022-06-01', '2026-06-01', '2026-06-01', 'V004', 120000.00, 'PO2022-234'),
('SW005', 3, 1, 'AVIZO-1234-FLOAT', 'Floating', '2022-10-15', '2025-10-15', '2025-10-15', 'V005', 75000.00, 'PO2022-567'),
('SW007', 2, 2, 'THX-2025-7890', 'Node-locked', '2023-01-01', '2027-01-01', '2025-01-01', 'V007', 230000.00, 'PO2023-345'),
('SW008', 6, 6, 'LV-2023-CTRL-LAB', 'Floating', '2023-12-31', '2028-12-31', '2024-12-31', 'V008', 190000.00, 'PO2023-678'),
('SW009', 4, 3, 'TS-9876-3210', 'Floating', '2022-05-30', '2026-05-30', '2024-05-30', 'V009', 145000.00, 'PO2022-901'),
('SW010', 15, 10, 'CD-2025-INST', 'Site', '2023-02-28', '2026-02-28', '2025-02-28', 'V010', 95000.00, 'PO2023-012');

-- Insert sample License Usage (current checkouts)
INSERT INTO LicenseUsage (software_id, user_id, checkout_time, last_heartbeat, session_id, ip_address, host_name, checkout_location) VALUES
('SW001', 1, NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 10 MINUTE, UUID(), '192.168.1.101', 'PC-MAT-101', 'Lab 202'),
('SW001', 2, NOW() - INTERVAL 1 HOUR, NOW() - INTERVAL 5 MINUTE, UUID(), '192.168.1.102', 'PC-CHEM-102', 'Lab 205'),
('SW002', 3, NOW() - INTERVAL 3 HOUR, NOW() - INTERVAL 15 MINUTE, UUID(), '192.168.1.103', 'PC-PHY-103', 'Lab 208'),
('SW003', 1, NOW() - INTERVAL 4 HOUR, NOW() - INTERVAL 20 MINUTE, UUID(), '192.168.1.101', 'PC-MAT-101', 'Lab 202'),
('SW003', 2, NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 8 MINUTE, UUID(), '192.168.1.102', 'PC-CHEM-102', 'Lab 205'),
('SW003', 3, NOW() - INTERVAL 1 HOUR, NOW() - INTERVAL 12 MINUTE, UUID(), '192.168.1.103', 'PC-PHY-103', 'Lab 208'),
('SW005', 3, NOW() - INTERVAL 5 HOUR, NOW() - INTERVAL 25 MINUTE, UUID(), '192.168.1.103', 'PC-PHY-103', 'Lab 208');

-- Insert sample License Audit records
INSERT INTO LicenseAudit (software_id, user_id, action, action_time, ip_address, session_id, details) VALUES
('SW001', 1, 'checkout', NOW() - INTERVAL 2 HOUR, '192.168.1.101', UUID(), 'Initial checkout'),
('SW001', 2, 'checkout', NOW() - INTERVAL 1 HOUR, '192.168.1.102', UUID(), 'Initial checkout'),
('SW002', 3, 'checkout', NOW() - INTERVAL 3 HOUR, '192.168.1.103', UUID(), 'Initial checkout'),
('SW002', 4, 'checkout', NOW() - INTERVAL 5 HOUR, '192.168.1.104', UUID(), 'Initial checkout'),
('SW002', 4, 'checkin', NOW() - INTERVAL 4 HOUR, '192.168.1.104', UUID(), 'Normal checkin'),
('SW003', 1, 'checkout', NOW() - INTERVAL 4 HOUR, '192.168.1.101', UUID(), 'Initial checkout'),
('SW003', 2, 'checkout', NOW() - INTERVAL 2 HOUR, '192.168.1.102', UUID(), 'Initial checkout'),
('SW003', 3, 'checkout', NOW() - INTERVAL 1 HOUR, '192.168.1.103', UUID(), 'Initial checkout'),
('SW001', 4, 'deny', NOW() - INTERVAL 30 MINUTE, '192.168.1.104', NULL, 'No licenses available'),
('SW005', 3, 'checkout', NOW() - INTERVAL 5 HOUR, '192.168.1.103', UUID(), 'Initial checkout');

-- Insert License Rules
INSERT INTO LicenseRules (software_id, rule_type, rule_value, priority, is_active, created_by) VALUES
('SW001', 'time_limit', '8', 100, TRUE, 4), -- 8-hour checkout limit for OriginPro
('SW002', 'ip_range', '192.168.1.0/24', 200, TRUE, 4), -- COMSOL only on campus network
('SW003', 'hours', '8:00-20:00', 300, TRUE, 4), -- MATLAB only during working hours
('SW003', 'user_group', '1,2,3,4', 400, TRUE, 4), -- MATLAB limited to specific groups
('SW005', 'department', 'Physics', 500, TRUE, 4); -- Avizo limited to Physics department

-- Create a function to update available seats based on usage
DELIMITER //
CREATE FUNCTION update_license_available_seats()
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE sw_id VARCHAR(10);
    DECLARE total INT;
    DECLARE used INT;
    
    -- Cursor for software IDs
    DECLARE sw_cursor CURSOR FOR 
        SELECT software_id FROM Software;
    
    -- Error handler
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN sw_cursor;
    
    -- Loop through software
    sw_loop: LOOP
        FETCH sw_cursor INTO sw_id;
        IF done THEN
            LEAVE sw_loop;
        END IF;
        
        -- Count active usage
        SELECT COUNT(*) INTO used FROM LicenseUsage WHERE software_id = sw_id;
        
        -- Update the Software table
        UPDATE Software SET used_seats = used WHERE software_id = sw_id;
        
        -- Update the LicensePool table
        SELECT total_seats INTO total FROM LicensePool WHERE software_id = sw_id LIMIT 1;
        IF total IS NOT NULL THEN
            UPDATE LicensePool 
            SET available_seats = total_seats - used 
            WHERE software_id = sw_id;
        END IF;
    END LOOP;
    
    CLOSE sw_cursor;
    RETURN 1;
END //
DELIMITER ;

-- Initial call to update seats
SELECT update_license_available_seats();


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

CREATE TABLE Lab_Visits (
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

CREATE TABLE Maintenance_Visits (
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

CREATE TABLE Consumable_Inventory (
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
INSERT INTO Lab_Visits VALUES
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
INSERT INTO Maintenance_Visits VALUES
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
INSERT INTO Consumable_Inventory VALUES
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

-- This script adds the necessary license tables to the existing cifdb database
-- Run this once to set up the license system

USE cifdb;

-- Add network licensing fields to Software table if they don't exist
ALTER TABLE Software 
ADD COLUMN IF NOT EXISTS is_network_license BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS license_server VARCHAR(100),
ADD COLUMN IF NOT EXISTS license_port INT,
ADD COLUMN IF NOT EXISTS license_protocol ENUM('TCP', 'UDP') DEFAULT 'TCP';

-- Create License_Allocations table for tracking license allocations
CREATE TABLE IF NOT EXISTS License_Allocations (
    allocation_id VARCHAR(10) PRIMARY KEY,
    software_id VARCHAR(10) NOT NULL,
    user_id INT NOT NULL,
    allocation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATETIME,
    mac_address VARCHAR(20),
    ip_address VARCHAR(15),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (software_id) REFERENCES Software(software_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create License_Sessions table for tracking license usage sessions
CREATE TABLE IF NOT EXISTS License_Sessions (
    session_id VARCHAR(10) PRIMARY KEY,
    allocation_id VARCHAR(10) NOT NULL,
    checkout_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checkin_time DATETIME,
    client_hostname VARCHAR(100),
    client_ip VARCHAR(15),
    heartbeat_last_time DATETIME,
    session_status ENUM('active', 'closed', 'expired', 'crashed') DEFAULT 'active',
    FOREIGN KEY (allocation_id) REFERENCES License_Allocations(allocation_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create License_Servers table
CREATE TABLE IF NOT EXISTS License_Servers (
    server_id VARCHAR(10) PRIMARY KEY,
    server_name VARCHAR(100) NOT NULL,
    server_ip VARCHAR(15) NOT NULL,
    server_port INT NOT NULL,
    protocol ENUM('TCP', 'UDP') DEFAULT 'TCP',
    heartbeat_interval INT DEFAULT 60, -- seconds
    status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
    max_connections INT DEFAULT 100
);

-- Add CATLAB to software if it doesn't exist
INSERT IGNORE INTO Software (software_id, software_name, version, license_type, license_key, license_expiry, vendor_id, max_installations, usage_location, is_network_license, license_server, license_port, license_protocol)
VALUES ('SW013', 'CATLAB', '1.0', 'Academic Floating License', 'CTLB-2024-ABCD-1234', '2025-12-31', 'V003', 10, 'Research Labs', TRUE, '127.0.0.1', 27000, 'TCP');

-- Add license server for CATLAB if it doesn't exist
INSERT IGNORE INTO License_Servers (server_id, server_name, server_ip, server_port, protocol, heartbeat_interval, status, max_connections)
VALUES ('LS001', 'CATLAB License Server', '127.0.0.1', 27000, 'TCP', 30, 'active', 25); 
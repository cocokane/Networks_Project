#!/usr/bin/env python3
import mysql.connector
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('setup_database')

def get_db_password():
    """Read database password from file"""
    try:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(parent_dir, 'database_pass.txt'), 'r') as f:
            for line in f:
                if line.startswith('password:'):
                    return line.strip().split('password:')[1].strip()
    except Exception as e:
        logger.error(f"Error reading database password: {e}")
        return None

def setup_database():
    """Ensure all required tables exist in the database"""
    password = get_db_password()
    if not password:
        logger.error("Could not read database password")
        return False
    
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': password,
    }
    
    try:
        # First connect without database to check if it exists
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS cifdb")
        conn.database = "cifdb"
        
        logger.info("Creating/checking tables...")
        
        # Check if Users table exists, create if it doesn't
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(255) NOT NULL
            )
        """)
        
        # Check if any users exist, add some if not
        cursor.execute("SELECT COUNT(*) FROM Users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            logger.info("Adding sample users")
            cursor.execute("""
                INSERT INTO Users (name, email, password, role) VALUES
                ('Deepanjali Kumari', 'deepanjali.kumari@iitgn.ac.in', '22110069', 'Visitor'),
                ('Harshita Singh', 'harshita.singh@iitgn.ac.in', '22110140', 'Staff'),
                ('Anushika Mishra', 'anushika.mishra@iitgn.ac.in', '22110029', 'Staff'),
                ('Yash Kokane', 'yash.kokane@iitgn.ac.in', '20110237', 'Admin'),
                ('Test User', 'test@example.com', 'password', 'Staff')
            """)
        
        # Create Software table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Software (
                software_id VARCHAR(10) PRIMARY KEY,
                software_name VARCHAR(100) NOT NULL,
                version VARCHAR(20),
                license_type VARCHAR(50),
                license_key VARCHAR(100),
                license_expiry DATE,
                vendor_id VARCHAR(10),
                max_installations INT,
                usage_location VARCHAR(100),
                is_network_license BOOLEAN DEFAULT FALSE,
                license_server VARCHAR(100),
                license_port INT,
                license_protocol ENUM('TCP', 'UDP') DEFAULT 'TCP'
            )
        """)
        
        # Check if CATLAB software exists, add if not
        cursor.execute("SELECT COUNT(*) FROM Software WHERE software_id = 'SW013'")
        software_count = cursor.fetchone()[0]
        
        if software_count == 0:
            logger.info("Adding CATLAB software")
            cursor.execute("""
                INSERT INTO Software VALUES
                ('SW013', 'CATLAB', '1.0', 'Academic Floating License', 'CTLB-2024-ABCD-1234', 
                '2025-12-31', NULL, 10, 'Research Labs', TRUE, '127.0.0.1', 27000, 'TCP')
            """)
        
        # Create License_Allocations table if it doesn't exist
        cursor.execute("""
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
            )
        """)
        
        # Create License_Sessions table if it doesn't exist
        cursor.execute("""
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
            )
        """)
        
        # Create License_Servers table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS License_Servers (
                server_id VARCHAR(10) PRIMARY KEY,
                server_name VARCHAR(100) NOT NULL,
                server_ip VARCHAR(15) NOT NULL,
                server_port INT NOT NULL,
                protocol ENUM('TCP', 'UDP') DEFAULT 'TCP',
                heartbeat_interval INT DEFAULT 60,
                status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
                max_connections INT DEFAULT 100
            )
        """)
        
        # Check if license server exists, add if not
        cursor.execute("SELECT COUNT(*) FROM License_Servers WHERE server_id = 'LS001'")
        server_count = cursor.fetchone()[0]
        
        if server_count == 0:
            logger.info("Adding license server")
            cursor.execute("""
                INSERT INTO License_Servers VALUES
                ('LS001', 'CATLAB License Server', '127.0.0.1', 27000, 'TCP', 30, 'active', 25)
            """)
        
        conn.commit()
        logger.info("Database setup completed successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        return False
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    print("Setting up CATLAB database...")
    if setup_database():
        print("Database setup completed successfully!")
    else:
        print("Database setup failed. See log for details.")
        sys.exit(1) 
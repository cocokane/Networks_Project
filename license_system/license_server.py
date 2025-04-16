   # -*- coding: utf-8 -*-
import socket
import threading
import json
import time
import mysql.connector
from datetime import datetime
import logging
import uuid
import os
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("license_server.log")
    ]
)

logger = logging.getLogger('license_server')

class LicenseServer:
    def __init__(self, host='0.0.0.0', port=27000, db_config=None):
        self.host = host
        self.port = port
        
        # Default database configuration
        self.db_config = db_config or {
            'host': '127.0.0.1',
            'user': 'root',
            'password': self.get_db_password(),
            'database': 'cifdb'
        }
        
        self.active_connections = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        
        logger.info(f"License server initialized with config: {self.db_config}")
    
    def get_db_password(self):
        """Read database password from file"""
        try:
            # Go up one directory to find the database_pass.txt file
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            with open(os.path.join(parent_dir, 'database_pass.txt'), 'r') as f:
                for line in f:
                    if line.startswith('password:'):
                        return line.strip().split('password:')[1].strip()
        except Exception as e:
            logger.error(f"Error reading database password: {e}")
            return None
    
    def start(self):
        """Start the license server"""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            logger.info(f"License server started on {self.host}:{self.port}")
            
            # Start heartbeat monitoring in a separate thread
            heartbeat_thread = threading.Thread(target=self.monitor_heartbeats)
            heartbeat_thread.daemon = True
            heartbeat_thread.start()
            
            try:
                while self.running:
                    client_socket, client_address = self.server_socket.accept()
                    logger.info(f"Connection from {client_address}")
                    
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                    client_thread.daemon = True
                    client_thread.start()
            except KeyboardInterrupt:
                logger.info("Server shutting down...")
            finally:
                self.server_socket.close()
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            
    def handle_client(self, client_socket, client_address):
        """Handle client connections"""
        try:
            data = client_socket.recv(1024)
            if not data:
                return
                
            request = json.loads(data.decode('utf-8'))
            response = self.process_request(request, client_address)
            
            client_socket.send(json.dumps(response).encode('utf-8'))
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
    
    def process_request(self, request, client_address):
        """Process different types of license requests"""
        command = request.get('command')
        
        if command == 'checkout':
            return self.checkout_license(request, client_address)
        elif command == 'checkin':
            return self.checkin_license(request)
        elif command == 'heartbeat':
            return self.update_heartbeat(request)
        elif command == 'query':
            return self.query_license(request)
        else:
            logger.warning(f"Unknown command received: {command}")
            return {'status': 'error', 'message': 'Unknown command'}
    
    def checkout_license(self, request, client_address):
        """Process a license checkout request"""
        software_id = request.get('software_id')
        user_id = request.get('user_id')
        client_hostname = request.get('hostname')
        mac_address = request.get('mac_address')
        
        logger.info(f"License checkout request: software={software_id}, user={user_id}, host={client_hostname}")
        
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Check if software exists and has available licenses
            cursor.execute("""
                SELECT s.*, COUNT(ls.session_id) as active_sessions 
                FROM Software s
                LEFT JOIN License_Allocations la ON s.software_id = la.software_id
                LEFT JOIN License_Sessions ls ON la.allocation_id = ls.allocation_id AND ls.session_status = 'active'
                WHERE s.software_id = %s
                GROUP BY s.software_id
            """, (software_id,))
            
            software = cursor.fetchone()
            if not software:
                logger.error(f"Software {software_id} not found")
                return {'status': 'error', 'message': 'Software not found'}
            
            # Check if user has an existing active session for this software
            cursor.execute("""
                SELECT ls.session_id 
                FROM License_Allocations la
                JOIN License_Sessions ls ON la.allocation_id = ls.allocation_id
                WHERE la.user_id = %s AND la.software_id = %s AND ls.session_status = 'active'
            """, (user_id, software_id))
            
            existing_session = cursor.fetchone()
            if existing_session:
                logger.warning(f"User {user_id} already has an active session: {existing_session['session_id']}")
                return {'status': 'error', 'message': 'You already have an active license for this software'}
            
            # Check if user has allocation
            cursor.execute("""
                SELECT * FROM License_Allocations 
                WHERE software_id = %s AND user_id = %s AND is_active = TRUE
                AND (expiry_date IS NULL OR expiry_date > NOW())
            """, (software_id, user_id))
            
            allocation = cursor.fetchone()
            
            # Check if we have available licenses
            if software['active_sessions'] >= software['max_installations'] and not allocation:
                logger.warning(f"No licenses available for {software_id}, active={software['active_sessions']}, max={software['max_installations']}")
                return {'status': 'error', 'message': 'No licenses available'}
            
            # If user doesn't have an allocation, check registration
            if not allocation:
                logger.warning(f"User {user_id} has no allocation for {software_id}")
                return {'status': 'error', 'message': 'You need to register for a license in the application first. Please complete license registration.'}
            
            # Create a session
            # Generate a shorter session ID that fits in VARCHAR(10)
            # Use 'LS' prefix + last 8 digits of timestamp
            session_id = f"LS{str(int(time.time()))[-8:]}"

            # Ensure allocation_id fits into VARCHAR(10)
            safe_allocation_id = allocation['allocation_id'][:10]

            cursor.execute("""
                INSERT INTO License_Sessions
                (session_id, allocation_id, checkout_time, client_hostname, client_ip, heartbeat_last_time, session_status)
                VALUES (%s, %s, NOW(), %s, %s, NOW(), 'active')
            """, (session_id, safe_allocation_id, client_hostname, client_address[0]))
            conn.commit()
            
            # Add to active connections
            self.active_connections[session_id] = {
                'allocation_id': safe_allocation_id,
                'last_heartbeat': datetime.now(),
                'address': client_address
            }
            
            logger.info(f"License checked out successfully: session={session_id}")
            
            return {
                'status': 'success',
                'message': 'License checked out successfully',
                'session_id': session_id,
                'expiry': allocation['expiry_date'].isoformat() if allocation['expiry_date'] else None
            }
            
        except Exception as e:
            logger.error(f"Error checking out license: {e}")
            try:
                conn.rollback()
            except:
                pass
            return {'status': 'error', 'message': f'Error checking out license: {str(e)}'}
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
    
    def checkin_license(self, request):
        """Process a license check-in request"""
        session_id = request.get('session_id')
        
        if not session_id:
            return {'status': 'error', 'message': 'Missing session_id'}
        
        logger.info(f"License checkin request: session={session_id}")
        
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE License_Sessions
                SET checkin_time = NOW(), session_status = 'closed'
                WHERE session_id = %s AND session_status = 'active'
            """, (session_id,))
            
            if cursor.rowcount == 0:
                logger.warning(f"Session {session_id} not found or already closed")
                return {'status': 'error', 'message': 'Session not found or already closed'}
            
            conn.commit()
            
            # Remove from active connections
            if session_id in self.active_connections:
                del self.active_connections[session_id]
            
            logger.info(f"License checked in successfully: session={session_id}")
            return {'status': 'success', 'message': 'License checked in successfully'}
        except Exception as e:
            logger.error(f"Error checking in license: {e}")
            try:
                conn.rollback()
            except:
                pass
            return {'status': 'error', 'message': f'Error checking in license: {str(e)}'}
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
    
    def update_heartbeat(self, request):
        """Process a heartbeat update request"""
        session_id = request.get('session_id')
        
        if not session_id:
            return {'status': 'error', 'message': 'Missing session_id'}
        
        logger.debug(f"Heartbeat update: session={session_id}")
        
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE License_Sessions
                SET heartbeat_last_time = NOW()
                WHERE session_id = %s AND session_status = 'active'
            """, (session_id,))
            
            if cursor.rowcount == 0:
                logger.warning(f"Session {session_id} not found or not active")
                return {'status': 'error', 'message': 'Session not found or not active'}
            
            conn.commit()
            
            # Update active connections
            if session_id in self.active_connections:
                self.active_connections[session_id]['last_heartbeat'] = datetime.now()
            
            return {'status': 'success', 'message': 'Heartbeat updated'}
        except Exception as e:
            logger.error(f"Error updating heartbeat: {e}")
            try:
                conn.rollback()
            except:
                pass
            return {'status': 'error', 'message': f'Error updating heartbeat: {str(e)}'}
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
    
    def query_license(self, request):
        """Query license information"""
        software_id = request.get('software_id')
        
        logger.info(f"License query request: software={software_id}")
        
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT s.*, COUNT(ls.session_id) as active_sessions 
                FROM Software s
                LEFT JOIN License_Allocations la ON s.software_id = la.software_id
                LEFT JOIN License_Sessions ls ON la.allocation_id = ls.allocation_id AND ls.session_status = 'active'
                WHERE s.software_id = %s
                GROUP BY s.software_id
            """, (software_id,))
            
            software = cursor.fetchone()
            if not software:
                logger.warning(f"Software {software_id} not found")
                return {'status': 'error', 'message': 'Software not found'}
            
            available = software['max_installations'] - software['active_sessions']
            
            return {
                'status': 'success',
                'software_name': software['software_name'],
                'version': software['version'],
                'total_licenses': software['max_installations'],
                'active_sessions': software['active_sessions'],
                'available_licenses': available if available >= 0 else 0
            }
        except Exception as e:
            logger.error(f"Error querying license: {e}")
            return {'status': 'error', 'message': f'Error querying license: {str(e)}'}
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
    
    def monitor_heartbeats(self):
        """Check for stale heartbeats and mark sessions as expired"""
        logger.info("Starting heartbeat monitoring thread")
        while self.running:
            current_time = datetime.now()
            expired_sessions = []
            
            # Find expired sessions (no heartbeat for more than 2 minutes)
            for session_id, data in list(self.active_connections.items()):
                if (current_time - data['last_heartbeat']).total_seconds() > 120:
                    expired_sessions.append(session_id)
                    logger.warning(f"Session {session_id} has expired (no heartbeat for >2 mins)")
            
            # Update database for expired sessions
            if expired_sessions:
                try:
                    conn = mysql.connector.connect(**self.db_config)
                    cursor = conn.cursor()
                    
                    for session_id in expired_sessions:
                        cursor.execute("""
                            UPDATE License_Sessions
                            SET session_status = 'expired', checkin_time = NOW()
                            WHERE session_id = %s AND session_status = 'active'
                        """, (session_id,))
                        
                        # Remove from active connections
                        if session_id in self.active_connections:
                            del self.active_connections[session_id]
                    
                    conn.commit()
                    logger.info(f"Marked {len(expired_sessions)} sessions as expired")
                except Exception as e:
                    logger.error(f"Error updating expired sessions: {e}")
                finally:
                    try:
                        cursor.close()
                        conn.close()
                    except:
                        pass
            
            # Sleep for a while before checking again
            time.sleep(30)

if __name__ == "__main__":
    port = 27000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            pass
    
    print(f"Starting CATLAB License Server on port {port}...")
    server = LicenseServer(port=port)
    server.start()

import socket
import json
import threading
import time
import platform
import uuid
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('license_client')

class LicenseClient:
    def __init__(self, server_ip, server_port, software_id, user_id):
        self.server_ip = server_ip
        self.server_port = server_port
        self.software_id = software_id
        self.user_id = user_id
        self.session_id = None
        self.heartbeat_thread = None
        self.is_running = False
        self.last_heartbeat_time = None
        self.heartbeat_interval = 30  # seconds
        
    def get_mac_address(self):
        """Get the MAC address of the client"""
        return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                        for elements in range(0, 2*6, 2)][::-1])
    
    def get_hostname(self):
        """Get the hostname of the client"""
        return platform.node()
    
    def send_request(self, request):
        """Send a request to the license server and get response"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)  # 10 second timeout
            s.connect((self.server_ip, self.server_port))
            s.send(json.dumps(request).encode('utf-8'))
            
            response = s.recv(1024).decode('utf-8')
            s.close()
            
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error communicating with license server: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def checkout_license(self):
        """Check out a license from the server"""
        logger.info(f"Attempting to check out license for {self.software_id} for user {self.user_id}")
        
        request = {
            'command': 'checkout',
            'software_id': self.software_id,
            'user_id': self.user_id,
            'hostname': self.get_hostname(),
            'mac_address': self.get_mac_address()
        }
        
        response = self.send_request(request)
        
        if response.get('status') == 'success':
            self.session_id = response.get('session_id')
            logger.info(f"License checked out successfully. Session ID: {self.session_id}")
            
            # Start heartbeat in a separate thread
            self.is_running = True
            self.heartbeat_thread = threading.Thread(target=self.send_heartbeats)
            self.heartbeat_thread.daemon = True
            self.heartbeat_thread.start()
        else:
            logger.error(f"Failed to check out license: {response.get('message')}")
        
        return response
    
    def checkin_license(self):
        """Check in a license to the server"""
        if not self.session_id:
            return {'status': 'error', 'message': 'No active license session'}
        
        logger.info(f"Checking in license for session {self.session_id}")
        
        request = {
            'command': 'checkin',
            'session_id': self.session_id
        }
        
        response = self.send_request(request)
        
        if response.get('status') == 'success':
            logger.info("License checked in successfully")
            self.is_running = False
            self.session_id = None
        else:
            logger.error(f"Failed to check in license: {response.get('message')}")
        
        return response
    
    def query_license(self):
        """Query license information"""
        logger.info(f"Querying license information for {self.software_id}")
        
        request = {
            'command': 'query',
            'software_id': self.software_id
        }
        
        return self.send_request(request)
    
    def send_heartbeats(self):
        """Send periodic heartbeats to keep the license active"""
        logger.info(f"Starting heartbeat thread for session {self.session_id}")
        
        while self.is_running and self.session_id:
            try:
                request = {
                    'command': 'heartbeat',
                    'session_id': self.session_id
                }
                
                response = self.send_request(request)
                
                if response.get('status') == 'success':
                    self.last_heartbeat_time = time.time()
                    logger.debug(f"Heartbeat sent successfully for session {self.session_id}")
                else:
                    logger.error(f"Heartbeat failed: {response.get('message')}")
                    # Don't stop the thread, we'll try again
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
            
            # Sleep for the heartbeat interval before sending the next heartbeat
            time.sleep(self.heartbeat_interval)
        
        logger.info(f"Heartbeat thread stopped for session {self.session_id}")

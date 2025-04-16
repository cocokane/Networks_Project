import socket
import json
import threading
import time
import platform
import uuid
import logging
import traceback
from datetime import datetime

# Set up logging with trace IDs
def setup_logger():
    """Set up the license client logger with trace ID support"""
    logger = logging.getLogger('license_client')
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create trace_id filter
    class TraceIDFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, 'trace_id'):
                record.trace_id = 'NONE'
            return True
    
    trace_filter = TraceIDFilter()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(trace_filter)
    logger.addHandler(console_handler)
    
    # Log initialization
    logger.info("License client logger initialized", extra={'trace_id': 'INIT'})
    
    return logger

# Initialize logger
logger = setup_logger()

# Create a trace ID context manager
class TraceContext:
    """Context manager for tracking operations with a trace ID"""
    def __init__(self, name):
        self.name = name
        self.trace_id = str(uuid.uuid4())[:8]  # Short trace ID for readability
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting operation: {self.name}", extra={'trace_id': self.trace_id})
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is not None:
            logger.error(f"Operation {self.name} failed after {duration:.2f}s: {exc_val}", 
                        extra={'trace_id': self.trace_id})
        else:
            logger.info(f"Operation {self.name} completed successfully in {duration:.2f}s", 
                        extra={'trace_id': self.trace_id})

class LicenseClient:
    def __init__(self, server_ip, server_port, software_id, user_id):
        with TraceContext("LicenseClient.init") as ctx:
            self.server_ip = server_ip
            self.server_port = server_port
            self.software_id = software_id
            self.user_id = user_id
            self.session_id = None
            self.heartbeat_thread = None
            self.is_running = False
            self.last_heartbeat_time = None
            self.heartbeat_interval = 30  # seconds
            self.trace_id = ctx.trace_id
            
            logger.info(f"License client initialized for software {software_id}, user {user_id}", 
                     extra={'trace_id': ctx.trace_id})
            logger.debug(f"Server connection details: {server_ip}:{server_port}", 
                      extra={'trace_id': ctx.trace_id})
            
            # Try to get host info immediately
            try:
                hostname = self.get_hostname()
                mac = self.get_mac_address()
                logger.debug(f"Client machine info - hostname: {hostname}, MAC: {mac}", 
                          extra={'trace_id': ctx.trace_id})
            except Exception as e:
                logger.warning(f"Could not get initial machine info: {e}", 
                            extra={'trace_id': ctx.trace_id})
        
    def get_mac_address(self):
        """Get the MAC address of the client"""
        with TraceContext("get_mac_address") as ctx:
            try:
                mac_addr = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                            for elements in range(0, 2*6, 2)][::-1])
                logger.debug(f"Retrieved MAC address: {mac_addr}", extra={'trace_id': ctx.trace_id})
                return mac_addr
            except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"Error getting MAC address: {e}\n{error_details}", 
                          extra={'trace_id': ctx.trace_id})
                return "00:00:00:00:00:00"  # Fallback
    
    def get_hostname(self):
        """Get the hostname of the client"""
        with TraceContext("get_hostname") as ctx:
            try:
                hostname = platform.node()
                logger.debug(f"Retrieved hostname: {hostname}", extra={'trace_id': ctx.trace_id})
                return hostname
            except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"Error getting hostname: {e}\n{error_details}", 
                          extra={'trace_id': ctx.trace_id})
                return "unknown-host"  # Fallback
    
    def send_request(self, request):
        """Send a request to the license server and get response"""
        with TraceContext("send_request") as ctx:
            try:
                request_type = request.get('command', 'unknown')
                logger.debug(f"Preparing to send {request_type} request to {self.server_ip}:{self.server_port}", 
                          extra={'trace_id': ctx.trace_id})
                
                # Create socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)  # 10 second timeout
                logger.debug(f"Socket created, timeout set to 10s", extra={'trace_id': ctx.trace_id})
                
                # Connect
                logger.debug(f"Connecting to {self.server_ip}:{self.server_port}", 
                          extra={'trace_id': ctx.trace_id})
                connect_start = time.time()
                
                try:
                    s.connect((self.server_ip, self.server_port))
                    connect_time = time.time() - connect_start
                    logger.debug(f"Connected in {connect_time:.3f}s", extra={'trace_id': ctx.trace_id})
                    
                    # Send request
                    request_data = json.dumps(request).encode('utf-8')
                    logger.debug(f"Sending {len(request_data)} bytes", extra={'trace_id': ctx.trace_id})
                    s.send(request_data)
                    
                    # Receive response
                    logger.debug(f"Waiting for response", extra={'trace_id': ctx.trace_id})
                    response_data = s.recv(1024).decode('utf-8')
                    logger.debug(f"Received {len(response_data)} bytes", extra={'trace_id': ctx.trace_id})
                    
                    # Close socket
                    s.close()
                    logger.debug(f"Socket closed", extra={'trace_id': ctx.trace_id})
                    
                    # Parse response
                    try:
                        response = json.loads(response_data)
                        status = response.get('status', 'unknown')
                        logger.info(f"Response received with status: {status}", extra={'trace_id': ctx.trace_id})
                        return response
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON response: {e}\nRaw data: {response_data}", 
                                  extra={'trace_id': ctx.trace_id})
                        return {'status': 'error', 'message': f'Invalid JSON response: {e}'}
                
                except socket.timeout:
                    logger.error(f"Connection timeout to {self.server_ip}:{self.server_port}", 
                              extra={'trace_id': ctx.trace_id})
                    s.close()
                    return {'status': 'error', 'message': 'Connection timeout'}
                
                except ConnectionRefusedError:
                    logger.error(f"Connection refused by {self.server_ip}:{self.server_port}", 
                              extra={'trace_id': ctx.trace_id})
                    s.close()
                    return {'status': 'error', 'message': 'Connection refused - is the server running?'}
                
            except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"Error communicating with license server: {e}\n{error_details}", 
                          extra={'trace_id': ctx.trace_id})
                return {'status': 'error', 'message': str(e)}
    
    def checkout_license(self):
        """Check out a license from the server"""
        with TraceContext("checkout_license") as ctx:
            logger.info(f"Attempting to check out license for software {self.software_id} for user {self.user_id}", 
                     extra={'trace_id': ctx.trace_id})
            
            # Gather client information
            hostname = self.get_hostname()
            mac_address = self.get_mac_address()
            
            # Prepare request
            request = {
                'command': 'checkout',
                'software_id': self.software_id,
                'user_id': self.user_id,
                'hostname': hostname,
                'mac_address': mac_address,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send request
            response = self.send_request(request)
            
            if response.get('status') == 'success':
                self.session_id = response.get('session_id')
                logger.info(f"License checked out successfully. Session ID: {self.session_id}", 
                         extra={'trace_id': ctx.trace_id})
                
                # Start heartbeat in a separate thread
                self.is_running = True
                self.heartbeat_thread = threading.Thread(target=self.send_heartbeats)
                self.heartbeat_thread.daemon = True
                self.heartbeat_thread.start()
                logger.debug(f"Heartbeat thread started", extra={'trace_id': ctx.trace_id})
            else:
                error_msg = response.get('message', 'Unknown error')
                logger.error(f"Failed to check out license: {error_msg}", extra={'trace_id': ctx.trace_id})
            
            return response
    
    def checkin_license(self):
        """Check in a license to the server"""
        with TraceContext("checkin_license") as ctx:
            if not self.session_id:
                logger.warning(f"Checkin attempted with no active session", extra={'trace_id': ctx.trace_id})
                return {'status': 'error', 'message': 'No active license session'}
            
            logger.info(f"Checking in license for session {self.session_id}", extra={'trace_id': ctx.trace_id})
            
            # Prepare request
            request = {
                'command': 'checkin',
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Stop heartbeat thread
            if self.heartbeat_thread and self.heartbeat_thread.is_alive():
                logger.debug(f"Setting is_running to False to stop heartbeat thread", 
                          extra={'trace_id': ctx.trace_id})
                self.is_running = False
                time.sleep(0.5)  # Give the thread a moment to exit
            
            # Send request
            response = self.send_request(request)
            
            if response.get('status') == 'success':
                logger.info(f"License checked in successfully for session {self.session_id}", 
                         extra={'trace_id': ctx.trace_id})
                old_session = self.session_id
                self.session_id = None
                logger.debug(f"Session {old_session} cleared", extra={'trace_id': ctx.trace_id})
            else:
                error_msg = response.get('message', 'Unknown error')
                logger.error(f"Failed to check in license: {error_msg}", extra={'trace_id': ctx.trace_id})
            
            return response
    
    def query_license(self):
        """Query license information"""
        with TraceContext("query_license") as ctx:
            logger.info(f"Querying license information for {self.software_id}", extra={'trace_id': ctx.trace_id})
            
            # Prepare request
            request = {
                'command': 'query',
                'software_id': self.software_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send request
            response = self.send_request(request)
            
            if response.get('status') == 'success':
                available = response.get('available_licenses', 'unknown')
                total = response.get('total_licenses', 'unknown')
                logger.info(f"License query successful: {available}/{total} licenses available", 
                         extra={'trace_id': ctx.trace_id})
            else:
                error_msg = response.get('message', 'Unknown error')
                logger.error(f"License query failed: {error_msg}", extra={'trace_id': ctx.trace_id})
            
            return response
    
    def send_heartbeats(self):
        """Send periodic heartbeats to keep the license active"""
        heartbeat_trace_id = str(uuid.uuid4())[:8]  # Create a dedicated trace ID for heartbeat thread
        logger.info(f"Starting heartbeat thread for session {self.session_id}", 
                 extra={'trace_id': heartbeat_trace_id})
        
        while self.is_running and self.session_id:
            try:
                # Prepare request
                request = {
                    'command': 'heartbeat',
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Send request
                logger.debug(f"Sending heartbeat for session {self.session_id}", 
                          extra={'trace_id': heartbeat_trace_id})
                response = self.send_request(request)
                
                if response.get('status') == 'success':
                    self.last_heartbeat_time = time.time()
                    logger.debug(f"Heartbeat successful for session {self.session_id}", 
                              extra={'trace_id': heartbeat_trace_id})
                else:
                    # Log specific error from server if available
                    error_msg = response.get('message', 'Unknown reason')
                    logger.error(f"Heartbeat failed for session {self.session_id}: {error_msg}", 
                              extra={'trace_id': heartbeat_trace_id})
                    
                    # Check if session is invalid
                    if "invalid session" in error_msg.lower() or "not found" in error_msg.lower():
                        logger.warning(f"Session invalid, stopping heartbeat", 
                                    extra={'trace_id': heartbeat_trace_id})
                        self.is_running = False
                        break

            except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"Error in heartbeat: {e}\n{error_details}", 
                          extra={'trace_id': heartbeat_trace_id})
            
            # Sleep for the heartbeat interval before sending the next heartbeat
            logger.debug(f"Sleeping for {self.heartbeat_interval}s before next heartbeat", 
                      extra={'trace_id': heartbeat_trace_id})
            
            # Check is_running flag every second rather than blocking for the full interval
            for _ in range(self.heartbeat_interval):
                if not self.is_running:
                    break
                time.sleep(1)
        
        logger.info(f"Heartbeat thread stopped for session {self.session_id}", 
                 extra={'trace_id': heartbeat_trace_id})

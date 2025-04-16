# license_system/smolcatlab.py

import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
import logging
import time
import mysql.connector
import hashlib
import re
import uuid
import traceback
from datetime import datetime, timedelta

# Ensure the license_client module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from license_system.license_client import LicenseClient
except ImportError:
    print("Error: Could not import LicenseClient. Make sure it's in the correct path.")
    sys.exit(1)

# --- Configuration ---
LOG_LEVEL = logging.DEBUG  # Use DEBUG to see detailed logs
SERVER_IP = '127.0.0.1'    # License server IP
SERVER_PORT = 27000        # License server port
SOFTWARE_ID = 'SW013'      # Software ID for CATLAB
# --- End Configuration ---

# Set up enhanced logging system
def setup_logger():
    """Set up the logging system with console and file output"""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Create a unique log file name with timestamp
    log_file = os.path.join(log_dir, f'smolcatlab_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Configure logging
    logger = logging.getLogger('smolcatlab')
    logger.setLevel(LOG_LEVEL)
    
    # Clear existing handlers (in case this is called multiple times)
    logger.handlers = []
    
    # Create trace_id filter - define this first before creating handlers
    class TraceIDFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, 'trace_id'):
                record.trace_id = 'NONE'
            return True
    
    trace_filter = TraceIDFilter()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s')
    console_handler.setFormatter(console_formatter)
    # Add filter to handler before adding handler to logger
    console_handler.addFilter(trace_filter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(LOG_LEVEL)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s')
    file_handler.setFormatter(file_formatter)
    # Add filter to handler before adding handler to logger
    file_handler.addFilter(trace_filter)
    logger.addHandler(file_handler)
    
    # Print information about the log file location
    print(f"Logging to: {log_file}")
    # Use extra parameter to provide trace_id value
    logger.info(f"Logging initialized. Log file: {log_file}", extra={'trace_id': 'INIT'})
    
    return logger

# Initialize logger
logger = setup_logger()

# Create a trace ID context manager for operation tracking
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

class DatabaseManager:
    """Handles database operations"""
    def __init__(self):
        with TraceContext("DatabaseManager.init"):
            self.db_config = {
                'host': '127.0.0.1',
                'user': 'root',
                'password': 'Sandeep2107*',
                'database': 'cifdb'
            }
            logger.debug("Database config initialized with host=%s, user=%s, database=%s", 
                        self.db_config['host'], self.db_config['user'], self.db_config['database'],
                        extra={'trace_id': 'INIT'})
            
            # Try to load password from file
            password = self.get_db_password()
            if password:
                logger.debug("Password loaded from file successfully", extra={'trace_id': 'INIT'})
                self.db_config['password'] = password
            else:
                logger.warning("Could not load password from file, using default", extra={'trace_id': 'INIT'})
        
    def get_db_password(self):
        """Read database password from file"""
        with TraceContext("get_db_password") as ctx:
            try:
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                db_pass_file = os.path.join(parent_dir, 'database_pass.txt')
                logger.debug(f"Reading password from: {db_pass_file}", extra={'trace_id': ctx.trace_id})
                
                if not os.path.exists(db_pass_file):
                    logger.error(f"Password file not found: {db_pass_file}", extra={'trace_id': ctx.trace_id})
                    return None
                
                with open(db_pass_file, 'r') as f:
                    logger.debug("Password file opened successfully", extra={'trace_id': ctx.trace_id})
                    content = f.read()
                    logger.debug(f"Password file content length: {len(content)} chars", extra={'trace_id': ctx.trace_id})
                    
                    # Debug the file content line by line, masking actual password
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'password:' in line.lower():
                            masked_line = line.split('password:')[0] + 'password: ********'
                            logger.debug(f"Line {i+1}: {masked_line}", extra={'trace_id': ctx.trace_id})
                        else:
                            logger.debug(f"Line {i+1}: {line}", extra={'trace_id': ctx.trace_id})
                    
                    for line in content.split('\n'):
                        if line.startswith('password:'):
                            password = line.strip().split('password:')[1].strip()
                            logger.debug("Password found in file", extra={'trace_id': ctx.trace_id})
                            return password
                
                logger.error("No password line found in file", extra={'trace_id': ctx.trace_id})
                return None
            except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"Error reading database password: {e}\n{error_details}", extra={'trace_id': ctx.trace_id})
                return None
    
    def get_connection(self):
        """Get a database connection"""
        with TraceContext("get_connection") as ctx:
            logger.debug(f"Attempting database connection to {self.db_config['host']}, database={self.db_config['database']}", 
                       extra={'trace_id': ctx.trace_id})
            try:
                conn = mysql.connector.connect(**self.db_config)
                logger.debug(f"Database connection successful. Connected to {self.db_config['database']}", 
                           extra={'trace_id': ctx.trace_id})
                return conn
            except mysql.connector.Error as e:
                error_details = traceback.format_exc()
                logger.error(f"Database connection error: {e}\n{error_details}", extra={'trace_id': ctx.trace_id})
                # Log additional details about the connection attempt
                logger.error(f"Connection parameters: host={self.db_config['host']}, "
                           f"user={self.db_config['user']}, database={self.db_config['database']}",
                           extra={'trace_id': ctx.trace_id})
                raise
    
    def authenticate_user(self, email_or_username, password):
        """Authenticate a user with provided credentials"""
        with TraceContext("authenticate_user") as ctx:
            conn = None
            try:
                logger.debug(f"Authenticating user: {email_or_username}", extra={'trace_id': ctx.trace_id})
                conn = self.get_connection()
                cursor = conn.cursor(dictionary=True)
                
                # Hash the password for comparison with stored hash
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                logger.debug(f"Password hashed for comparison", extra={'trace_id': ctx.trace_id})
                
                # Try to find user by email OR username
                query = """
                    SELECT id, name, email, role FROM users 
                    WHERE (email = %s OR name = %s) AND password = %s
                """
                logger.debug(f"Executing query with hashed password", extra={'trace_id': ctx.trace_id})
                cursor.execute(query, (email_or_username, email_or_username, hashed_password))
                
                user = cursor.fetchone()
                
                # If no match with hash, try plain password (for testing/development)
                if not user:
                    logger.debug(f"No match with hashed password, trying plain password", extra={'trace_id': ctx.trace_id})
                    cursor.execute(query, (email_or_username, email_or_username, password))
                    user = cursor.fetchone()
                
                if user:
                    logger.info(f"User authenticated successfully: {user['name']} (ID: {user['id']})", 
                               extra={'trace_id': ctx.trace_id})
                else:
                    logger.warning(f"Authentication failed for {email_or_username}", extra={'trace_id': ctx.trace_id})
                
                return user
            except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"Authentication error: {e}\n{error_details}", extra={'trace_id': ctx.trace_id})
                return None
            finally:
                if conn:
                    conn.close()
                    logger.debug("Database connection closed", extra={'trace_id': ctx.trace_id})
    
    def register_user(self, name, email, password, role):
        """Register a new user"""
        with TraceContext("register_user") as ctx:
            conn = None
            try:
                logger.info(f"Registering new user: {name}, {email}, role={role}", extra={'trace_id': ctx.trace_id})
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Hash the password
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                logger.debug("Password hashed for storage", extra={'trace_id': ctx.trace_id})
                
                # Insert new user
                query = """
                    INSERT INTO users (name, email, password, role)
                    VALUES (%s, %s, %s, %s)
                """
                logger.debug(f"Executing insert query", extra={'trace_id': ctx.trace_id})
                cursor.execute(query, (name, email, hashed_password, role))
                
                # Get the new user's ID
                user_id = cursor.lastrowid
                logger.debug(f"New user ID: {user_id}", extra={'trace_id': ctx.trace_id})
                
                # Commit transaction
                conn.commit()
                logger.info(f"User registered successfully with ID {user_id}", extra={'trace_id': ctx.trace_id})
                
                return {
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'role': role
                }
            except mysql.connector.Error as e:
                if conn:
                    conn.rollback()
                    logger.debug("Transaction rolled back", extra={'trace_id': ctx.trace_id})
                
                error_details = traceback.format_exc()
                if e.errno == 1062:  # Duplicate entry error
                    logger.error(f"User with this email already exists: {email}", extra={'trace_id': ctx.trace_id})
                    raise ValueError("User with this email already exists")
                else:
                    logger.error(f"Registration error: {e}\n{error_details}", extra={'trace_id': ctx.trace_id})
                    raise
            finally:
                if conn:
                    conn.close()
                    logger.debug("Database connection closed", extra={'trace_id': ctx.trace_id})
    
    def create_license_allocation(self, user_id, software_id='SW013', duration_months=6):
        """Create a license allocation for the user"""
        with TraceContext("create_license_allocation") as ctx:
            conn = None
            try:
                logger.info(f"Creating license allocation for user {user_id}, software {software_id}, duration={duration_months} months", 
                           extra={'trace_id': ctx.trace_id})
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Generate a unique allocation ID
                allocation_id = f"LA{int(time.time())}"[-10:]  # Ensure it fits VARCHAR(10)
                logger.debug(f"Generated allocation ID: {allocation_id}", extra={'trace_id': ctx.trace_id})
                
                # Calculate expiry date
                expiry_date = (datetime.now() + timedelta(days=30*duration_months)).strftime('%Y-%m-%d %H:%M:%S')
                logger.debug(f"Expiry date set to: {expiry_date}", extra={'trace_id': ctx.trace_id})
                
                # Insert allocation
                query = """
                    INSERT INTO license_allocations 
                    (allocation_id, software_id, user_id, allocation_date, expiry_date, is_active)
                    VALUES (%s, %s, %s, NOW(), %s, TRUE)
                """
                logger.debug(f"Executing insert query", extra={'trace_id': ctx.trace_id})
                cursor.execute(query, (allocation_id, software_id, user_id, expiry_date))
                
                # Commit transaction
                conn.commit()
                logger.info(f"License allocation created successfully: {allocation_id}", extra={'trace_id': ctx.trace_id})
                
                return {
                    'allocation_id': allocation_id,
                    'expiry_date': expiry_date
                }
            except Exception as e:
                if conn:
                    conn.rollback()
                    logger.debug("Transaction rolled back", extra={'trace_id': ctx.trace_id})
                
                error_details = traceback.format_exc()
                logger.error(f"License allocation error: {e}\n{error_details}", extra={'trace_id': ctx.trace_id})
                raise
            finally:
                if conn:
                    conn.close()
                    logger.debug("Database connection closed", extra={'trace_id': ctx.trace_id})
    
    def has_license_allocation(self, user_id, software_id='SW013'):
        """Check if user has a valid license allocation"""
        with TraceContext("has_license_allocation") as ctx:
            conn = None
            try:
                logger.debug(f"Checking license allocation for user {user_id}, software {software_id}", 
                           extra={'trace_id': ctx.trace_id})
                conn = self.get_connection()
                cursor = conn.cursor(dictionary=True)
                
                query = """
                    SELECT * FROM license_allocations 
                    WHERE user_id = %s AND software_id = %s AND is_active = TRUE
                    AND (expiry_date IS NULL OR expiry_date > NOW())
                """
                logger.debug("Executing query", extra={'trace_id': ctx.trace_id})
                cursor.execute(query, (user_id, software_id))
                
                allocation = cursor.fetchone()
                result = allocation is not None
                
                if result:
                    logger.info(f"User {user_id} has valid license allocation: {allocation['allocation_id']}", 
                               extra={'trace_id': ctx.trace_id})
                else:
                    logger.info(f"User {user_id} does not have valid license allocation", 
                               extra={'trace_id': ctx.trace_id})
                
                return result
            except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"License check error: {e}\n{error_details}", extra={'trace_id': ctx.trace_id})
                return False
            finally:
                if conn:
                    conn.close()
                    logger.debug("Database connection closed", extra={'trace_id': ctx.trace_id})

class LoginDialog(tk.Toplevel):
    """Dialog for user login"""
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        with TraceContext("LoginDialog.init") as ctx:
            self.parent = parent
            self.db_manager = db_manager
            self.authenticated = False
            self.user_info = None
            self.trace_id = ctx.trace_id
            
            logger.debug("Setting up login dialog UI", extra={'trace_id': ctx.trace_id})
            self.title("SmolCATLAB - Login")
            self.geometry("350x180")
            self.resizable(False, False)
            
            # Make dialog modal
            self.transient(parent)
            self.grab_set()
            
            # Create widgets
            frame = ttk.Frame(self, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Email or Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.username_var = tk.StringVar()
            ttk.Entry(frame, textvariable=self.username_var, width=30).grid(row=0, column=1, pady=5)
            
            ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.password_var = tk.StringVar()
            ttk.Entry(frame, textvariable=self.password_var, show="*", width=30).grid(row=1, column=1, pady=5)
            
            # Quick login for testing
            self.quick_login_frame = ttk.Frame(frame)
            self.quick_login_frame.grid(row=2, column=0, columnspan=2, pady=5)
            
            ttk.Button(self.quick_login_frame, text="Admin Login", 
                      command=lambda: self.quick_login("ajay.verma@gmail.com", "123456")).pack(side=tk.LEFT, padx=5)
            ttk.Button(self.quick_login_frame, text="Staff Login", 
                      command=lambda: self.quick_login("meera.nair@gmail.com", "123456")).pack(side=tk.LEFT, padx=5)
            
            # Regular buttons
            button_frame = ttk.Frame(frame)
            button_frame.grid(row=3, column=0, columnspan=2, pady=10)
            
            ttk.Button(button_frame, text="Login", command=self.login).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Register", command=self.open_register).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Exit", command=self.exit_app).pack(side=tk.LEFT, padx=5)
            
            # Bind Return key to login
            self.bind("<Return>", lambda event: self.login())
            
            # Center dialog on parent
            self.update_idletasks()
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")
            
            # Set focus to username field
            logger.debug("Setting default test credentials", extra={'trace_id': ctx.trace_id})
            self.username_var.set("yash.kokane@iitgn.ac.in")  # Default for testing
            self.password_var.set("20110237")  # Default for testing
            logger.debug("Login dialog initialized", extra={'trace_id': ctx.trace_id})
    
    def quick_login(self, username, password):
        """Quick login with predefined credentials"""
        with TraceContext("quick_login") as ctx:
            logger.debug(f"Quick login selected for {username}", extra={'trace_id': ctx.trace_id})
            self.username_var.set(username)
            self.password_var.set(password)
            self.login()
    
    def login(self):
        """Validate credentials and login"""
        with TraceContext("login") as ctx:
            username = self.username_var.get()
            password = self.password_var.get()
            
            logger.debug(f"Login attempt for user: {username}", extra={'trace_id': ctx.trace_id})
            
            if not username or not password:
                logger.warning("Login form incomplete", extra={'trace_id': ctx.trace_id})
                messagebox.showerror("Login Error", "Please enter both username and password")
                return
            
            try:
                logger.debug("Calling authentication method", extra={'trace_id': ctx.trace_id})
                user = self.db_manager.authenticate_user(username, password)
                
                if user:
                    logger.info(f"User authenticated: {user['name']}, {user['email']}, role={user['role']}",
                               extra={'trace_id': ctx.trace_id})
                    self.authenticated = True
                    self.user_info = user
                    
                    # Check if user has license allocation
                    logger.debug("Checking for license allocation", extra={'trace_id': ctx.trace_id})
                    has_allocation = self.db_manager.has_license_allocation(user['id'])
                    
                    if not has_allocation:
                        logger.info(f"User {user['id']} does not have license allocation", 
                                   extra={'trace_id': ctx.trace_id})
                        # Ask if user wants to create an allocation
                        if messagebox.askyesno("License Required", 
                                             "You don't have a license allocation yet. Create one now?"):
                            try:
                                logger.debug("Creating license allocation", extra={'trace_id': ctx.trace_id})
                                allocation = self.db_manager.create_license_allocation(user['id'])
                                logger.info(f"Allocation created: {allocation['allocation_id']}", 
                                          extra={'trace_id': ctx.trace_id})
                                messagebox.showinfo("License Created", 
                                                  f"License allocation created. Valid until {allocation['expiry_date']}")
                            except Exception as e:
                                error_details = traceback.format_exc()
                                logger.error(f"Failed to create allocation: {e}\n{error_details}", 
                                           extra={'trace_id': ctx.trace_id})
                                messagebox.showerror("Allocation Error", f"Failed to create license: {e}")
                                # Continue anyway, user can try again from main window
                    
                    logger.debug("Destroying login dialog", extra={'trace_id': ctx.trace_id})
                    self.destroy()
                else:
                    logger.warning(f"Authentication failed for {username}", extra={'trace_id': ctx.trace_id})
                    messagebox.showerror("Login Failed", "Invalid username or password")
            except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"Login error: {e}\n{error_details}", extra={'trace_id': ctx.trace_id})
                messagebox.showerror("Login Error", f"An error occurred: {e}")
    
    def open_register(self):
        """Open registration dialog"""
        with TraceContext("open_register") as ctx:
            logger.debug("Opening registration dialog", extra={'trace_id': ctx.trace_id})
            self.withdraw()  # Hide login dialog temporarily
            register_dialog = RegisterDialog(self.parent, self.db_manager)
            
            # If registration was successful, use those credentials
            if register_dialog.registered and register_dialog.user_info:
                logger.info(f"Using credentials from successful registration", extra={'trace_id': ctx.trace_id})
                self.authenticated = True
                self.user_info = register_dialog.user_info
                self.destroy()
            else:
                logger.debug("Registration not completed, showing login dialog again", 
                           extra={'trace_id': ctx.trace_id})
                self.deiconify()  # Show login dialog again
    
    def exit_app(self):
        """Exit the application"""
        with TraceContext("exit_app") as ctx:
            logger.info("User requested application exit from login dialog", extra={'trace_id': ctx.trace_id})
            self.authenticated = False
            self.parent.destroy()

class RegisterDialog(tk.Toplevel):
    """Dialog for user registration"""
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager
        self.registered = False
        self.user_info = None
        
        self.title("SmolCATLAB - Register")
        self.geometry("400x260")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create widgets
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Full Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.email_var, width=30).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.password_var, show="*", width=30).grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Confirm Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.confirm_password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.confirm_password_var, show="*", width=30).grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="Role:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.role_var = tk.StringVar(value="Visitor")
        role_combo = ttk.Combobox(frame, textvariable=self.role_var, 
                                 values=["Visitor", "Staff", "Admin"], width=15)
        role_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        role_combo.current(0)
        
        # License allocation options
        license_frame = ttk.LabelFrame(frame, text="License Options", padding=5)
        license_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        ttk.Label(license_frame, text="Duration:").grid(row=0, column=0, sticky=tk.W)
        self.duration_var = tk.StringVar(value="6")
        ttk.Combobox(license_frame, textvariable=self.duration_var, 
                    values=["1", "3", "6", "12"], width=5).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(license_frame, text="months").grid(row=0, column=2, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Register", command=self.register).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        # Center dialog on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Set focus to name field
        self.name_var.set("Test User")  # Default for testing
        self.email_var.set("test.user@example.com")  # Default for testing
    
    def register(self):
        """Register a new user"""
        name = self.name_var.get()
        email = self.email_var.get()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        role = self.role_var.get()
        duration = int(self.duration_var.get())
        
        # Validate inputs
        if not name or not email or not password or not confirm_password:
            messagebox.showerror("Registration Error", "All fields are required")
            return
        
        if password != confirm_password:
            messagebox.showerror("Registration Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            messagebox.showerror("Registration Error", "Password must be at least 6 characters")
            return
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Registration Error", "Invalid email format")
            return
        
        try:
            # Register user
            user = self.db_manager.register_user(name, email, password, role)
            
            if user:
                # Create license allocation
                try:
                    allocation = self.db_manager.create_license_allocation(
                        user['id'], 'SW013', duration)
                    
                    messagebox.showinfo("Registration Successful", 
                                      f"User registered successfully!\nLicense valid until {allocation['expiry_date']}")
                    
                    self.registered = True
                    self.user_info = user
                    self.destroy()
                except Exception as e:
                    logger.error(f"License allocation error during registration: {e}")
                    messagebox.showwarning("License Warning", 
                                        f"User registered but license allocation failed: {e}")
                    # Still consider registration successful
                    self.registered = True
                    self.user_info = user
                    self.destroy()
            else:
                messagebox.showerror("Registration Failed", "Failed to register user")
        except ValueError as e:
            messagebox.showerror("Registration Error", str(e))
        except Exception as e:
            logger.error(f"Registration error: {e}")
            messagebox.showerror("Registration Error", f"An error occurred: {e}")

class SmolCatlabApp:
    def __init__(self, root, user_info):
        logger.debug("SmolCatlabApp.__init__: Starting")
        self.root = root
        self.user_info = user_info
        self.root.title(f"SmolCATLAB - {user_info['name']} ({user_info['role']})")
        self.root.geometry("500x300")
        self.root.minsize(500, 250)

        self.license_client = None
        self.has_license = False
        self.db_manager = DatabaseManager()

        # Create UI
        self.create_widgets()

        # Initialize License Client
        logger.debug("SmolCatlabApp.__init__: Initializing LicenseClient")
        try:
            self.license_client = LicenseClient(
                SERVER_IP,
                SERVER_PORT,
                SOFTWARE_ID,
                self.user_info['id']
            )
            self.status_label.config(text="Status: Ready. Client initialized.")
            logger.debug("SmolCatlabApp.__init__: LicenseClient initialized successfully")
        except Exception as e:
            logger.error(f"SmolCatlabApp.__init__: Failed to initialize LicenseClient: {e}", exc_info=True)
            self.status_label.config(text=f"Status: Error initializing client: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize License Client:\n{e}")
            self.root.destroy() # Exit if client fails
            return

        # Attempt initial checkout if user has allocation
        if self.db_manager.has_license_allocation(self.user_info['id']):
            self.root.after(100, self.checkout_license) # Use 'after' to allow UI to draw first
        else:
            self.status_label.config(text="Status: No license allocation found. Use 'Register License' to create one.")

        # Set up close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        logger.debug("SmolCatlabApp.__init__: Finished")

    def create_widgets(self):
        """Create application widgets"""
        # Menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # License menu
        license_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="License", menu=license_menu)
        license_menu.add_command(label="Check Out License", command=self.checkout_license)
        license_menu.add_command(label="Check In License", command=self.checkin_license)
        license_menu.add_command(label="Register License", command=self.register_license)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # User info frame
        user_frame = ttk.LabelFrame(main_frame, text="User Information", padding=10)
        user_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(user_frame, text=f"Name: {self.user_info['name']}").pack(anchor=tk.W)
        ttk.Label(user_frame, text=f"Email: {self.user_info['email']}").pack(anchor=tk.W)
        ttk.Label(user_frame, text=f"Role: {self.user_info['role']}").pack(anchor=tk.W)
        ttk.Label(user_frame, text=f"User ID: {self.user_info['id']}").pack(anchor=tk.W)
        
        # License status frame
        license_frame = ttk.LabelFrame(main_frame, text="License Status", padding=10)
        license_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_label = ttk.Label(license_frame, text="Status: Initializing...", anchor=tk.W, justify=tk.LEFT)
        self.status_label.pack(fill=tk.X, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.checkout_button = ttk.Button(button_frame, text="Check Out License", command=self.checkout_license)
        self.checkout_button.pack(side=tk.LEFT, padx=5)
        
        self.checkin_button = ttk.Button(button_frame, text="Check In License", command=self.checkin_license, state=tk.DISABLED)
        self.checkin_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Register License", command=self.register_license).pack(side=tk.LEFT, padx=5)

    def checkout_license(self):
        if self.has_license:
            logger.info("Checkout requested, but already have a license.")
            messagebox.showinfo("License Status", "License is already checked out.")
            return

        if not self.license_client:
            logger.error("Checkout failed: License client not initialized.")
            messagebox.showerror("Error", "License client not initialized.")
            return

        logger.info(f"Attempting license checkout for user {self.user_info['id']}...")
        self.status_label.config(text=f"Status: Checking out license for user {self.user_info['id']}...")
        self.root.update_idletasks() # Update UI immediately

        try:
            response = self.license_client.checkout_license()
            logger.debug(f"Checkout response: {response}")

            if response and response.get('status') == 'success':
                self.has_license = True
                session_id = response.get('session_id', 'N/A')
                expiry = response.get('expiry', 'N/A')
                self.status_label.config(text=f"Status: License CHECKED OUT.\nSession: {session_id}\nExpiry: {expiry}")
                self.checkout_button.config(state=tk.DISABLED)
                self.checkin_button.config(state=tk.NORMAL)
                logger.info(f"License checked out successfully. Session: {session_id}")
                # Heartbeat thread is started automatically by LicenseClient
            else:
                error_msg = response.get('message', 'Unknown error')
                self.status_label.config(text=f"Status: Checkout FAILED.\nReason: {error_msg}")
                logger.error(f"License checkout failed: {error_msg}")
                
                if "no allocation" in error_msg.lower() or "register" in error_msg.lower():
                    if messagebox.askyesno("License Required", 
                                         "You don't have a license allocation. Create one now?"):
                        self.register_license()
                else:
                    messagebox.showerror("Checkout Failed", f"Could not check out license:\n{error_msg}")

        except Exception as e:
            logger.error(f"Exception during checkout: {e}", exc_info=True)
            self.status_label.config(text=f"Status: Checkout ERROR.\nReason: {e}")
            messagebox.showerror("Checkout Error", f"An unexpected error occurred:\n{e}")

    def checkin_license(self):
        if not self.has_license:
            logger.info("Checkin requested, but no license is held.")
            return

        if not self.license_client:
            logger.error("Checkin failed: License client not initialized.")
            messagebox.showerror("Error", "License client not initialized.")
            return

        logger.info(f"Attempting license check-in for session {self.license_client.session_id}...")
        self.status_label.config(text="Status: Checking in license...")
        self.root.update_idletasks()

        try:
            # Stop the heartbeat thread before sending checkin
            if self.license_client.heartbeat_thread and self.license_client.heartbeat_thread.is_alive():
                 logger.debug("Setting is_running to False for heartbeat thread.")
                 self.license_client.is_running = False

            response = self.license_client.checkin_license()
            logger.debug(f"Checkin response: {response}")

            if response and response.get('status') == 'success':
                self.has_license = False
                self.status_label.config(text="Status: License CHECKED IN.")
                self.checkout_button.config(state=tk.NORMAL)
                self.checkin_button.config(state=tk.DISABLED)
                logger.info("License checked in successfully.")
            else:
                # Even if checkin fails, treat locally as checked in to allow retry/exit
                self.has_license = False
                error_msg = response.get('message', 'Unknown error')
                self.status_label.config(text=f"Status: Check-in FAILED (Client state reset).\nReason: {error_msg}")
                self.checkout_button.config(state=tk.NORMAL)
                self.checkin_button.config(state=tk.DISABLED)
                logger.error(f"License check-in failed: {error_msg}")
                messagebox.showwarning("Check-in Warning", f"Failed to confirm check-in with server:\n{error_msg}\n\nLicense state reset locally.")

        except Exception as e:
            logger.error(f"Exception during checkin: {e}", exc_info=True)
            # Reset state locally even on exception
            self.has_license = False
            self.checkout_button.config(state=tk.NORMAL)
            self.checkin_button.config(state=tk.DISABLED)
            self.status_label.config(text=f"Status: Check-in ERROR (Client state reset).\nReason: {e}")
            messagebox.showerror("Check-in Error", f"An unexpected error occurred during check-in:\n{e}\n\nLicense state reset locally.")

    def register_license(self):
        """Register a license allocation for the current user"""
        if self.db_manager.has_license_allocation(self.user_info['id']):
            if messagebox.askyesno("License Exists", 
                                 "You already have a license allocation. Create a new one?"):
                pass  # Continue with registration
            else:
                return  # User cancelled
        
        # Ask for duration
        duration_dialog = tk.Toplevel(self.root)
        duration_dialog.title("License Duration")
        duration_dialog.geometry("300x100")
        duration_dialog.transient(self.root)
        duration_dialog.grab_set()
        
        ttk.Label(duration_dialog, text="Select license duration:").pack(pady=5)
        
        duration_var = tk.StringVar(value="6")
        duration_frame = ttk.Frame(duration_dialog)
        duration_frame.pack(pady=5)
        
        ttk.Label(duration_frame, text="Duration:").grid(row=0, column=0, padx=5)
        ttk.Combobox(duration_frame, textvariable=duration_var, 
                    values=["1", "3", "6", "12"], width=5).grid(row=0, column=1, padx=5)
        ttk.Label(duration_frame, text="months").grid(row=0, column=2, padx=5)
        
        # Function to handle registration
        def do_register():
            try:
                duration = int(duration_var.get())
                allocation = self.db_manager.create_license_allocation(
                    self.user_info['id'], 'SW013', duration)
                
                messagebox.showinfo("License Created", 
                                  f"License allocation created successfully!\nValid until {allocation['expiry_date']}")
                
                duration_dialog.destroy()
                
                # Update status and enable checkout
                self.status_label.config(text=f"Status: License allocation created. Valid until {allocation['expiry_date']}")
                self.checkout_button.config(state=tk.NORMAL)
                
            except Exception as e:
                logger.error(f"License registration error: {e}")
                messagebox.showerror("Registration Error", f"Failed to create license: {e}")
                duration_dialog.destroy()
        
        ttk.Button(duration_dialog, text="Register", command=do_register).pack(pady=5)
        
        # Center dialog on parent
        duration_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (duration_dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (duration_dialog.winfo_height() // 2)
        duration_dialog.geometry(f"+{x}+{y}")

    def on_closing(self):
        logger.debug("on_closing called.")
        if self.has_license:
            logger.info("Checking in license before closing...")
            self.checkin_license()
            # Give checkin a moment, might need adjustment
            self.root.update_idletasks()
            time.sleep(0.5)
        else:
             logger.info("No active license to check in.")

        # Ensure heartbeat thread is stopped if still running somehow
        if self.license_client and self.license_client.heartbeat_thread and self.license_client.heartbeat_thread.is_alive():
            logger.warning("Force stopping heartbeat thread on close.")
            self.license_client.is_running = False

        logger.info("Destroying root window.")
        self.root.destroy()

def main():
    with TraceContext("main") as ctx:
        logger.debug("Starting SmolCatlab", extra={'trace_id': ctx.trace_id})
        root = tk.Tk()
        root.withdraw()  # Hide the root window initially
        logger.debug("Root window created and hidden", extra={'trace_id': ctx.trace_id})
        
        try:
            # Create database manager
            logger.debug("Creating DatabaseManager instance", extra={'trace_id': ctx.trace_id})
            db_manager = DatabaseManager()
            
            # Show login dialog
            logger.debug("Creating LoginDialog", extra={'trace_id': ctx.trace_id})
            login_dialog = LoginDialog(root, db_manager)
            
            # Check if login was successful
            if not login_dialog.authenticated:
                logger.info("Login cancelled or failed. Exiting.", extra={'trace_id': ctx.trace_id})
                root.destroy()
                return
            
            # Login successful, get user info
            user_info = login_dialog.user_info
            logger.info(f"User authenticated: {user_info['name']} (ID: {user_info['id']})", 
                       extra={'trace_id': ctx.trace_id})
            
            # Show the main window
            logger.debug("Showing main window", extra={'trace_id': ctx.trace_id})
            root.deiconify()  # Show the root window
            
            # Create the main application
            logger.debug("Creating SmolCatlabApp instance", extra={'trace_id': ctx.trace_id})
            app = SmolCatlabApp(root, user_info)
            
            # Start the mainloop
            logger.debug("Starting mainloop", extra={'trace_id': ctx.trace_id})
            root.mainloop()
            logger.debug("Mainloop finished", extra={'trace_id': ctx.trace_id})
        
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Unhandled exception in main: {e}\n{error_details}", extra={'trace_id': ctx.trace_id})
            messagebox.showerror("Critical Error", f"An unexpected error occurred:\n{e}")
            root.destroy()

if __name__ == "__main__":
    logger.info("--- Starting SmolCATLAB ---", extra={'trace_id': 'STARTUP'})
    main()
    logger.info("--- SmolCATLAB Exited ---", extra={'trace_id': 'SHUTDOWN'})
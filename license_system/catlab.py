#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
import time
import threading
import json
import configparser
import logging
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mysql.connector

# Add parent directory to path so we can import license_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from license_system.license_client import LicenseClient

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('catlab')

# Default configuration
DEFAULT_CONFIG = {
    'license_server': {
        'ip': 'localhost',
        'port': '27000',
        'software_id': 'SW013',  # CATLAB software_id from database
    },
    'user': {
        'id': '4'  # Default user ID
    },
    'email': {
        'server': 'smtp.gmail.com',
        'port': '587',
        'username': 'catlab.licensing@gmail.com',
        'password': 'your_app_password_here'  # Use an app password, not regular password
    }
}

class EmailVerifier:
    """Class to handle email verification"""
    def __init__(self, config):
        self.config = config
        self.verification_code = None
        self.debug_mode = False
    
    def set_debug_mode(self, is_debug):
        """Set debug mode based on user login"""
        self.debug_mode = is_debug
    
    def generate_verification_code(self):
        """Generate a random 6-digit verification code"""
        if self.debug_mode:
            self.verification_code = "123456"  # Fixed code in debug mode
            logger.info(f"DEBUG MODE: Using verification code: {self.verification_code}")
            return self.verification_code
        
        self.verification_code = ''.join(random.choices(string.digits, k=6))
        return self.verification_code
    
    def send_verification_email(self, recipient_email, user_name):
        """Send verification email with code"""
        if self.debug_mode:
            # In debug mode, just generate the code without sending email
            code = self.generate_verification_code()
            logger.info(f"DEBUG MODE: Would send verification code {code} to {recipient_email}")
            messagebox.showinfo("DEBUG MODE", 
                               f"Verification code: {code}\n\nIn production, this would be emailed to {recipient_email}")
            return True
        
        try:
            # Setup email server
            server = smtplib.SMTP(self.config['email']['server'], int(self.config['email']['port']))
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = recipient_email
            msg['Subject'] = "CATLAB License Verification"
            
            # Email body
            code = self.generate_verification_code()
            body = f"""
            <html>
              <body>
                <h2>CATLAB License Verification</h2>
                <p>Hello {user_name},</p>
                <p>Thank you for registering for CATLAB software. To verify your email and activate your license, 
                please enter the following verification code in the application:</p>
                <h3 style="background-color: #f0f0f0; padding: 10px; text-align: center; font-size: 24px;">{code}</h3>
                <p>This code will expire in 30 minutes.</p>
                <p>If you did not request this verification, please ignore this email.</p>
                <p>Best regards,<br>
                CATLAB Licensing Team</p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Verification email sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            return False

class LicenseRegistrationDialog(tk.Toplevel):
    """Dialog for registering for a license"""
    def __init__(self, parent, user_info, db_config, email_verifier):
        super().__init__(parent)
        self.parent = parent
        self.user_info = user_info  # User info from login
        self.db_config = db_config
        self.email_verifier = email_verifier
        self.registration_complete = False
        
        self.title("CATLAB - License Registration")
        self.geometry("450x350")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        # Wait for window to be closed
        self.wait_window()
    
    def create_widgets(self):
        # Registration info frame
        info_frame = tk.LabelFrame(self, text="License Registration", padx=10, pady=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # User info display
        tk.Label(info_frame, text=f"Name: {self.user_info['name']}").grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        tk.Label(info_frame, text=f"Email: {self.user_info['email']}").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        tk.Label(info_frame, text=f"Role: {self.user_info['role']}").grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # License duration selection
        tk.Label(info_frame, text="License Duration:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.duration_var = tk.StringVar(value="6")
        duration_combo = ttk.Combobox(info_frame, textvariable=self.duration_var, 
                                     values=["1", "3", "6", "12"], width=10)
        duration_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        tk.Label(info_frame, text="months").grid(row=3, column=2, sticky=tk.W, padx=0, pady=5)
        
        # Purpose of use
        tk.Label(info_frame, text="Purpose of Use:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.purpose_var = tk.StringVar()
        purpose_entry = tk.Entry(info_frame, textvariable=self.purpose_var, width=40)
        purpose_entry.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Terms and conditions
        self.agree_var = tk.BooleanVar(value=False)
        agree_check = tk.Checkbutton(info_frame, text="I agree to the license terms and conditions", 
                                     variable=self.agree_var)
        agree_check.grid(row=5, column=0, columnspan=3, sticky=tk.W, padx=5, pady=10)
        
        # Register button
        self.register_btn = tk.Button(info_frame, text="Register & Send Verification Code", 
                                     command=self.register_license)
        self.register_btn.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Verification frame (initially hidden)
        self.verify_frame = tk.LabelFrame(self, text="Email Verification", padx=10, pady=10)
        
        # Verification code entry
        tk.Label(self.verify_frame, text="Enter the verification code sent to your email:").pack(anchor=tk.W, padx=5, pady=5)
        self.code_var = tk.StringVar()
        code_entry = tk.Entry(self.verify_frame, textvariable=self.code_var, width=10, font=('Arial', 14))
        code_entry.pack(anchor=tk.W, padx=5, pady=5)
        
        # Verify button
        verify_btn = tk.Button(self.verify_frame, text="Verify Code", command=self.verify_code)
        verify_btn.pack(anchor=tk.W, padx=5, pady=10)
        
        # Resend code link
        resend_link = tk.Label(self.verify_frame, text="Resend code", fg="blue", cursor="hand2")
        resend_link.pack(anchor=tk.W, padx=5)
        resend_link.bind("<Button-1>", lambda e: self.send_verification_email())
    
    def register_license(self):
        """Register the license and send verification email"""
        if not self.agree_var.get():
            messagebox.showerror("Registration Error", "You must agree to the terms and conditions")
            return
        
        if not self.purpose_var.get():
            messagebox.showerror("Registration Error", "Please enter the purpose of use")
            return
        
        try:
            # Disable register button during processing
            self.register_btn.config(state=tk.DISABLED)
            
            # Send verification email
            if self.send_verification_email():
                # Show verification frame
                self.verify_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            else:
                self.register_btn.config(state=tk.NORMAL)
        except Exception as e:
            logger.error(f"Error during license registration: {e}")
            messagebox.showerror("Registration Error", f"An error occurred: {str(e)}")
            self.register_btn.config(state=tk.NORMAL)
    
    def send_verification_email(self):
        """Send verification email to the user"""
        success = self.email_verifier.send_verification_email(
            self.user_info['email'], 
            self.user_info['name']
        )
        
        if success:
            messagebox.showinfo("Verification Email", 
                               f"A verification code has been sent to {self.user_info['email']}.\n"
                               "Please check your inbox and enter the code below.")
            return True
        else:
            messagebox.showerror("Email Error", 
                                "Failed to send verification email. Please try again later.")
            return False
    
    def verify_code(self):
        """Verify the code entered by the user"""
        entered_code = self.code_var.get().strip()
        
        if not entered_code:
            messagebox.showerror("Verification Error", "Please enter the verification code")
            return
        
        if entered_code == self.email_verifier.verification_code:
            # Code is valid, complete registration
            if self.complete_registration():
                self.registration_complete = True
                messagebox.showinfo("Registration Complete", 
                                   "Your license has been activated successfully!")
                self.destroy()
            else:
                messagebox.showerror("Registration Error", 
                                    "Failed to complete registration. Please try again.")
        else:
            messagebox.showerror("Verification Error", 
                                "Invalid verification code. Please try again.")
    
    def complete_registration(self):
        """Complete the license registration in the database"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Calculate expiry date based on selected duration
            duration_months = int(self.duration_var.get())
            
            # Create an allocation for the user
            allocation_id = f"LA{str(int(time.time()))[-8:]}"
            
            cursor.execute("""
                INSERT INTO License_Allocations 
                (allocation_id, software_id, user_id, allocation_date, expiry_date, is_active)
                VALUES (%s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL %s MONTH), TRUE)
            """, (allocation_id, "SW013", self.user_info['id'], duration_months))
            
            conn.commit()
            logger.info(f"License allocation created: {allocation_id} for user {self.user_info['id']}")
            
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error completing registration: {e}")
            return False


class LoginDialog(tk.Toplevel):
    """Dialog for user login"""
    def __init__(self, parent, db_config):
        logger.debug("LoginDialog.__init__: Starting")
        super().__init__(parent)
        logger.debug("LoginDialog.__init__: super().__init__ completed")
        self.parent = parent
        self.db_config = db_config
        self.title("CATLAB - Login")
        self.geometry("350x200")
        self.resizable(False, False)
        self.authenticated = False
        self.user_info = None
        self.is_debug_user = False

        # Center the dialog
        logger.debug("LoginDialog.__init__: Setting transient")
        self.transient(parent)
        logger.debug("LoginDialog.__init__: Setting grab")
        self.grab_set()
        logger.debug("LoginDialog.__init__: Creating widgets")

        # Username field
        tk.Label(self, text="Email:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.email_var = tk.StringVar()
        email_entry = tk.Entry(self, textvariable=self.email_var, width=30)
        email_entry.grid(row=0, column=1, padx=10, pady=10)

        # Password field
        tk.Label(self, text="Password:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(self, textvariable=self.password_var, show="*", width=30)
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="Login", command=self.login).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Exit", command=self.exit_app).pack(side=tk.LEFT, padx=10)

        # Set focus to email field
        email_entry.focus_set()
        logger.debug("LoginDialog.__init__: Widgets created")

        # Wait for window to be closed
        logger.debug("LoginDialog.__init__: Calling wait_window()")
        self.wait_window()
        logger.debug("LoginDialog.__init__: wait_window() finished")
    
    def login(self):
        """Validate login credentials against database"""
        email = self.email_var.get()
        password = self.password_var.get()
        
        if not email or not password:
            messagebox.showerror("Login Error", "Email and password are required")
            return
        
        # Check if using debug account
        self.is_debug_user = (email.lower() == "ajay.verma@gmail.com" and password == "123456")
        
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT id, name, email, role FROM Users 
                WHERE email = %s AND password = %s
            """, (email, password))
            
            user = cursor.fetchone()
            
            if user:
                self.authenticated = True
                self.user_info = user
                
                if self.is_debug_user:
                    messagebox.showinfo("DEBUG MODE", "Logged in as debug user. Email verification will be bypassed.")
                
                # Check if the user already has a license allocation
                cursor.execute("""
                    SELECT * FROM License_Allocations 
                    WHERE user_id = %s AND software_id = 'SW013' AND is_active = TRUE
                    AND expiry_date > NOW()
                """, (user['id'],))
                
                allocation = cursor.fetchone()
                
                if allocation:
                    # User already has an active license
                    logger.info(f"User {user['id']} has an active license allocation")
                    self.destroy()
                else:
                    # User needs to register for a license
                    self.destroy()
                    
                    # Create email verifier
                    config = configparser.ConfigParser()
                    for section, items in DEFAULT_CONFIG.items():
                        if not config.has_section(section):
                            config.add_section(section)
                        for key, value in items.items():
                            config.set(section, key, value)
                    
                    email_verifier = EmailVerifier(config)
                    # Set debug mode based on user
                    email_verifier.set_debug_mode(self.is_debug_user)
                    
                    # Show license registration dialog
                    reg_dialog = LicenseRegistrationDialog(self.parent, user, self.db_config, email_verifier)
                    
                    if not reg_dialog.registration_complete:
                        # User didn't complete registration
                        self.authenticated = False
                        messagebox.showinfo("License Required", 
                                          "You need to complete license registration to use CATLAB.")
                        self.parent.destroy()
            else:
                messagebox.showerror("Login Error", "Invalid email or password")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {str(e)}")
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
    
    def exit_app(self):
        """Exit the application"""
        self.parent.destroy()


class CatlabApp:
    def __init__(self, root):
        logger.debug("CatlabApp.__init__: Starting")
        self.root = root
        self.root.title("CATLAB - Chemical Analysis Tool")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        # Hide the main window initially
        logger.debug("CatlabApp.__init__: Withdrawing root window")
        self.root.withdraw() # <<< Hides the main window
        logger.debug("CatlabApp.__init__: Root window withdrawn")

        # Get database config
        logger.debug("CatlabApp.__init__: Getting DB password")
        db_password = self.get_db_password() # <<< Reads password file
        logger.debug(f"CatlabApp.__init__: DB password {'obtained' if db_password else 'NOT obtained'}")
        self.db_config = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': db_password,
            'database': 'cifdb'
        }

        # Authenticate user first
        logger.debug("CatlabApp.__init__: Creating LoginDialog")
        login_dialog = LoginDialog(self.root, self.db_config) # <<< Creates and shows login dialog
        logger.debug(f"CatlabApp.__init__: LoginDialog closed, authenticated={login_dialog.authenticated}")

        if not login_dialog.authenticated:
            # User didn't log in successfully
            logger.warning("CatlabApp.__init__: Login failed or cancelled. Destroying root window.")
            self.root.destroy() # <<< Destroys root window if login fails/cancelled
            return

        # User authenticated, get the user info
        logger.debug("CatlabApp.__init__: User authenticated")
        self.user_info = login_dialog.user_info

        # Load configuration
        logger.debug("CatlabApp.__init__: Loading config")
        self.config = self.load_config()
        # Update user ID in config to match logged in user
        logger.debug("CatlabApp.__init__: Setting user ID in config")
        self.config.set('user', 'id', str(self.user_info['id']))

        # Show main window
        logger.debug("CatlabApp.__init__: Deiconifying root window")
        self.root.deiconify() # <<< Shows the main window again *after* login
        logger.debug("CatlabApp.__init__: Root window deiconified")

        # Initialize license client with authenticated user
        logger.debug("CatlabApp.__init__: Initializing LicenseClient")
        self.license_client = LicenseClient(
            self.config['license_server']['ip'],
            int(self.config['license_server']['port']),
            self.config['license_server']['software_id'],
            str(self.user_info['id'])  # Use the authenticated user ID
        )
        logger.debug("CatlabApp.__init__: LicenseClient initialized")

        # Create flag for license status
        self.has_license = False

        # Create widgets
        logger.debug("CatlabApp.__init__: Creating widgets")
        self.create_widgets()
        logger.debug("CatlabApp.__init__: Widgets created")

        # Try to check out license on startup
        logger.debug("CatlabApp.__init__: Attempting initial license checkout")
        self.checkout_license()
        logger.debug("CatlabApp.__init__: Initial license checkout attempted")

        # Set up a protocol for when the window is closed
        logger.debug("CatlabApp.__init__: Setting close protocol")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        logger.debug("CatlabApp.__init__: Finished")
    
    def get_db_password(self):
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

    def load_config(self):
        """Load configuration from file or use defaults"""
        config = configparser.ConfigParser()
        
        # Set defaults
        for section, items in DEFAULT_CONFIG.items():
            if not config.has_section(section):
                config.add_section(section)
            for key, value in items.items():
                config.set(section, key, value)
        
        # Try to load from file if it exists
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'catlab.ini')
        if os.path.exists(config_file):
            config.read(config_file)
        else:
            # Save default config
            with open(config_file, 'w') as f:
                config.write(f)
        
        return config

    def create_widgets(self):
        """Create the application widgets"""
        # Create a menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Create a file menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Create a license menu
        self.license_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="License", menu=self.license_menu)
        self.license_menu.add_command(label="Check Out License", command=self.checkout_license)
        self.license_menu.add_command(label="Check In License", command=self.checkin_license)
        self.license_menu.add_command(label="Query License", command=self.query_license)
        
        # Create a status bar
        self.status_bar = tk.Frame(self.root, height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.license_status = tk.Label(self.status_bar, text="License Status: Not Checked Out", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.license_status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create a tab control
        self.tab_control = ttk.Notebook(self.root)
        
        # Create tabs
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab1, text='Sample Analysis')
        self.tab_control.add(self.tab2, text='Data Visualization')
        self.tab_control.add(self.tab3, text='Reports')
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Add content to Sample Analysis tab
        self.create_sample_analysis_tab()
        
        # Add content to Data Visualization tab
        self.create_data_visualization_tab()
        
        # Add content to Reports tab
        self.create_reports_tab()

    def create_sample_analysis_tab(self):
        """Create content for the Sample Analysis tab"""
        # Sample list frame
        sample_frame = tk.LabelFrame(self.tab1, text="Sample List", padx=10, pady=10)
        sample_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a treeview to display sample list
        columns = ('id', 'name', 'type', 'date')
        self.sample_tree = ttk.Treeview(sample_frame, columns=columns, show='headings')
        
        # Define headings
        self.sample_tree.heading('id', text='ID')
        self.sample_tree.heading('name', text='Sample Name')
        self.sample_tree.heading('type', text='Type')
        self.sample_tree.heading('date', text='Collection Date')
        
        # Define column widths
        self.sample_tree.column('id', width=50)
        self.sample_tree.column('name', width=200)
        self.sample_tree.column('type', width=100)
        self.sample_tree.column('date', width=150)
        
        # Add sample data (mock data for demo)
        samples = [
            (1, 'Water Sample A', 'Liquid', '2023-05-01'),
            (2, 'Soil Sample B', 'Solid', '2023-05-02'),
            (3, 'Gas Sample C', 'Gas', '2023-05-03'),
            (4, 'Water Sample D', 'Liquid', '2023-05-04'),
            (5, 'Soil Sample E', 'Solid', '2023-05-05'),
        ]
        
        for sample in samples:
            self.sample_tree.insert('', tk.END, values=sample)
            
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(sample_frame, orient=tk.VERTICAL, command=self.sample_tree.yview)
        self.sample_tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.sample_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = tk.Frame(self.tab1)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add some buttons
        ttk.Button(button_frame, text="New Sample", command=self.new_sample_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Analyze Selected", command=self.analyze_sample_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_sample_action).pack(side=tk.LEFT, padx=5)

    def create_data_visualization_tab(self):
        """Create content for the Data Visualization tab"""
        # Placeholder for data visualization tab
        message_label = tk.Label(self.tab2, text="Data visualization features will be displayed here")
        message_label.pack(padx=20, pady=20)
        
        # Mock visualization frame
        viz_frame = tk.LabelFrame(self.tab2, text="Visualization Options", padx=10, pady=10)
        viz_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add some options
        ttk.Label(viz_frame, text="Chart Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        chart_type = ttk.Combobox(viz_frame, values=["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"])
        chart_type.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        chart_type.current(0)
        
        ttk.Label(viz_frame, text="Data Series:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        data_series = ttk.Combobox(viz_frame, values=["pH Levels", "Temperature", "Contaminant Concentration", "Particle Size"])
        data_series.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        data_series.current(0)
        
        ttk.Button(viz_frame, text="Generate Chart", command=self.generate_chart_action).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Placeholder for the chart
        chart_frame = tk.LabelFrame(self.tab2, text="Chart View", padx=10, pady=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        chart_label = tk.Label(chart_frame, text="Chart will be displayed here\n(Requires license to generate charts)")
        chart_label.pack(fill=tk.BOTH, expand=True)

    def create_reports_tab(self):
        """Create content for the Reports tab"""
        # Placeholder for reports tab
        message_label = tk.Label(self.tab3, text="Report generation features will be displayed here")
        message_label.pack(padx=20, pady=20)
        
        # Reports options frame
        reports_frame = tk.LabelFrame(self.tab3, text="Report Options", padx=10, pady=10)
        reports_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add some options
        ttk.Label(reports_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        report_type = ttk.Combobox(reports_frame, values=["Full Analysis", "Summary", "Compliance Report", "Custom"])
        report_type.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        report_type.current(0)
        
        ttk.Label(reports_frame, text="Format:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        report_format = ttk.Combobox(reports_frame, values=["PDF", "Word Document", "Excel Spreadsheet", "HTML"])
        report_format.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        report_format.current(0)
        
        ttk.Button(reports_frame, text="Generate Report", command=self.generate_report_action).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Report preview
        preview_frame = tk.LabelFrame(self.tab3, text="Report Preview", padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        preview_label = tk.Label(preview_frame, text="Report preview will be displayed here\n(Requires license to generate reports)")
        preview_label.pack(fill=tk.BOTH, expand=True)

    def checkout_license(self):
        """Check out a license from the server"""
        if self.has_license:
            messagebox.showinfo("License Status", "You already have a license checked out.")
            return
        
        response = self.license_client.checkout_license()
        
        if response.get('status') == 'success':
            self.has_license = True
            self.license_status.config(text=f"License Status: Active - Session: {self.license_client.session_id}")
            messagebox.showinfo("License Status", "License checked out successfully!")
        else:
            self.has_license = False
            self.license_status.config(text="License Status: Not Checked Out")
            messagebox.showerror("License Error", f"Failed to check out license: {response.get('message')}")

    def checkin_license(self):
        """Check in a license to the server"""
        if not self.has_license:
            messagebox.showinfo("License Status", "No license is currently checked out.")
            return
        
        response = self.license_client.checkin_license()
        
        if response.get('status') == 'success':
            self.has_license = False
            self.license_status.config(text="License Status: Not Checked Out")
            messagebox.showinfo("License Status", "License checked in successfully!")
        else:
            messagebox.showerror("License Error", f"Failed to check in license: {response.get('message')}")

    def query_license(self):
        """Query license information"""
        response = self.license_client.query_license()
        
        if response.get('status') == 'success':
            info = response.get('data', {})
            
            # Format the license information
            license_info = (
                f"Software: {info.get('name', 'Unknown')}\n"
                f"Version: {info.get('version', 'Unknown')}\n"
                f"Total Licenses: {info.get('total_licenses', 'Unknown')}\n"
                f"Available Licenses: {info.get('available_licenses', 'Unknown')}\n"
                f"Current Sessions: {info.get('current_sessions', 'Unknown')}"
            )
            
            messagebox.showinfo("License Information", license_info)
        else:
            messagebox.showerror("License Error", f"Failed to query license information: {response.get('message')}")

    def on_closing(self):
        """Handle window closing event"""
        if self.has_license:
            # Ask user if they want to check in their license
            response = messagebox.askyesno("Check In License", "Do you want to check in your license before exiting?")
            if response:
                self.checkin_license()
        
        self.root.destroy()

    # Placeholder action methods
    def new_sample_action(self):
        if not self.has_license:
            messagebox.showwarning("License Required", "You need to check out a license to perform this action.")
            return
        messagebox.showinfo("New Sample", "This action would create a new sample (requires license).")

    def analyze_sample_action(self):
        if not self.has_license:
            messagebox.showwarning("License Required", "You need to check out a license to perform this action.")
            return
        selected = self.sample_tree.selection()
        if not selected:
            messagebox.showinfo("Selection", "Please select a sample to analyze.")
            return
        item = self.sample_tree.item(selected[0])
        messagebox.showinfo("Analyze Sample", f"Analyzing sample: {item['values'][1]} (requires license).")

    def delete_sample_action(self):
        if not self.has_license:
            messagebox.showwarning("License Required", "You need to check out a license to perform this action.")
            return
        selected = self.sample_tree.selection()
        if not selected:
            messagebox.showinfo("Selection", "Please select a sample to delete.")
            return
        self.sample_tree.delete(selected)

    def generate_chart_action(self):
        if not self.has_license:
            messagebox.showwarning("License Required", "You need to check out a license to perform this action.")
            return
        messagebox.showinfo("Generate Chart", "This action would generate a chart based on your selections (requires license).")

    def generate_report_action(self):
        if not self.has_license:
            messagebox.showwarning("License Required", "You need to check out a license to perform this action.")
            return
        messagebox.showinfo("Generate Report", "This action would generate a report based on your selections (requires license).")

def main():
    logger.debug("main: Starting")
    logger.debug("main: Creating tk.Tk() root window")
    root = tk.Tk()
    logger.debug("main: Root window created")
    logger.debug("main: Creating CatlabApp instance")
    app = CatlabApp(root)
    logger.debug("main: CatlabApp instance created")
    # Check if app initialization caused root to be destroyed (e.g., login cancelled)
    try:
        root.winfo_exists()
    except tk.TclError:
        logger.warning("main: Root window destroyed during app init. Exiting.")
        return

    logger.debug("main: Starting root.mainloop()")
    root.mainloop()
    logger.debug("main: root.mainloop() finished")

if __name__ == "__main__":
    logger.info("Starting CATLAB Application...")
    main()
    logger.info("CATLAB Application Exited.")

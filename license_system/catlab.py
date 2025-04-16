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

# Add parent directory to path so we can import license_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from license_system.license_client import LicenseClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
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
        'port': '7070',
        'software_id': '2',  # CATLAB software_id from database
    },
    'user': {
        'id': '1'  # Default user ID
    }
}

class CatlabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CATLAB - Chemical Analysis Tool")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize license client
        self.license_client = LicenseClient(
            self.config['license_server']['ip'],
            int(self.config['license_server']['port']),
            self.config['license_server']['software_id'],
            self.config['user']['id']
        )
        
        # Create flag for license status
        self.has_license = False
        
        # Create widgets
        self.create_widgets()
        
        # Try to check out license on startup
        self.checkout_license()
        
        # Set up a protocol for when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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
    root = tk.Tk()
    app = CatlabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

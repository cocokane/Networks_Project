# Central Instrumentation Facility (CIF) Inventory Management System

A comprehensive web application for managing the inventory, equipment, and resources of the Central Instrumentation Facility at IIT Gandhinagar.

## Overview

The CIF Inventory Management System is a Flask-based web application that provides an interface for tracking and managing laboratory equipment, consumables, software, maintenance visits, and vendor information. The system implements role-based access control with three user types:

- **Visitor**: Can view equipment, consumables, and software information
- **Staff**: Has Visitor permissions plus the ability to modify data and access maintenance records
- **Admin**: Has full access to all functionalities including user management

## Features

- **Equipment Management**: Track laboratory equipment, their locations, quantities, and operational status
- **Consumable Inventory**: Monitor consumable items with stock levels and reorder thresholds
- **Software Tracking**: Manage software licenses, versions, and installation information
- **Maintenance Records**: Keep records of maintenance visits, expenditures, and schedule future maintenance
- **Vendor Management**: Maintain vendor contact information and associations with equipment
- **Lab Visit Tracking**: Record and manage visitors using equipment
- **Role-based Access Control**: Different permission levels for visitors, staff, and administrators
- **Search Functionality**: Quickly find items across all inventory categories

## Database Schema

The system uses a MySQL database with the following tables:

- **Vendors**: Information about equipment and consumable suppliers
- **Equipment**: Laboratory equipment inventory and status
- **Lab_Visits**: Records of laboratory visitors
- **Maintenance_Visits**: Equipment maintenance records and schedules
- **Consumable_Inventory**: Consumable supplies tracking
- **Software**: Software licenses and installation records
- **Users**: User authentication and role management

## Installation

### Prerequisites

- Python 3.6 or higher
- MySQL Server
- Web browser

### Setup

1. Clone the repository:
```bash
   git clone https://github.com/cocokane/Networks_Project.git
```

2. Create and activate a virtual environment:
```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required dependencies:
```bash
   pip install -r requirements.txt
```

4. Set up the MySQL database:
   - Create a MySQL database
   - Import the schema from `cif_database.sql`
```bash
   mysql -u username -p < cif_database.sql
   ```

5. Configure database connection:
   - Create a file named `database_pass.txt` in the project root
   - Add your database password in the format `password: your_password_here`

6. Run the application:
   ```bash
   python app.py
   ```

7. Access the web interface at http://localhost:7000

## Usage

### Authentication

1. **Login**: Access the system using credentials based on your role (Visitor, Staff, or Admin)
2. **Registration**: New users can register accounts (approval may be required)

### Main Features

- **Inventory Overview**: View all inventory categories from the home page
- **Equipment Management**: Track and manage scientific equipment
- **Consumables**: Monitor consumable supplies and stock levels
- **Software**: Manage software licenses and installations
- **Maintenance Records**: Schedule and track equipment maintenance (Staff and Admin only)
- **Search**: Find specific items across categories

## Role-Based Access

- **Visitors**: 
  - View equipment, consumables, and software information
  - Search functionality

- **Staff**:
  - All Visitor permissions
  - Add, update, and manage equipment, consumables, and software
  - Access and update maintenance records

- **Admin**:
  - Full system access
  - User management
  - Database administration capabilities
  - Can act as any role

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, Bootstrap
- **Authentication**: Session-based with password hashing

## Security Features

- Password hashing using SHA-256
- Role-based access control
- Form validation
- Session management
- SQL injection prevention

## Contributors

- Yash Kokane
- Deepanjali Kumari
- Harshita Singh
- Anushika Mishra

## License

This project is for educational purposes at IIT Gandhinagar.



















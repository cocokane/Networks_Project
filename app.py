from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from sql_tools import *
from html_tools import *
import MySQLdb.cursors
import re
import os
import secrets
import hashlib
import uuid
from functools import wraps

import flask

app = Flask(__name__)
# Set debug mode based on environment
app.debug = os.environ.get('FLASK_ENV') == 'development'

# Generate a secure secret key or load from environment variable
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(16)

# Read database credentials from file
def get_db_password():
    try:
        with open('database_pass.txt', 'r') as f:
            for line in f:
                if line.startswith('password:'):
                    return line.strip().split('password:')[1].strip()
    except:
        return None
    
# Enter your mysql connection details here
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = get_db_password()
app.config['MYSQL_DB'] = 'cifdb'

# Initialize MySQL
mysql = MySQL(app)

# Create a login_required decorator to protect routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('bool'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# first
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'authority' in request.form:
        username = request.form['username']
        password = request.form['password']
        authority = request.form['authority']
        
        # Validate authority is one of the allowed values
        valid_roles = ["Visitor", "Staff", "Admin"]
        if authority not in valid_roles:
            msg = 'Invalid role selected!'
            return render_template('login.html', error=msg)
        
        # First check if the user is an admin
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Admin can be identified by either username or email
        # First try username
        cursor.execute('SELECT * FROM users WHERE name = %s AND password = %s AND role = %s',
                      (username, password, "Admin"))
        admin_account = cursor.fetchone()
        
        # If not found, try email
        if not admin_account:
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s AND role = %s',
                         (username, password, "Admin"))
            admin_account = cursor.fetchone()
        
        # If still not found, try with hashed password
        if not admin_account:
            # Hash the password for comparison
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Try username with hashed password
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s AND role = %s',
                         (username, hashed_password, "Admin"))
            admin_account = cursor.fetchone()
            
            # If still not found, try email with hashed password
            if not admin_account:
                cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s AND role = %s',
                             (username, hashed_password, "Admin"))
                admin_account = cursor.fetchone()
        
        # If user is an admin, allow them to login as any role
        if admin_account and authority != "Admin":
            # Admin is logging in as another role
            session['bool'] = True
            session['username'] = admin_account['name']
            session['email'] = admin_account['email']
            session['authority'] = authority  # Use the selected role
            session['id'] = admin_account['id']  # Store user ID in session
            msg = 'Logged in successfully as ' + authority + '!'
            return redirect(url_for('index'))
        
        # Regular authentication for non-admin users or admins logging in as admin
        # Try username first
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s AND role = %s',
                      (username, password, authority))
        account = cursor.fetchone()
        
        # If not found, try email
        if not account:
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s AND role = %s',
                         (username, password, authority))
            account = cursor.fetchone()
        
        # If still not found, try with hashed password
        if not account:
            # Hash the password for comparison
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Try username with hashed password
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s AND role = %s',
                         (username, hashed_password, authority))
            account = cursor.fetchone()
            
            # If still not found, try email with hashed password
            if not account:
                cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s AND role = %s',
                             (username, hashed_password, authority))
                account = cursor.fetchone()
        
        if account:
            session['bool'] = True
            session['username'] = account['name']
            session['email'] = account['email']
            session['authority'] = authority
            session['id'] = account['id']  # Store user ID in session
            msg = 'Logged in successfully!'
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username/password/role!'
            
    return render_template('login.html', error=msg)

@app.route('/test_connection')
def test_connection():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        return f"Connection works! Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
# about us url

# second

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'role' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        
        # Validate role
        valid_roles = ["Visitor", "Staff", "Admin"]
        if role not in valid_roles:
            msg = 'Invalid role selected!'
            return render_template('register.html', msg=msg)
            
        # Validate password strength
        if len(password) < 8:
            msg = 'Password must be at least 8 characters long!'
            return render_template('register.html', msg=msg)
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            # Check if email already exists
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            account = cursor.fetchone()  # fetches the first row
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9 ]+', username):
                msg = 'Username must contain only characters, numbers, and spaces!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
                cursor.execute('INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)', 
                            (username, email, hashed_password, role))
                mysql.connection.commit()
                msg = 'You have successfully registered!'
        except Exception as e:
            msg = f'Registration error: {str(e)}'
            
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)


# third

@app.route('/about_us')
def about():
    return render_template('about_us.html')


@app.route('/contact_us')
def contact():
    return render_template('contact_us.html')


# fourth
@app.route('/index')
def index():
    return render_template('index.html')


# fifth
@app.route('/index', methods=['POST'])
def choose():
    if request.form.get("start"):
        return redirect(url_for('pick_table'))
    else:
        return render_template('index.html')


# sixth

@app.route('/pick_table', methods=['POST', 'GET'])
def pick_table():
    # Check if user is logged in
    if not session.get('bool'):
        return redirect(url_for('login'))
        
    table_name = ''
    operation = ''
    if session.get('table_name'):
        session.pop('table_name', None)
        
    authority = session.get('authority')
    
    # Define accessible tables for each role
    accessible_tables = {
        'Admin': None,  # None means all tables
        'Staff': ["ConsumableInventory", "Equipment", "Software", "MaintenanceVisits"],
        'Visitor': ["ConsumableInventory", "Equipment", "Software"]
    }
    
    # Get all available tables
    tables = show_tables(mysql)
    
    # Generate the dropdown options based on role
    if authority == 'Admin':
        options = nested_list_to_html_select(tables)
    else:
        # Filter tables based on role permissions
        role_tables = accessible_tables.get(authority, [])
        options = ""
        for table in tables:
            if table[0] in role_tables:
                options += f"<option value='{table[0]}'>{table[0]}</option>"
                
    # Handle form submissions
    if request.method == 'POST' and 'table' in request.form:
        selected_table = request.form['table']
        
        # Check if user has permission to access this table
        if authority != 'Admin' and selected_table not in accessible_tables.get(authority, []):
            return render_template('error.html', error=f"You do not have permission to access the {selected_table} table")

        if 'pick' in request.form:
            session['table_name'] = selected_table
            return redirect(url_for('edit'))

        elif 'back' in request.form:
            return render_template('pick_table.html')

        elif 'rename' in request.form:
            # Only Admin can rename tables
            if authority != 'Admin':
                return render_template('error.html', error="Only administrators can rename tables")
                
            operation = 'rename'
            return render_template('pick_table.html', operation=operation, options=options)

        elif 'rename_execute' in request.form:
            # Only Admin can rename tables
            if authority != 'Admin':
                return render_template('error.html', error="Only administrators can rename tables")
                
            table = request.form['table']
            new_name = request.form['new_name']

            try:
                # Rename table
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(f"ALTER TABLE {table} RENAME TO {new_name}")
                mysql.connection.commit()

                session['table_name'] = new_name
                return redirect(url_for('edit'))
            except Exception as e:
                return render_template('invalid.html', e=str(e))

    # Get the table for display
    table_html = nested_list_to_html_table(tables)
    return render_template('pick_table.html', table=table_html, table_name=table_name, options=options, operation=operation)


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    # Check if user is logged in
    if not session.get('bool'):
        return redirect(url_for('login'))
        
    table_name = session.get('table_name')
    if not table_name:
        return redirect(url_for('pick_table'))
        
    # Check permissions based on role
    authority = session.get('authority')
    if authority == 'Visitor' and table_name not in ["ConsumableInventory", "Equipment", "Software"]:
        return render_template('error.html', error="You do not have permission to access this table")
    
    if authority == 'Staff' and table_name not in ["ConsumableInventory", "Equipment", "Software", "MaintenanceVisits"]:
        return render_template('error.html', error="You do not have permission to access this table")
    
    operation = None
    form_html = ''
    options = nested_list_to_html_select_2(col_names(mysql, table_name))
    msg = ''

    # Fix permission check logic - the previous condition was incorrect
    if request.method == 'POST' and 'delete_button' in request.form and authority != 'Admin':
        msg = 'Action not permitted!'
    elif request.method == 'POST' and ('insert_form' in request.form or 'insert_execute' in request.form or 'update_execute' in request.form or 'update_button' in request.form) and authority not in ['Admin', 'Staff']:
        msg = 'Action not permitted!'

    if authority == 'Admin':
        if request.method == 'POST' and 'delete_button' in request.form:
            values = request.form['delete_button'].split(',')
            values = [val if val.isnumeric() else "\'" + val + "\'" for val in values]
            columns = select_with_headers(mysql, table_name)[0]
            where = []
            for col, val in zip(columns, values):
                where.append(col + " = " + val)
            where = " AND ".join(where)
            tables = delete_from_table(mysql, table_name, where)
            try:
                tables = [nested_list_to_html_table(t) for t in tables]
                return render_template('delete_results.html', tables=tables, table_name=table_name)
            except Exception as e:
                return render_template('invalid.html', e=str(e))

    if authority == 'Admin' or authority == 'Staff':
        if request.method == 'POST' and 'insert_form' in request.form:
            operation = 'insert'
            table = nested_list_to_html_table(select_with_headers(mysql, table_name), buttons=True)
            form_html = get_insert_form(select_with_headers(mysql, table_name)[0])
            return render_template('edit.html', table=table, table_name=table_name, operation=operation,
                                   form_html=form_html)
        elif request.method == 'POST' and 'insert_execute' in request.form:
            columns = select_with_headers(mysql, table_name)[0]
            values = []
            for col in columns:
                val = request.form[col]
                if val.isnumeric():
                    values.append(val)
                else:
                    values.append("\'" + val + "\'")
            try:
                tables = insert_to_table(mysql, table_name, columns, values)
            except Exception as e:
                return render_template('invalid.html', e=str(e))
            tables = [nested_list_to_html_table(t) for t in tables]
            return render_template('insert_results.html', tables=tables, table_name=table_name)

        elif request.method == 'POST' and 'update_button' in request.form:
            operation = 'update'
            table = nested_list_to_html_table(select_with_headers(mysql, table_name), buttons=True)
            values = request.form['update_button'].split(',')
            form_html = get_update_form(select_with_headers(mysql, table_name)[0], values)
            values = [val if val.isnumeric() else "\'" + val + "\'" for val in values]
            columns = select_with_headers(mysql, table_name)[0]
            where = []
            for col, val in zip(columns, values):
                where.append(col + " = " + val)
            where = " AND ".join(where)
            session['update_where'] = where
            return render_template('edit.html', table=table, table_name=table_name, operation=operation,
                                   form_html=form_html)
        elif request.method == 'POST' and 'update_execute' in request.form:
            columns = select_with_headers(mysql, table_name)[0]
            values = []
            for col in columns:
                val = request.form[col]
                if val.isnumeric():
                    values.append(val)
                else:
                    values.append("\'" + val + "\'")

            set_statement = []
            for col, val in zip(columns, values):
                set_statement.append(col + " = " + val)
            set_statement = ", ".join(set_statement)

            try:
                tables = update_table(mysql, table_name, set_statement, session['update_where'])
            except Exception as e:
                return render_template('invalid.html', e=str(e))
            tables = [nested_list_to_html_table(t) for t in tables]
            if session.get('update_where'):
                session.pop('update_where', None)
            return render_template('update_results.html', tables=tables, table_name=table_name)

    if authority == 'Admin' or authority == 'Staff' or authority == 'Visitor':
        if request.method == 'POST' and 'search_form' in request.form:
            operation = 'search'
            table = nested_list_to_html_table(select_with_headers(mysql, table_name), buttons=True)
            # form_html = get_insert_form(select_with_headers(mysql, table_name)[0])
            return render_template('edit.html', table=table, table_name=table_name, operation=operation,
                                   options=options)
        elif request.method == 'POST' and 'search_execute' in request.form:
            # table = request.form['table']
            search_col = request.form['column']
            search_word = request.form['search_word']

            # search table
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                f"DROP VIEW IF EXISTS Search_Result; CREATE VIEW Search_Result AS SELECT * FROM {table_name} WHERE {search_col} LIKE '%{search_word}%'")
            result_table = cursor.fetchall()
            cursor.nextset()
            mysql.connection.commit()
            try:
                table_name = 'Search_Result'
                table = nested_list_to_html_table(select_with_headers(mysql, table_name), buttons=True)
                return render_template('search_result.html', table=table, table_name=table_name)
            except Exception as e:
                return render_template('invalid.html', e=str(e))

    table = nested_list_to_html_table(select_with_headers(mysql, table_name), buttons=True)
    return render_template('edit.html', table=table, table_name=table_name, operation=operation, form_html=form_html,
                           msg=msg)


# Add routes for direct category access
@app.route('/equipment')
def equipment():
    if not session.get('bool'):
        return redirect(url_for('login'))
    
    # Set the table name in session
    session['table_name'] = 'Equipment'
    return redirect(url_for('edit'))

@app.route('/consumables')
def consumables():
    if not session.get('bool'):
        return redirect(url_for('login'))
    
    # Set the table name in session
    session['table_name'] = 'ConsumableInventory'
    return redirect(url_for('edit'))

@app.route('/software')
@login_required
def software():
    cursor = mysql.connection.cursor()
    
    # Get software with license information and user's checkout status
    cursor.execute('''
        SELECT s.software_id, s.software_name, s.version, s.description, s.platform,
               s.supported_by, s.installed_location, s.total_seats, s.used_seats,
               s.license_model, v.vendor_name AS vendor_name,
               (SELECT COUNT(*) FROM LicenseUsage 
                WHERE software_id = s.software_id AND user_id = %s) AS has_checkout
        FROM Software s
        LEFT JOIN Vendors v ON s.vendor_id = v.vendor_id
        ORDER BY s.software_name
    ''', (session['id'],))
    
    software_list = cursor.fetchall()
    cursor.close()
    
    return render_template('software.html', 
                          software=software_list, 
                          title='Software')

@app.route('/software_detail')
@login_required
def software_detail():
    cursor = mysql.connection.cursor()
    
    # Get software with license information and user's checkout status
    cursor.execute('''
        SELECT s.software_id, s.software_name, s.version, s.description, s.platform,
               s.supported_by, s.installed_location, s.total_seats, s.used_seats,
               s.license_model, v.vendor_name AS vendor_name,
               (SELECT COUNT(*) FROM LicenseUsage 
                WHERE software_id = s.software_id AND user_id = %s) AS has_checkout
        FROM Software s
        LEFT JOIN Vendors v ON s.vendor_id = v.vendor_id
        ORDER BY s.software_name
    ''', (session['id'],))
    
    software_list = cursor.fetchall()
    cursor.close()
    
    return render_template('software.html', 
                          software=software_list, 
                          title='Software')

@app.route('/maintenance')
def maintenance():
    if not session.get('bool'):
        return redirect(url_for('login'))
    
    # Only Admin and Staff can access maintenance
    authority = session.get('authority')
    if authority not in ['Admin', 'Staff']:
        return render_template('error.html', error="You do not have permission to access this page")
    
    # Set the table name in session
    session['table_name'] = 'MaintenanceVisits'
    return redirect(url_for('edit'))

# License Management Routes
@app.route('/licenses')
def licenses():
    # Check if user is logged in
    if not session.get('bool'):
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor()
    
    # Get all software with license information
    cursor.execute('''
        SELECT s.software_id, s.software_name, s.version, s.total_seats, s.used_seats, 
               s.license_model, s.maintenance_expiry, v.vendor_name as vendor_name
        FROM Software s
        LEFT JOIN Vendors v ON s.vendor_id = v.vendor_id
        ORDER BY s.software_name
    ''')
    software_licenses = cursor.fetchall()
    
    # Get license pools
    cursor.execute('''
        SELECT lp.id, lp.software_id, s.software_name as software_name, lp.total_seats, 
               lp.available_seats, lp.license_model, lp.license_key, 
               lp.expiry_date, lp.maintenance_expiry, v.vendor_name as vendor_name
        FROM LicensePool lp
        JOIN Software s ON lp.software_id = s.software_id
        LEFT JOIN Vendors v ON lp.vendor_id = v.vendor_id
        ORDER BY s.software_name
    ''')
    license_pools = cursor.fetchall()
    
    cursor.close()
    return render_template('licenses.html', 
                          software_licenses=software_licenses,
                          license_pools=license_pools,
                          title='License Management')

@app.route('/license_return')
def license_return():
    # Check if user is logged in
    if not session.get('bool'):
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get all active licenses for the current user
    cursor.execute('''
        SELECT lu.id, s.software_id, s.software_name as software_name, s.version as software_version,
               lu.checkout_time as checkout_date, 
               DATE_ADD(lu.checkout_time, INTERVAL 30 DAY) as expiration_date,
               lu.host_name as machine_id,
               DATEDIFF(DATE_ADD(lu.checkout_time, INTERVAL 30 DAY), NOW()) as days_remaining
        FROM LicenseUsage lu
        JOIN Software s ON lu.software_id = s.software_id
        WHERE lu.user_id = %s
        ORDER BY lu.checkout_time DESC
    ''', (session['id'],))
    
    active_licenses = cursor.fetchall()
    cursor.close()
    
    return render_template('license_return.html', 
                        active_licenses=active_licenses, 
                        title='License Return')

@app.route('/return_license', methods=['POST'])
def return_license():
    # Check if user is logged in
    if not session.get('bool'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        license_id = request.form['license_id']
        return_reason = request.form['return_reason']
        notes = request.form['notes']
        confirm_uninstall = 'confirm_uninstall' in request.form
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get license details
        cursor.execute('''
            SELECT lu.id, lu.software_id, lu.session_id
            FROM LicenseUsage lu
            WHERE lu.id = %s AND lu.user_id = %s
        ''', (license_id, session['id']))
        
        license_details = cursor.fetchone()
        
        if license_details:
            # Delete the usage record
            cursor.execute('DELETE FROM LicenseUsage WHERE id = %s', (license_id,))
            
            # Log the return with details
            details = f"Return reason: {return_reason}. Notes: {notes}. Uninstall confirmed: {confirm_uninstall}"
            cursor.execute('''
                INSERT INTO LicenseAudit 
                (software_id, user_id, action, ip_address, session_id, details)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (license_details['software_id'], 
                  session['id'], 
                  'checkin', 
                  request.remote_addr, 
                  license_details['session_id'], 
                  details))
            
            # Update available seats
            cursor.execute('SELECT update_license_available_seats()')
            
            mysql.connection.commit()
            cursor.close()
            
            flash('License returned successfully!', 'success')
        else:
            cursor.close()
            flash('Error: License not found or not associated with your account.', 'danger')
        
        return redirect(url_for('license_return'))

@app.route('/renew_license', methods=['POST'])
def renew_license():
    # Check if user is logged in
    if not session.get('bool'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        license_id = request.form['license_id']
        duration = int(request.form['duration'])
        reason = request.form['reason']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Update license expiration by extending the expected_checkin date
        cursor.execute('''
            UPDATE LicenseUsage
            SET expected_checkin = DATE_ADD(COALESCE(expected_checkin, NOW()), INTERVAL %s DAY)
            WHERE id = %s AND user_id = %s
        ''', (duration, license_id, session['id']))
        
        if cursor.rowcount > 0:
            # Log the renewal
            cursor.execute('''
                SELECT software_id, session_id FROM LicenseUsage WHERE id = %s
            ''', (license_id,))
            license_info = cursor.fetchone()
            
            if license_info:
                cursor.execute('''
                    INSERT INTO LicenseAudit 
                    (software_id, user_id, action, ip_address, session_id, details)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (license_info['software_id'], 
                      session['id'], 
                      'renew', 
                      request.remote_addr, 
                      license_info['session_id'], 
                      f"Renewed for {duration} days. Reason: {reason}"))
            
            mysql.connection.commit()
            cursor.close()
            flash('License renewed successfully!', 'success')
        else:
            cursor.close()
            flash('Error: License not found or not associated with your account.', 'danger')
        
        return redirect(url_for('license_return'))

@app.route('/license_usage')
def license_usage():
    # Check if user is logged in
    if not session.get('bool'):
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor()
    
    # Get current license usage
    cursor.execute('''
        SELECT lu.id, s.software_name as software_name, s.version, u.name as user_name, 
               u.email, lu.checkout_time, lu.last_heartbeat, 
               lu.ip_address, lu.host_name, lu.checkout_location
        FROM LicenseUsage lu
        JOIN Software s ON lu.software_id = s.software_id
        JOIN Users u ON lu.user_id = u.id
        ORDER BY lu.checkout_time DESC
    ''')
    active_usage = cursor.fetchall()
    
    # Get recent license audit history
    cursor.execute('''
        SELECT la.id, s.software_name as software_name, u.name as user_name, 
               la.action, la.action_time, la.ip_address, la.details
        FROM LicenseAudit la
        JOIN Software s ON la.software_id = s.software_id
        JOIN Users u ON la.user_id = u.id
        ORDER BY la.action_time DESC
        LIMIT 100
    ''')
    audit_history = cursor.fetchall()
    
    cursor.close()
    return render_template('license_usage.html', 
                          active_usage=active_usage,
                          audit_history=audit_history,
                          title='License Usage')

@app.route('/license_rules')
def license_rules():
    # Check if user is logged in
    if not session.get('bool'):
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor()
    
    # Get all license rules
    cursor.execute('''
        SELECT lr.id, s.software_name as software_name, lr.rule_type, lr.rule_value, 
               lr.priority, lr.is_active, u.name as created_by_name
        FROM LicenseRules lr
        JOIN Software s ON lr.software_id = s.software_id
        LEFT JOIN Users u ON lr.created_by = u.id
        ORDER BY s.software_name, lr.priority
    ''')
    rules = cursor.fetchall()
    
    # Get all software for the form
    cursor.execute('SELECT software_id, software_name, version FROM Software ORDER BY software_name')
    software_list = cursor.fetchall()
    
    cursor.close()
    return render_template('license_rules.html', 
                          rules=rules,
                          software_list=software_list,
                          title='License Rules')

@app.route('/add_license_rule', methods=['POST'])
def add_license_rule():
    # Check if user is logged in
    if not session.get('bool'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        software_id = request.form['software_id']
        rule_type = request.form['rule_type']
        rule_value = request.form['rule_value']
        priority = request.form['priority']
        is_active = 'is_active' in request.form
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO LicenseRules 
            (software_id, rule_type, rule_value, priority, is_active, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (software_id, rule_type, rule_value, priority, is_active, session['id']))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('License rule added successfully!', 'success')
        return redirect(url_for('license_rules'))

@app.route('/user_groups')
@login_required
def user_groups():
    cursor = mysql.connection.cursor()
    
    # Get all user groups
    cursor.execute('''
        SELECT ug.id, ug.group_name, ug.description, 
               COUNT(ugm.user_id) as member_count
        FROM UserGroups ug
        LEFT JOIN UserGroupMembers ugm ON ug.id = ugm.group_id
        GROUP BY ug.id
        ORDER BY ug.group_name
    ''')
    groups = cursor.fetchall()
    
    cursor.close()
    return render_template('user_groups.html', 
                          groups=groups,
                          title='User Groups')

@app.route('/group_members/<int:group_id>')
@login_required
def group_members(group_id):
    cursor = mysql.connection.cursor()
    
    # Get group details
    cursor.execute('SELECT id, group_name, description FROM UserGroups WHERE id = %s', (group_id,))
    group = cursor.fetchone()
    
    # Get group members
    cursor.execute('''
        SELECT u.id, u.name, u.email, ugm.added_at, 
               adder.name as added_by_name
        FROM UserGroupMembers ugm
        JOIN users u ON ugm.user_id = u.id
        LEFT JOIN users adder ON ugm.added_by = adder.id
        WHERE ugm.group_id = %s
        ORDER BY u.name
    ''', (group_id,))
    members = cursor.fetchall()
    
    # Get users not in the group for the form
    cursor.execute('''
        SELECT id, name, email 
        FROM users
        WHERE id NOT IN (
            SELECT user_id FROM UserGroupMembers WHERE group_id = %s
        )
        ORDER BY name
    ''', (group_id,))
    available_users = cursor.fetchall()
    
    cursor.close()
    return render_template('group_members.html', 
                          group=group,
                          members=members,
                          available_users=available_users,
                          title=f'Members of {group["group_name"]}')

@app.route('/add_group_member', methods=['POST'])
@login_required
def add_group_member():
    if request.method == 'POST':
        group_id = request.form['group_id']
        user_id = request.form['user_id']
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO UserGroupMembers 
            (group_id, user_id, added_by)
            VALUES (%s, %s, %s)
        ''', (group_id, user_id, session['id']))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('User added to group successfully!', 'success')
        return redirect(url_for('group_members', group_id=group_id))

@app.route('/remove_group_member/<int:group_id>/<int:user_id>')
@login_required
def remove_group_member(group_id, user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('''
        DELETE FROM UserGroupMembers 
        WHERE group_id = %s AND user_id = %s
    ''', (group_id, user_id))
    
    mysql.connection.commit()
    cursor.close()
    
    flash('User removed from group successfully!', 'success')
    return redirect(url_for('group_members', group_id=group_id))

@app.route('/software_access/<string:software_id>')
@login_required
def software_access(software_id):
    cursor = mysql.connection.cursor()
    
    # Get software details
    cursor.execute('SELECT software_id, software_name, version FROM Software WHERE software_id = %s', (software_id,))
    software = cursor.fetchone()
    
    # Get groups with access
    cursor.execute('''
        SELECT sga.group_id, ug.group_name, sga.access_level, 
               sga.granted_at, u.name as granted_by_name
        FROM SoftwareGroupAccess sga
        JOIN UserGroups ug ON sga.group_id = ug.id
        LEFT JOIN users u ON sga.granted_by = u.id
        WHERE sga.software_id = %s
        ORDER BY ug.group_name
    ''', (software_id,))
    access_groups = cursor.fetchall()
    
    # Get groups without access for the form
    cursor.execute('''
        SELECT id, group_name 
        FROM UserGroups
        WHERE id NOT IN (
            SELECT group_id FROM SoftwareGroupAccess WHERE software_id = %s
        )
        ORDER BY group_name
    ''', (software_id,))
    available_groups = cursor.fetchall()
    
    cursor.close()
    return render_template('software_access.html', 
                          software=software,
                          access_groups=access_groups,
                          available_groups=available_groups,
                          title=f'Access Control for {software["software_name"]}')

@app.route('/add_software_access', methods=['POST'])
@login_required
def add_software_access():
    if request.method == 'POST':
        software_id = request.form['software_id']
        group_id = request.form['group_id']
        access_level = request.form['access_level']
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO SoftwareGroupAccess 
            (software_id, group_id, access_level, granted_by)
            VALUES (%s, %s, %s, %s)
        ''', (software_id, group_id, access_level, session['id']))
        
        mysql.connection.commit()
        cursor.close()
        
        flash('Group access added successfully!', 'success')
        return redirect(url_for('software_access', software_id=software_id))

@app.route('/remove_software_access/<string:software_id>/<int:group_id>')
@login_required
def remove_software_access(software_id, group_id):
    cursor = mysql.connection.cursor()
    cursor.execute('''
        DELETE FROM SoftwareGroupAccess 
        WHERE software_id = %s AND group_id = %s
    ''', (software_id, group_id))
    
    mysql.connection.commit()
    cursor.close()
    
    flash('Group access removed successfully!', 'success')
    return redirect(url_for('software_access', software_id=software_id))

@app.route('/checkout_license/<string:software_id>')
@login_required
def checkout_license(software_id):
    cursor = mysql.connection.cursor()
    
    # Check if there are available licenses
    cursor.execute('''
        SELECT s.software_id, s.software_name, lp.available_seats, lp.license_model
        FROM Software s
        JOIN LicensePool lp ON s.software_id = lp.software_id
        WHERE s.software_id = %s AND lp.available_seats > 0
    ''', (software_id,))
    license_info = cursor.fetchone()
    
    if not license_info:
        # Log the denial
        cursor.execute('''
            INSERT INTO LicenseAudit 
            (software_id, user_id, action, ip_address, details)
            VALUES (%s, %s, %s, %s, %s)
        ''', (software_id, session['id'], 'deny', request.remote_addr, 'No licenses available'))
        
        mysql.connection.commit()
        cursor.close()
        flash('No licenses available for this software!', 'danger')
        return redirect(url_for('software'))
    
    # Check if user has permission
    cursor.execute('''
        SELECT COUNT(*) as has_access
        FROM UserGroupMembers ugm
        JOIN SoftwareGroupAccess sga ON ugm.group_id = sga.group_id
        WHERE ugm.user_id = %s AND sga.software_id = %s
    ''', (session['id'], software_id))
    access_check = cursor.fetchone()
    
    if not access_check or access_check['has_access'] == 0:
        # Log the denial
        cursor.execute('''
            INSERT INTO LicenseAudit 
            (software_id, user_id, action, ip_address, details)
            VALUES (%s, %s, %s, %s, %s)
        ''', (software_id, session['id'], 'deny', request.remote_addr, 'User does not have permission'))
        
        mysql.connection.commit()
        cursor.close()
        flash('You do not have permission to use this software!', 'danger')
        return redirect(url_for('software'))
    
    # Check if user already has a license checked out
    cursor.execute('''
        SELECT id
        FROM LicenseUsage
        WHERE software_id = %s AND user_id = %s
    ''', (software_id, session['id']))
    existing_checkout = cursor.fetchone()
    
    if existing_checkout:
        # Update the heartbeat
        cursor.execute('''
            UPDATE LicenseUsage
            SET last_heartbeat = NOW()
            WHERE id = %s
        ''', (existing_checkout['id'],))
        
        mysql.connection.commit()
        cursor.close()
        flash('You already have a license for this software!', 'info')
        return redirect(url_for('software'))
    
    # Create a new checkout
    session_id = str(uuid.uuid4())
    host_name = request.headers.get('Host', 'unknown')
    
    cursor.execute('''
        INSERT INTO LicenseUsage 
        (software_id, user_id, session_id, ip_address, host_name)
        VALUES (%s, %s, %s, %s, %s)
    ''', (software_id, session['id'], session_id, request.remote_addr, host_name))
    
    # Log the checkout
    cursor.execute('''
        INSERT INTO LicenseAudit 
        (software_id, user_id, action, ip_address, session_id, details)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (software_id, session['id'], 'checkout', request.remote_addr, session_id, 'License checked out'))
    
    # Update available seats
    cursor.execute('SELECT update_license_available_seats()')
    
    mysql.connection.commit()
    cursor.close()
    
    flash(f'License for {license_info["software_name"]} checked out successfully!', 'success')
    return redirect(url_for('software'))

@app.route('/checkin_license/<string:software_id>')
@login_required
def checkin_license(software_id):
    cursor = mysql.connection.cursor()
    
    # Get the checkout info
    cursor.execute('''
        SELECT id, session_id
        FROM LicenseUsage
        WHERE software_id = %s AND user_id = %s
    ''', (software_id, session['id']))
    checkout = cursor.fetchone()
    
    if not checkout:
        cursor.close()
        flash('You do not have a license checked out for this software!', 'danger')
        return redirect(url_for('software'))
    
    # Delete the usage record
    cursor.execute('DELETE FROM LicenseUsage WHERE id = %s', (checkout['id'],))
    
    # Log the checkin
    cursor.execute('''
        INSERT INTO LicenseAudit 
        (software_id, user_id, action, ip_address, session_id, details)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (software_id, session['id'], 'checkin', request.remote_addr, checkout['session_id'], 'License checked in'))
    
    # Update available seats
    cursor.execute('SELECT update_license_available_seats()')
    
    mysql.connection.commit()
    cursor.close()
    
    flash('License checked in successfully!', 'success')
    return redirect(url_for('software'))

@app.route('/license_checkout')
@login_required
def license_checkout():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch available software licenses
    available_software = []  # This should be replaced with actual database query

    # Render the license checkout template with available software
    return render_template('license_checkout.html', available_software=available_software)

# app run

if __name__ == '__main__':
    app.run(debug=True, port=7000)

# List of changes to be made to the program (by me)
# 1. Change the basic database tables (Prescription -> add doctor id, )
# Show inventory, product, medicine together. Include these tables: 
# Purchase order directly references medicine id. 
# 2. Remove foreign keys. This can be done by making joins.
# 3. Change access. For that maybe make different login pages. 
# 4. For patient, add a search button for all the prescriptions he has taken. (akshat)  In Medicine, add a search bar. 
# 5. Undo Button (optional)


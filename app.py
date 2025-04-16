from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from sql_tools import *
from html_tools import *
import MySQLdb.cursors
import re
import os
import secrets
import hashlib

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
            cursor.execute('SELECT * FROM users WHERE name = %s AND password = %s AND role = %s',
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
            msg = 'Logged in successfully as ' + authority + '!'
            return redirect(url_for('index'))
        
        # Regular authentication for non-admin users or admins logging in as admin
        # Try username first
        cursor.execute('SELECT * FROM users WHERE name = %s AND password = %s AND role = %s',
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
            cursor.execute('SELECT * FROM users WHERE name = %s AND password = %s AND role = %s',
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
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
                cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s)', 
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
        'Staff': ["Consumable_Inventory", "Equipment", "Software", "Maintenance_Visits"],
        'Visitor': ["Consumable_Inventory", "Equipment", "Software"]
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
    if authority == 'Visitor' and table_name not in ["Consumable_Inventory", "Equipment", "Software"]:
        return render_template('error.html', error="You do not have permission to access this table")
    
    if authority == 'Staff' and table_name not in ["Consumable_Inventory", "Equipment", "Software", "Maintenance_Visits"]:
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
    session['table_name'] = 'Consumable_Inventory'
    return redirect(url_for('edit'))

@app.route('/software')
def software():
    if not session.get('bool'):
        return redirect(url_for('login'))
    
    # Set the table name in session
    session['table_name'] = 'Software'
    return redirect(url_for('edit'))

@app.route('/maintenance')
def maintenance():
    if not session.get('bool'):
        return redirect(url_for('login'))
    
    # Only Admin and Staff can access maintenance
    authority = session.get('authority')
    if authority not in ['Admin', 'Staff']:
        return render_template('error.html', error="You do not have permission to access this page")
    
    # Set the table name in session
    session['table_name'] = 'Maintenance_Visits'
    return redirect(url_for('edit'))

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


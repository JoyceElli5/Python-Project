from flask import Flask, render_template, request, redirect, session, flash, url_for 
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json
import os
from datetime import datetime, timedelta
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from functools import wraps
import bleach
from decimal import Decimal, InvalidOperation
import sendemail

app = Flask(__name__)

# Use environment variables for sensitive data
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '918273645')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'expense_tracker')

# Session configuration for security
app.config['SESSION_COOKIE_SECURE'] = True  # Only send over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # Session timeout

mysql = MySQL(app)

# Security decorator for authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

# Input validation functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    return re.match(r'^[A-Za-z0-9_]{3,20}$', username) is not None

def validate_amount(amount_str):
    try:
        amount = Decimal(str(amount_str))
        return 0 < amount <= Decimal('999999.99')
    except (InvalidOperation, ValueError):
        return False

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if text is None:
        return ""
    return bleach.clean(str(text), tags=[], attributes={}, strip=True)

# HOME PAGE
@app.route("/home")
@login_required
def home():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get user's payment methods with parameterized query
        cursor.execute('SELECT * FROM payment_methods WHERE user_id = %s', (session['id'],))
        payment_methods = cursor.fetchall()
        
        if not payment_methods:
            payment_methods = []

        cursor.execute('SELECT * FROM user_accounts WHERE userid = %s', (session['id'],))
        user_accounts = cursor.fetchall()
        if not user_accounts:
            user_accounts = []    
        
        # Get total balance from all payment methods
        total_balance = sum(float(method['balance']) for method in payment_methods) if payment_methods else 0
        
        # Get total expenses for current month with parameterized query
        cursor.execute('''
            SELECT SUM(amount) as total_expenses 
            FROM expenses 
            WHERE userid = %s AND MONTH(date) = MONTH(CURRENT_DATE()) AND YEAR(date) = YEAR(CURRENT_DATE())
        ''', (session['id'],))
        result = cursor.fetchone()
        total_expenses = float(result['total_expenses']) if result['total_expenses'] else 0
        
        total_income = total_balance + total_expenses
        
        # Get budget limit with parameterized query
        cursor.execute('SELECT limits FROM limitss WHERE user_id = %s ORDER BY id DESC LIMIT 1', (session['id'],))
        limit_result = cursor.fetchone()
        budget_limit = float(limit_result['limits']) if limit_result and limit_result['limits'] else 0

        # Get recent transactions with parameterized query
        cursor.execute('''
            SELECT * FROM expenses 
            WHERE userid = %s 
            ORDER BY date DESC 
            LIMIT 5
        ''', (session['id'],))
        recent_transactions = cursor.fetchall()
        
        # Calculate date range for chart
        today = datetime.now()
        start_date = datetime(today.year, today.month, 1).strftime('%d %b')
        end_date = today.strftime('%d %b')
        
        cursor.close()
        
        return render_template(
            'homepage.html',
            payment_methods=payment_methods,
            total_balance=total_balance,
            total_income=total_income,
            total_expenses=total_expenses,
            budget_limit=budget_limit,
            recent_transactions=recent_transactions,
            start_date=start_date,
            end_date=end_date,
            user_accounts=user_accounts,
            get_category_icon=get_category_icon
        )
    except Exception as e:
        app.logger.error(f"Error in home route: {str(e)}")
        flash('An error occurred while loading the dashboard.', 'error')
        return redirect(url_for('signin'))

@app.route("/")
def add():
    return render_template("index.html")

# SIGN UP OR REGISTER
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username', ''))
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        
        # Input validation
        if not validate_username(username):
            flash('Username must be 3-20 characters long and contain only letters, numbers, and underscores.', "error")
            return render_template('signup.html')
            
        if not validate_email(email):
            flash('Please enter a valid email address.', "error")
            return render_template('signup.html')
            
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', "error")
            return render_template('signup.html')

        try:
            cursor = mysql.connection.cursor()
            
            # Check if username already exists
            cursor.execute('SELECT * FROM register WHERE username = %s', (username,))
            if cursor.fetchone():
                flash('Username already exists!', "error")
                cursor.close()
                return render_template('signup.html')
            
            # Check if email already exists
            cursor.execute('SELECT * FROM register WHERE email = %s', (email,))
            if cursor.fetchone():
                flash('Email already registered!', "error")
                cursor.close()
                return render_template('signup.html')
            
            # Hash password before storing
            hashed_password = generate_password_hash(password)
            
            # Insert new user with parameterized query
            cursor.execute('INSERT INTO register (username, email, password) VALUES (%s, %s, %s)', 
                         (username, email, hashed_password))
            mysql.connection.commit()
            cursor.close()
            
            flash('You have successfully registered!', "success")
            return redirect(url_for('signin'))
            
        except Exception as e:
            app.logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', "error")
        
    return render_template('signup.html')

# LOGIN PAGE
@app.route("/signin")
def signin():
    return render_template("login.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        
        if not validate_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template('login.html')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM register WHERE email = %s', (email,))
            account = cursor.fetchone()
            cursor.close()

            if account and check_password_hash(account[3], password):  # account[3] is password field
                session.permanent = True
                session['loggedin'] = True
                session['id'] = account[0]
                session['email'] = account[2]  # account[2] is email field
                session['username'] = account[1]  # account[1] is username field
                flash("Login successful", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid email or password", "error")

        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            flash("An error occurred during login. Please try again.", "error")

    return render_template('login.html')

# ADDING DATA
@app.route("/add")
@login_required
def adding():
    try:
        # Fetch the user's accounts to populate the dropdown
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id, account_name, account_type, balance FROM user_accounts WHERE userid = %s', (session['id'],))
        user_accounts = cursor.fetchall()
        cursor.close()
        
        return render_template('add.html', user_accounts=user_accounts)
    except Exception as e:
        app.logger.error(f"Error loading accounts: {str(e)}")
        flash('An error occurred while loading your accounts.', 'error')
        return redirect(url_for('home'))

@app.route('/addexpense', methods=['GET', 'POST'])
@login_required
def addexpense():
    if request.method == 'POST':
        datetime_str = request.form.get('date', '')  # Expecting datetime-local format
        expensename = sanitize_input(request.form.get('expensename', '').strip())
        amount_str = request.form.get('amount', '').strip()
        paymode = sanitize_input(request.form.get('paymode', '').strip())
        category = sanitize_input(request.form.get('category', '').strip())
        account_id = request.form.get('account_id', '').strip()

        # Parse datetime-local input (e.g., '2025-06-04T14:30')
        try:
            expense_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
            expense_date = expense_datetime.date()
        except ValueError:
            flash("Invalid date/time format! Please select a valid date and time.", "error")
            return redirect(url_for('adding'))

        today = datetime.today().date()
        one_week_ago = today - timedelta(days=7)

        # Date barrier check
        if not (one_week_ago <= expense_date <= today):
            flash(f"Date must be within the last 7 days (from {one_week_ago} to {today})", "error")
            return redirect(url_for('adding'))

        # Validate amount input
        try:
            amount = float(amount_str)
            if amount < 0.01 or amount > 999999.99:
                raise ValueError("Amount out of allowed range.")
        except ValueError:
            flash("Please enter a valid amount between 0.01 and 999999.99", "error")
            return redirect(url_for('adding'))

        # Validate expense name
        if not expensename:
            flash("Expense name is required", "error")
            return redirect(url_for('adding'))

        # Optional: further validation on paymode, category, account_id if needed

        try:
            cursor = mysql.connection.cursor()

            # Fetch user limit
            cursor.execute(
                'SELECT limits FROM limitss WHERE user_id = %s ORDER BY id DESC LIMIT 1',
                (session['id'],)
            )
            result = cursor.fetchone()
            limit = float(result[0]) if result else None

            # Check if amount exceeds limit
            if limit and amount > limit:
                session['pending_expense'] = {
                    'date': datetime_str,
                    'expensename': expensename,
                    'amount': amount,
                    'paymode': paymode,
                    'category': category,
                    'account_id': account_id
                }
                cursor.close()
                return render_template('limit_warning.html', amount=amount, limit=limit)

            # Insert into expenses
            cursor.execute(
                'INSERT INTO expenses (userid, date, expensename, amount, paymode, category, account_id) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (session['id'], expense_date, expensename, amount, paymode, category, account_id)
            )
            mysql.connection.commit()
            cursor.close()

            user_email = session.get('email')  # Make sure you store email in session on login
            if user_email:
                 message = f"Hey, your recent expense of GH${amount} exceeded your set limit of GH${limit}."
            sendemail.sendmail(message, user_email) 
            flash("Expense added successfully!", "success")
            return redirect(url_for('display'))

        except Exception as e:
            app.logger.error(f"Add expense error: {str(e)}")
            flash("An error occurred while adding the expense.", "error")
            return redirect(url_for('adding'))

    # For GET request, render the form
    return render_template('addexpense.html')
@app.route('/confirm_expense', methods=['POST'])
@login_required
def confirm_expense():
    data = session.get('pending_expense')
    if not data:
        return redirect(url_for('adding'))

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO expenses (userid, date, expensename, amount, paymode, category, account_id) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (session['id'], data['date'], data['expensename'], data['amount'],
             data['paymode'], data['category'], data['account_id'])
        )
        mysql.connection.commit()
        cursor.close()
        
        session.pop('pending_expense', None)
        flash('Expense added successfully!', 'success')
        return redirect(url_for('display'))
        
    except Exception as e:
        app.logger.error(f"Confirm expense error: {str(e)}")
        flash('An error occurred while adding the expense.', 'error')
        return redirect(url_for('adding'))

# DISPLAY GRAPH
@app.route("/display")
@login_required
def display():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM expenses WHERE userid = %s ORDER BY date DESC', (session['id'],))
        expense = cursor.fetchall()
        cursor.close()
        return render_template('display.html', expense=expense)
    except Exception as e:
        app.logger.error(f"Display error: {str(e)}")
        flash('An error occurred while loading expenses.', 'error')
        return redirect(url_for('home'))

# DELETE DATA
@app.route('/delete/<int:expense_id>', methods=['POST', 'GET'])
@login_required
def delete(expense_id):
    try:
        cursor = mysql.connection.cursor()
        # Verify the expense belongs to the current user before deleting
        cursor.execute('DELETE FROM expenses WHERE id = %s AND userid = %s', (expense_id, session['id']))
        
        if cursor.rowcount > 0:
            mysql.connection.commit()
            flash('Expense deleted successfully!', 'success')
        else:
            flash('Expense not found or you do not have permission to delete it.', 'error')
        
        cursor.close()
        
    except Exception as e:
        app.logger.error(f"Delete error: {str(e)}")
        flash('An error occurred while deleting the expense.', 'error')
    
    return redirect(url_for('display'))

# UPDATE DATA
@app.route('/edit/<int:expense_id>', methods=['POST', 'GET'])
@login_required
def edit(expense_id):
    try:
        cursor = mysql.connection.cursor()
        # Verify the expense belongs to the current user
        cursor.execute('SELECT * FROM expenses WHERE id = %s AND userid = %s', (expense_id, session['id']))
        row = cursor.fetchone()
        cursor.close()
        
        if not row:
            flash('Expense not found or you do not have permission to edit it.', 'error')
            return redirect(url_for('display'))
        
        return render_template('edit.html', expenses=row)
        
    except Exception as e:
        app.logger.error(f"Edit error: {str(e)}")
        flash('An error occurred while loading the expense.', 'error')
        return redirect(url_for('display'))

@app.route('/update/<int:expense_id>', methods=['POST'])
@login_required
def update(expense_id):
    if request.method == 'POST':
        date = request.form.get('date', '')
        expensename = sanitize_input(request.form.get('expensename', ''))
        amount_str = request.form.get('amount', '')
        paymode = sanitize_input(request.form.get('paymode', ''))
        category = sanitize_input(request.form.get('category', ''))
        
        # Validate inputs
        if not validate_amount(amount_str):
            flash('Please enter a valid amount between 0.01 and 999999.99', 'error')
            return redirect(url_for('edit', expense_id=expense_id))
        
        amount = float(amount_str)
        
        if not expensename.strip():
            flash('Expense name is required', 'error')
            return redirect(url_for('edit', expense_id=expense_id))

        try:
            cursor = mysql.connection.cursor()
            # Update only if the expense belongs to the current user
            cursor.execute(
                "UPDATE expenses SET date = %s, expensename = %s, amount = %s, paymode = %s, category = %s WHERE id = %s AND userid = %s",
                (date, expensename, amount, paymode, category, expense_id, session['id'])
            )
            
            if cursor.rowcount > 0:
                mysql.connection.commit()
                flash('Expense updated successfully!', 'success')
            else:
                flash('Expense not found or you do not have permission to update it.', 'error')
            
            cursor.close()
            
        except Exception as e:
            app.logger.error(f"Update error: {str(e)}")
            flash('An error occurred while updating the expense.', 'error')
        
        return redirect(url_for('display'))

# Helper function to get category icon
def get_category_icon(category):
    icons = {
        'food': 'fa-utensils',
        'entertainment': 'fa-film',
        'business': 'fa-briefcase',
        'rent': 'fa-home',
        'EMI': 'fa-credit-card',
        'other': 'fa-tag'
    }
    return icons.get(category, 'fa-tag')

app.jinja_env.globals.update(get_category_icon=get_category_icon)

# Add payment method route
@app.route("/add_payment_method", methods=['POST'])
@login_required
def add_payment_method():
    try:
        data = request.get_json()
        payment_type = sanitize_input(data.get('type', ''))
        name = sanitize_input(data.get('name', ''))
        balance_str = data.get('balance', '')

        if not all([payment_type, name, balance_str]):
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        if not validate_amount(balance_str):
            return jsonify({'success': False, 'message': 'Invalid balance amount'})

        balance = float(balance_str)
        
        cursor = mysql.connection.cursor()
        
        # Insert into user_accounts
        cursor.execute('''
            INSERT INTO user_accounts (userid, account_name, account_type, balance)
            VALUES (%s, %s, %s, %s)
        ''', (session['id'], name, payment_type, balance))

        # Insert into payment_methods
        cursor.execute('''
            INSERT INTO payment_methods (user_id, type, name, balance)
            VALUES (%s, %s, %s, %s)
        ''', (session['id'], payment_type, name, balance))

        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Payment method added successfully'})
        
    except Exception as e:
        app.logger.error(f"Add payment method error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to add payment method'})

# Get chart data route
@app.route("/get_chart_data")
@login_required
def get_chart_data():
    try:
        period = request.args.get('period', 'month')
        
        today = datetime.now()
        labels = []
        values = []
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if period == 'week':
            start_date = (today - timedelta(days=6)).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
            
            for i in range(7):
                date = today - timedelta(days=6-i)
                labels.append(date.strftime('%d %b'))
            
            cursor.execute(''' 
                SELECT DATE(date) as expense_date, SUM(amount) as total
                FROM expenses
                WHERE userid = %s AND DATE(date) BETWEEN %s AND %s
                GROUP BY DATE(date)
                ORDER BY DATE(date)
            ''', (session['id'], start_date, end_date))
            
            results = cursor.fetchall()
            expense_dict = {result['expense_date'].strftime('%d %b'): float(result['total']) for result in results}
            
            for label in labels:
                values.append(expense_dict.get(label, 0))
                
        elif period == 'month':
            for week in range(1, 5):
                labels.append(f'Week {week}')
            
            cursor.execute('''
                SELECT 
                    FLOOR((DAY(date) - 1) / 7) + 1 as week_number,
                    SUM(amount) as total
                FROM expenses
                WHERE userid = %s AND YEAR(date) = %s AND MONTH(date) = %s
                GROUP BY week_number
                ORDER BY week_number
            ''', (session['id'], today.year, today.month))
            
            results = cursor.fetchall()
            expense_dict = {result['week_number']: float(result['total']) for result in results}
            
            for i in range(1, 5):
                values.append(expense_dict.get(i, 0))
                
        else:  # year
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            labels = months
            
            cursor.execute('''
                SELECT 
                    MONTH(date) as month_number,
                    SUM(amount) as total
                FROM expenses
                WHERE userid = %s AND YEAR(date) = %s
                GROUP BY month_number
                ORDER BY month_number
            ''', (session['id'], today.year))
            
            results = cursor.fetchall()
            expense_dict = {result['month_number']: float(result['total']) for result in results}
            
            for i in range(1, 13):
                values.append(expense_dict.get(i, 0))
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'labels': labels,
            'values': values,
            'start_date': labels[0] if labels else '',
            'end_date': labels[-1] if labels else ''
        })
        
    except Exception as e:
        app.logger.error(f"Chart data error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load chart data'})

# Get transactions by category
@app.route("/get_transactions_by_category")
@login_required
def get_transactions_by_category():
    try:
        category = sanitize_input(request.args.get('category', 'all'))
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if category == 'all':
            cursor.execute('''
                SELECT * FROM expenses 
                WHERE userid = %s 
                ORDER BY date DESC 
                LIMIT 10
            ''', (session['id'],))
        else:
            cursor.execute('''
                SELECT * FROM expenses 
                WHERE userid = %s AND category = %s
                ORDER BY date DESC 
                LIMIT 10
            ''', (session['id'], category))
        
        transactions = cursor.fetchall()
        cursor.close()
        
        # Format dates for display
        for transaction in transactions:
            if isinstance(transaction['date'], datetime):
                transaction['date'] = transaction['date'].strftime('%d %b, %Y')
        
        return jsonify({
            'success': True,
            'transactions': transactions
        })
        
    except Exception as e:
        app.logger.error(f"Transactions by category error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load transactions'})

@app.route("/add_account", methods=['GET', 'POST'])
@login_required
def add_account():
    if request.method == 'POST':
        account_name = sanitize_input(request.form.get('account_name', ''))
        account_type = sanitize_input(request.form.get('account_type', ''))
        initial_balance_str = request.form.get('initial_balance', '')
        
        if not validate_amount(initial_balance_str):
            flash('Please enter a valid initial balance.', 'error')
            return render_template('add_account.html')
        
        initial_balance = float(initial_balance_str)
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('''INSERT INTO user_accounts (userid, account_name, account_type, balance) 
                             VALUES (%s, %s, %s, %s)''', 
                          (session['id'], account_name, account_type, initial_balance))
            mysql.connection.commit()
            cursor.close()
            
            flash('Account added successfully!', 'success')
            return redirect(url_for('home'))
            
        except Exception as e:
            app.logger.error(f"Add account error: {str(e)}")
            flash('An error occurred while adding the account.', 'error')
    
    return render_template('add_account.html')

# Update account balance
@app.route("/update_balance/<int:account_id>", methods=['POST'])
@login_required
def update_balance(account_id):
    new_balance_str = request.form.get('new_balance', '')
    
    if not validate_amount(new_balance_str):
        flash('Please enter a valid balance amount.', 'error')
        return redirect(url_for('home'))
    
    new_balance = float(new_balance_str)
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE user_accounts SET balance = %s WHERE id = %s AND userid = %s', 
                      (new_balance, account_id, session['id']))
        
        if cursor.rowcount > 0:
            mysql.connection.commit()
            flash('Balance updated successfully!', 'success')
        else:
            flash('Account not found or you do not have permission to update it.', 'error')
        
        cursor.close()
        
    except Exception as e:
        app.logger.error(f"Update balance error: {str(e)}")
        flash('An error occurred while updating the balance.', 'error')
    
    return redirect(url_for('home'))

# Delete account
@app.route("/delete_account/<int:account_id>", methods=['POST'])
@login_required
def delete_account(account_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM user_accounts WHERE id = %s AND userid = %s', 
                      (account_id, session['id']))
        
        if cursor.rowcount > 0:
            mysql.connection.commit()
            flash('Account deleted successfully!', 'success')
        else:
            flash('Account not found or you do not have permission to delete it.', 'error')
        
        cursor.close()
        
    except Exception as e:
        app.logger.error(f"Delete account error: {str(e)}")
        flash('An error occurred while deleting the account.', 'error')
    
    return redirect(url_for('home'))

# API endpoint for chart data
@app.route("/api/expense_data")
@login_required
def expense_data():
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute('''SELECT DATE(date) as expense_date, SUM(amount) as daily_total 
                         FROM expenses WHERE userid = %s 
                         AND date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                         GROUP BY DATE(date) ORDER BY DATE(date)''', (session['id'],))
        
        data = cursor.fetchall()
        cursor.close()
        
        labels = [str(row[0]) for row in data]
        amounts = [float(row[1]) for row in data]
        
        return jsonify({
            'labels': labels,
            'data': amounts
        })
        
    except Exception as e:
        app.logger.error(f"Expense data API error: {str(e)}")
        return jsonify({'error': 'Failed to load expense data'}), 500

# LIMIT FUNCTIONALITY
@app.route("/limit")
@login_required
def limit():
    return redirect(url_for('limitn'))

@app.route("/limitnum", methods=['POST'])
@login_required
def limitnum():
    if request.method == "POST":
        number_str = request.form.get('number', '')
        
        if not validate_amount(number_str):
            flash('Please enter a valid limit amount.', 'error')
            return redirect(url_for('limitn'))
        
        number = float(number_str)
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO limitss (user_id, limits) VALUES (%s, %s)', (session['id'], number))
            mysql.connection.commit()
            cursor.close()
            flash('Budget limit set successfully!', 'success')
            
        except Exception as e:
            app.logger.error(f"Set limit error: {str(e)}")
            flash('An error occurred while setting the limit.', 'error')
        
        return redirect(url_for('limitn'))

@app.route("/limitn")
@login_required
def limitn():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT limits FROM limitss WHERE user_id = %s ORDER BY id DESC LIMIT 1', (session['id'],))
        result = cursor.fetchone()
        cursor.close()
        
        limit_amount = result[0] if result else 0
        return render_template("limit.html", y=limit_amount)
        
    except Exception as e:
        app.logger.error(f"Limit display error: {str(e)}")
        flash('An error occurred while loading the limit.', 'error')
        return redirect(url_for('home'))

# REPORT FUNCTIONS
@app.route("/today")
@login_required
def today():
    try:
        cursor = mysql.connection.cursor()
        
        # Get today's expenses with time
        cursor.execute('SELECT TIME(date), amount FROM expenses WHERE userid = %s AND DATE(date) = DATE(NOW())', (session['id'],))
        texpense = cursor.fetchall()
        
        # Get all today's expenses
        cursor.execute('SELECT * FROM expenses WHERE userid = %s AND DATE(date) = DATE(NOW()) ORDER BY date DESC', (session['id'],))
        expense = cursor.fetchall()
        
        # Calculate totals by category
        total = 0
        t_food = t_entertainment = t_business = t_rent = t_EMI = t_other = 0
        
        for x in expense:
            total += x[4]  # amount is at index 4
            category = x[6]  # category is at index 6
            if category == "food":
                t_food += x[4]
            elif category == "entertainment":
                t_entertainment += x[4]
            elif category == "business":
                t_business += x[4]
            elif category == "rent":
                t_rent += x[4]
            elif category == "EMI":
                t_EMI += x[4]
            elif category == "other":
                t_other += x[4]
        
        cursor.close()
        
        return render_template("today.html", 
                             texpense=texpense, expense=expense, total=total,
                             t_food=t_food, t_entertainment=t_entertainment,
                             t_business=t_business, t_rent=t_rent, 
                             t_EMI=t_EMI, t_other=t_other)
                             
    except Exception as e:
        app.logger.error(f"Today report error: {str(e)}")
        flash('An error occurred while loading today\'s report.', 'error')
        return redirect(url_for('home'))

@app.route("/month")
@login_required
def month():
    try:
        cursor = mysql.connection.cursor()
        
        # Get this month's expenses by date
        cursor.execute('SELECT DATE(date), SUM(amount) FROM expenses WHERE userid = %s AND MONTH(DATE(date)) = MONTH(now()) GROUP BY DATE(date) ORDER BY DATE(date)', (session['id'],))
        texpense = cursor.fetchall()
        
        # Get all this month's expenses
        cursor.execute('SELECT * FROM expenses WHERE userid = %s AND MONTH(DATE(date)) = MONTH(now()) ORDER BY date DESC', (session['id'],))
        expense = cursor.fetchall()
        
        # Calculate totals by category
        total = 0
        t_food = t_entertainment = t_business = t_rent = t_EMI = t_other = 0
        
        for x in expense:
            total += x[4]
            category = x[6]
            if category == "food":
                t_food += x[4]
            elif category == "entertainment":
                t_entertainment += x[4]
            elif category == "business":
                t_business += x[4]
            elif category == "rent":
                t_rent += x[4]
            elif category == "EMI":
                t_EMI += x[4]
            elif category == "other":
                t_other += x[4]
        
        cursor.close()
        
        return render_template("today.html", 
                             texpense=texpense, expense=expense, total=total,
                             t_food=t_food, t_entertainment=t_entertainment,
                             t_business=t_business, t_rent=t_rent, 
                             t_EMI=t_EMI, t_other=t_other)
                             
    except Exception as e:
        app.logger.error(f"Month report error: {str(e)}")
        flash('An error occurred while loading this month\'s report.', 'error')
        return redirect(url_for('home'))

@app.route("/year")
@login_required
def year():
    try:
        cursor = mysql.connection.cursor()
        
        # Get this year's expenses by month
        cursor.execute('SELECT MONTH(date), SUM(amount) FROM expenses WHERE userid = %s AND YEAR(DATE(date)) = YEAR(now()) GROUP BY MONTH(date) ORDER BY MONTH(date)', (session['id'],))
        texpense = cursor.fetchall()
        
        # Get all this year's expenses
        cursor.execute('SELECT * FROM expenses WHERE userid = %s AND YEAR(DATE(date)) = YEAR(now()) ORDER BY date DESC', (session['id'],))
        expense = cursor.fetchall()
        
        # Calculate totals by category
        total = 0
        t_food = t_entertainment = t_business = t_rent = t_EMI = t_other = 0
        
        for x in expense:
            total += x[4]
            category = x[6]
            if category == "food":
                t_food += x[4]
            elif category == "entertainment":
                t_entertainment += x[4]
            elif category == "business":
                t_business += x[4]
            elif category == "rent":
                t_rent += x[4]
            elif category == "EMI":
                t_EMI += x[4]
            elif category == "other":
                t_other += x[4]
        
        cursor.close()
        
        return render_template("today.html", 
                             texpense=texpense, expense=expense, total=total,
                             t_food=t_food, t_entertainment=t_entertainment,
                             t_business=t_business, t_rent=t_rent, 
                             t_EMI=t_EMI, t_other=t_other)
                             
    except Exception as e:
        app.logger.error(f"Year report error: {str(e)}")
        flash('An error occurred while loading this year\'s report.', 'error')
        return redirect(url_for('home'))

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('add'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=False)  # Set debug=False for production

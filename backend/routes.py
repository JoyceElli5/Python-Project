from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
from backend.dashboard_data import (
    get_dashboard_data, get_chart_data, get_user_profile, get_user_by_username,
    create_user, update_user_profile, update_last_login,
    add_account, update_account, delete_account,
    add_budget, update_budget,
    add_savings_goal, update_savings_goal,
    add_category, get_user_categories, get_user_accounts, 
    get_user_budgets, get_user_savings_goals
)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route('/')
@app.route('/home')
def home():
    """Dashboard home page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    dashboard_data = get_dashboard_data(user_id)
    
    return render_template('home.html', dashboard_data=dashboard_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            update_last_login(user['id'])
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form.get('full_name')
        
        # Check if user already exists
        if get_user_by_username(username):
            flash('Username already exists', 'error')
            return render_template('signup.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        user_id = create_user(username, email, password_hash, full_name)
        
        # Create default categories
        default_categories = [
            ('Food & Dining', 'fas fa-utensils', '#ef4444', 800),
            ('Transportation', 'fas fa-car', '#3b82f6', 500),
            ('Entertainment', 'fas fa-film', '#8b5cf6', 300),
            ('Bills & Utilities', 'fas fa-file-invoice', '#f59e0b', 1200),
            ('Shopping', 'fas fa-shopping-bag', '#10b981', 600),
            ('Health & Fitness', 'fas fa-heartbeat', '#ec4899', 400)
        ]
        
        for name, icon, color, budget in default_categories:
            add_category(user_id, name, icon, color, budget)
        
        # Create default monthly budget
        today = datetime.now()
        period_start = today.replace(day=1).strftime('%Y-%m-%d')
        period_end = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        add_budget(user_id, 'monthly', 5000, period_start, period_end.strftime('%Y-%m-%d'))
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Account management routes
@app.route('/accounts/add', methods=['GET', 'POST'])
def add_account_route():
    """Add new account"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        account_name = request.form['account_name']
        account_type = request.form['account_type']
        balance = float(request.form['balance'])
        account_number = request.form['account_number']
        
        add_account(session['user_id'], account_name, account_type, balance, account_number)
        flash('Account added successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('add_account.html')

@app.route('/accounts/edit/<int:account_id>', methods=['GET', 'POST'])
def edit_account_route(account_id):
    """Edit account"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        account_name = request.form['account_name']
        balance = float(request.form['balance'])
        
        update_account(account_id, session['user_id'], 
                      account_name=account_name, balance=balance)
        flash('Account updated successfully!', 'success')
        return redirect(url_for('home'))
    
    # Get account details for form
    accounts = get_user_accounts(session['user_id'])
    account = next((acc for acc in accounts if acc['id'] == account_id), None)
    
    if not account:
        flash('Account not found', 'error')
        return redirect(url_for('home'))
    
    return render_template('edit_account.html', account=account)

# Budget management routes
@app.route('/budgets/manage')
def manage_budgets():
    """Manage budgets"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    budgets = get_user_budgets(session['user_id'])
    categories = get_user_categories(session['user_id'])
    
    return render_template('manage_budgets.html', budgets=budgets, categories=categories)

@app.route('/budgets/add', methods=['POST'])
def add_budget_route():
    """Add new budget"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    budget_type = request.form['budget_type']
    amount = float(request.form['amount'])
    category_id = request.form.get('category_id') or None
    
    # Calculate period dates based on budget type
    today = datetime.now()
    if budget_type == 'monthly':
        period_start = today.replace(day=1)
        period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif budget_type == 'weekly':
        period_start = today - timedelta(days=today.weekday())
        period_end = period_start + timedelta(days=6)
    else:  # yearly
        period_start = today.replace(month=1, day=1)
        period_end = today.replace(month=12, day=31)
    
    add_budget(session['user_id'], budget_type, amount, 
               period_start.strftime('%Y-%m-%d'), period_end.strftime('%Y-%m-%d'), category_id)
    
    flash('Budget added successfully!', 'success')
    return redirect(url_for('manage_budgets'))

# Savings goal management routes
@app.route('/savings/manage')
def manage_savings():
    """Manage savings goals"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    goals = get_user_savings_goals(session['user_id'])
    return render_template('manage_savings.html', goals=goals)

@app.route('/savings/add', methods=['POST'])
def add_savings_route():
    """Add new savings goal"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    goal_name = request.form['goal_name']
    target_amount = float(request.form['target_amount'])
    current_amount = float(request.form.get('current_amount', 0))
    target_date = request.form.get('target_date') or None
    description = request.form.get('description') or None
    
    add_savings_goal(session['user_id'], goal_name, target_amount, 
                    current_amount, target_date, description)
    
    flash('Savings goal added successfully!', 'success')
    return redirect(url_for('manage_savings'))

@app.route('/savings/update/<int:goal_id>', methods=['POST'])
def update_savings_route(goal_id):
    """Update savings goal progress"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_amount = float(request.form['current_amount'])
    update_savings_goal(goal_id, session['user_id'], current_amount=current_amount)
    
    flash('Savings goal updated!', 'success')
    return redirect(url_for('manage_savings'))

# Category management routes
@app.route('/categories/manage')
def manage_categories():
    """Manage categories"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    categories = get_user_categories(session['user_id'])
    return render_template('manage_categories.html', categories=categories)

@app.route('/categories/add', methods=['POST'])
def add_category_route():
    """Add new category"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form['name']
    icon = request.form.get('icon', 'fas fa-tag')
    color = request.form.get('color', '#6366f1')
    budget_limit = float(request.form.get('budget_limit', 0))
    
    add_category(session['user_id'], name, icon, color, budget_limit)
    flash('Category added successfully!', 'success')
    return redirect(url_for('manage_categories'))

# API routes
@app.route('/api/chart-data')
def api_chart_data():
    """API endpoint for chart data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    period = int(request.args.get('period', 7))
    data = get_chart_data(session['user_id'], period)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

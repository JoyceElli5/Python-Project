from datetime import datetime, timedelta
from decimal import Decimal
import sqlite3
from flask import session

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('moneytrack.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_dashboard_data(user_id):
    """Fetch all dashboard data for a user"""
    conn = get_db_connection()
    
    # Get total balance across all accounts
    total_balance = conn.execute(
        'SELECT SUM(balance) as total FROM accounts WHERE user_id = ? AND is_active = 1',
        (user_id,)
    ).fetchone()['total'] or 0
    
    # Get current month expenses
    current_month = datetime.now().strftime('%Y-%m')
    monthly_expenses = conn.execute(
        '''SELECT SUM(amount) as total FROM transactions 
           WHERE user_id = ? AND transaction_type = 'expense' 
           AND strftime('%Y-%m', transaction_date) = ?''',
        (user_id, current_month)
    ).fetchone()['total'] or 0
    
    # Get previous month expenses for comparison
    previous_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
    previous_monthly_expenses = conn.execute(
        '''SELECT SUM(amount) as total FROM transactions 
           WHERE user_id = ? AND transaction_type = 'expense' 
           AND strftime('%Y-%m', transaction_date) = ?''',
        (user_id, previous_month)
    ).fetchone()['total'] or 0
    
    # Calculate expense change percentage
    expense_change = 0
    if previous_monthly_expenses > 0:
        expense_change = ((monthly_expenses - previous_monthly_expenses) / previous_monthly_expenses) * 100
    
    # Get previous month balance for comparison
    previous_month_balance = conn.execute(
        '''SELECT SUM(balance) as total FROM accounts 
           WHERE user_id = ? AND is_active = 1''',
        (user_id,)
    ).fetchone()['total'] or 0
    
    # Calculate balance change (simplified - in real app you'd track historical balances)
    balance_change = 2.5 if total_balance > previous_month_balance else -1.2
    
    # Get monthly budget
    monthly_budget = conn.execute(
        '''SELECT amount FROM budgets 
           WHERE user_id = ? AND budget_type = 'monthly' 
           AND is_active = 1 ORDER BY created_at DESC LIMIT 1''',
        (user_id,)
    ).fetchone()
    monthly_limit = monthly_budget['amount'] if monthly_budget else 5000
    
    # Calculate budget utilization
    budget_utilization = (monthly_expenses / monthly_limit * 100) if monthly_limit > 0 else 0
    
    # Get savings goal progress
    savings_goal = conn.execute(
        '''SELECT target_amount, current_amount FROM savings_goals 
           WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1''',
        (user_id,)
    ).fetchone()
    
    if savings_goal:
        savings_percentage = int((savings_goal['current_amount'] / savings_goal['target_amount']) * 100)
        savings_current = savings_goal['current_amount']
        savings_target = savings_goal['target_amount']
    else:
        savings_percentage = 0
        savings_current = 0
        savings_target = 10000
    
    # Get payment cards/accounts
    accounts = conn.execute(
        '''SELECT id, account_name, account_type, balance, account_number 
           FROM accounts WHERE user_id = ? AND is_active = 1 ORDER BY balance DESC''',
        (user_id,)
    ).fetchall()
    
    # Get recent transactions (last 10)
    recent_transactions = conn.execute(
        '''SELECT t.amount, t.description, t.merchant, t.transaction_date, 
                  t.created_at, c.name as category, c.icon
           FROM transactions t
           LEFT JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ? AND t.transaction_type = 'expense'
           ORDER BY t.created_at DESC LIMIT 10''',
        (user_id,)
    ).fetchall()
    
    # Get category spending for current month
    category_spending = conn.execute(
        '''SELECT c.name, c.color, c.icon, c.budget_limit, 
                  COALESCE(SUM(t.amount), 0) as spent
           FROM categories c
           LEFT JOIN transactions t ON c.id = t.category_id 
           AND t.user_id = ? AND t.transaction_type = 'expense'
           AND strftime('%Y-%m', t.transaction_date) = ?
           WHERE c.user_id = ? AND c.is_active = 1
           GROUP BY c.id, c.name, c.color, c.icon, c.budget_limit
           ORDER BY spent DESC''',
        (user_id, current_month, user_id)
    ).fetchall()
    
    # Calculate overall budget utilization
    total_category_budget = sum([cat['budget_limit'] for cat in category_spending])
    total_category_spent = sum([cat['spent'] or 0 for cat in category_spending])
    overall_budget_utilization = int((total_category_spent / total_category_budget * 100)) if total_category_budget > 0 else 0
    
    # Get last 7 days spending for chart
    chart_data = []
    chart_labels = []
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        date_str = date.strftime('%Y-%m-%d')
        daily_spending = conn.execute(
            '''SELECT SUM(amount) as total FROM transactions 
               WHERE user_id = ? AND transaction_type = 'expense' 
               AND transaction_date = ?''',
            (user_id, date_str)
        ).fetchone()['total'] or 0
        chart_data.append(float(daily_spending))
        chart_labels.append(date.strftime('%d %b'))
    
    conn.close()
    
    return {
        'total_balance': float(total_balance),
        'balance_change': balance_change,
        'monthly_expenses': float(monthly_expenses),
        'expense_change': expense_change,
        'monthly_limit': float(monthly_limit),
        'budget_utilization': int(budget_utilization),
        'savings_percentage': savings_percentage,
        'savings_current': float(savings_current),
        'savings_target': float(savings_target),
        'accounts': [dict(account) for account in accounts],
        'recent_transactions': [dict(transaction) for transaction in recent_transactions],
        'category_spending': [dict(category) for category in category_spending],
        'chart_data': chart_data,
        'chart_labels': chart_labels
    }

def get_chart_data(user_id, period=7):
    """Get chart data for specified period"""
    conn = get_db_connection()
    
    chart_data = []
    chart_labels = []
    
    for i in range(period):
        date = datetime.now() - timedelta(days=period-1-i)
        date_str = date.strftime('%Y-%m-%d')
        daily_spending = conn.execute(
            '''SELECT SUM(amount) as total FROM transactions 
               WHERE user_id = ? AND transaction_type = 'expense' 
               AND transaction_date = ?''',
            (user_id, date_str)
        ).fetchone()['total'] or 0
        chart_data.append(float(daily_spending))
        
        if period <= 7:
            chart_labels.append(date.strftime('%d %b'))
        elif period <= 30:
            chart_labels.append(date.strftime('%d/%m'))
        else:
            chart_labels.append(date.strftime('%b %Y'))
    
    conn.close()
    
    return {
        'data': chart_data,
        'labels': chart_labels
    }

# Account management functions
def add_account(user_id, account_name, account_type, balance, account_number):
    """Add new account for user"""
    conn = get_db_connection()
    cursor = conn.execute(
        '''INSERT INTO accounts (user_id, account_name, account_type, balance, account_number) 
           VALUES (?, ?, ?, ?, ?)''',
        (user_id, account_name, account_type, balance, account_number)
    )
    account_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return account_id

def update_account(account_id, user_id, **kwargs):
    """Update account information"""
    conn = get_db_connection()
    
    fields = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            fields.append(f"{key} = ?")
            values.append(value)
    
    if fields:
        query = f"UPDATE accounts SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?"
        values.extend([account_id, user_id])
        conn.execute(query, values)
        conn.commit()
    
    conn.close()
    return True

def delete_account(account_id, user_id):
    """Delete account"""
    conn = get_db_connection()
    conn.execute(
        'UPDATE accounts SET is_active = 0 WHERE id = ? AND user_id = ?',
        (account_id, user_id)
    )
    conn.commit()
    conn.close()
    return True

# Budget management functions
def add_budget(user_id, budget_type, amount, period_start, period_end, category_id=None):
    """Add new budget"""
    conn = get_db_connection()
    cursor = conn.execute(
        '''INSERT INTO budgets (user_id, category_id, budget_type, amount, period_start, period_end) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, category_id, budget_type, amount, period_start, period_end)
    )
    budget_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return budget_id

def update_budget(budget_id, user_id, **kwargs):
    """Update budget"""
    conn = get_db_connection()
    
    fields = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            fields.append(f"{key} = ?")
            values.append(value)
    
    if fields:
        query = f"UPDATE budgets SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
        values.extend([budget_id, user_id])
        conn.execute(query, values)
        conn.commit()
    
    conn.close()
    return True

# Savings goal management functions
def add_savings_goal(user_id, goal_name, target_amount, current_amount=0, target_date=None, description=None):
    """Add new savings goal"""
    conn = get_db_connection()
    cursor = conn.execute(
        '''INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date, description) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, goal_name, target_amount, current_amount, target_date, description)
    )
    goal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return goal_id

def update_savings_goal(goal_id, user_id, **kwargs):
    """Update savings goal"""
    conn = get_db_connection()
    
    fields = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            fields.append(f"{key} = ?")
            values.append(value)
    
    if fields:
        query = f"UPDATE savings_goals SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?"
        values.extend([goal_id, user_id])
        conn.execute(query, values)
        conn.commit()
    
    conn.close()
    return True

# Category management functions
def add_category(user_id, name, icon='fas fa-tag', color='#6366f1', budget_limit=0):
    """Add new category"""
    conn = get_db_connection()
    cursor = conn.execute(
        '''INSERT INTO categories (user_id, name, icon, color, budget_limit) 
           VALUES (?, ?, ?, ?, ?)''',
        (user_id, name, icon, color, budget_limit)
    )
    category_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return category_id

def get_user_categories(user_id):
    """Get all categories for user"""
    conn = get_db_connection()
    categories = conn.execute(
        'SELECT * FROM categories WHERE user_id = ? AND is_active = 1 ORDER BY name',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(category) for category in categories]

def get_user_accounts(user_id):
    """Get all accounts for user"""
    conn = get_db_connection()
    accounts = conn.execute(
        'SELECT * FROM accounts WHERE user_id = ? AND is_active = 1 ORDER BY account_name',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(account) for account in accounts]

def get_user_budgets(user_id):
    """Get all budgets for user"""
    conn = get_db_connection()
    budgets = conn.execute(
        '''SELECT b.*, c.name as category_name FROM budgets b
           LEFT JOIN categories c ON b.category_id = c.id
           WHERE b.user_id = ? AND b.is_active = 1 
           ORDER BY b.created_at DESC''',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(budget) for budget in budgets]

def get_user_savings_goals(user_id):
    """Get all savings goals for user"""
    conn = get_db_connection()
    goals = conn.execute(
        'SELECT * FROM savings_goals WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(goal) for goal in goals]

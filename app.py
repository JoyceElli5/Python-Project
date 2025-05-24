from flask import Flask, render_template, request, redirect, session, flash, url_for 
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'a'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123jklasdf$'
app.config['MYSQL_DB'] = 'expense_tracker'

mysql = MySQL(app)

# ===== DATABASE MODELS ===== #
def init_db_tables():
    """Initialize database tables if they don't exist"""
    try:
        cursor = mysql.connection.cursor()
        
        # Create limits table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS `limits` (
                `id` INT NOT NULL AUTO_INCREMENT,
                `userid` INT NOT NULL,
                `limitss` DECIMAL(10,2) NOT NULL,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                FOREIGN KEY (`userid`) REFERENCES `register`(`id`) ON DELETE CASCADE,
                INDEX `userid_idx` (`userid`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        ''')
        mysql.connection.commit()
    except Exception as e:
        print(f"Error initializing database tables: {str(e)}")
        # If foreign key fails, create without foreign key constraint
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS `limits` (
                `id` INT NOT NULL AUTO_INCREMENT,
                `userid` INT NOT NULL,
                `limitss` DECIMAL(10,2) NOT NULL,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                INDEX `userid_idx` (`userid`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        ''')
        mysql.connection.commit()

# Initialize tables when app starts
with app.app_context():
    try:
        init_db_tables()
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database tables: {str(e)}")


# ===== ENHANCEMENTS ===== #
def get_user_balance(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT SUM(amount) FROM expenses WHERE userid = %s', (user_id,))
    total = cursor.fetchone()[0] or 0
    return total

def get_recent_expenses(user_id, limit=5):
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT expensename, amount, date, category 
        FROM expenses 
        WHERE userid = %s 
        ORDER BY date DESC 
        LIMIT %s
    ''', (user_id, limit))
    return cursor.fetchall()

def get_category_totals(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT category, SUM(amount) 
        FROM expenses 
        WHERE userid = %s 
        GROUP BY category
    ''', (user_id,))
    return {category: amount for category, amount in cursor.fetchall()}
def get_current_limit(user_id):
    """Get the current active limit for a user"""
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT limitss FROM limits 
        WHERE userid = %s 
        ORDER BY created_at DESC LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    return float(result[0]) if result else None

def get_monthly_spending(user_id):
    """Get total spending for current month"""
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) 
        FROM expenses 
        WHERE userid = %s 
        AND MONTH(date) = MONTH(CURRENT_DATE())
        AND YEAR(date) = YEAR(CURRENT_DATE())
    ''', (user_id,))
    return float(cursor.fetchone()[0])
# ===== END ENHANCEMENTS ===== #

@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect('/home')
    return redirect('/signup')  # Redirect to sign-up page if not logged in


# HOME PAGE - ENHANCED
@app.route('/home')
def home():
    if 'loggedin' not in session:
        return redirect('/signin')
    
    user_id = session['id']
    
    # Initialize all values to 0 for new users
    balance = 0
    recent_expenses = []
    category_totals = {}
    
    # Only query if user might have data
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM expenses WHERE userid = %s', (user_id,))
    has_expenses = cursor.fetchone()[0] > 0
    
    if has_expenses:
        balance = get_user_balance(user_id)
        recent_expenses = get_recent_expenses(user_id)
        category_totals = get_category_totals(user_id)
    
    return render_template("homepage.html",
                         balance=balance,
                         recent_expenses=recent_expenses,
                         category_totals=category_totals,
                         empty_state=not has_expenses)
#SIGN--UP--OR--REGISTER


@app.route('/signup')
def signup():
    if 'loggedin' in session:
        return redirect('/home')
    return render_template('signup.html')



@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM register WHERE username = % s', (username, ))
        account = cursor.fetchone()
        print(account)
        if account:
            flash ('Account already exists !', "error")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash ( 'Invalid email address !', "error")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('name must contain only characters and numbers', "error")
        else:
            cursor.execute('INSERT INTO register VALUES (NULL, % s, % s, % s)', (username, email,password))
            mysql.connection.commit()
            flash('You have successfully registered !',"success")
            return redirect('/signin')  
        
    return render_template('signup.html')    
        
        
 
        
 #LOGIN--PAGE
    
@app.route("/signin")
def signin():
    return render_template("login.html")
        
@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
   
  
    if request.method == 'POST' :
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM register WHERE email = % s AND password = % s', (email, password ),)
        account = cursor.fetchone()
        print (account)
        
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid=  account[0]
            session['email'] = account[1]
            session['username'] = account[1]
            flash("login successful","success")
            return redirect('/home')
        else:
            flash("invalid credentials","error")
    return render_template('login.html', msg = msg)



       





#ADDING----DATA


@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    
    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']
    
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO expenses VALUES (NULL,  % s, % s, % s, % s, % s, % s)', (session['id'] ,date, expensename, amount, paymode, category))
    mysql.connection.commit()
    print(date + " " + expensename + " " + amount + " " + paymode + " " + category)
    
    return redirect("/display")



#DISPLAY---graph 

@app.route("/display")
def display():
    print(session["username"],session['id'])
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM expenses WHERE userid = % s AND date ORDER BY `expenses`.`date` DESC',(str(session['id'])))
    expense = cursor.fetchall()
  
       
    return render_template('display.html' ,expense = expense)
                          



#delete---the--data

@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete(id):
     cursor = mysql.connection.cursor()
     cursor.execute('DELETE FROM expenses WHERE  id = {0}'.format(id))
     mysql.connection.commit()
     print('deleted successfully')    
     return redirect("/display")
 
    
#UPDATE---DATA

@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM expenses WHERE  id = %s', (id,))
    row = cursor.fetchall()
   
    print(row[0])
    return render_template('edit.html', expenses = row[0])




@app.route('/update/<id>', methods = ['POST'])
def update(id):
  if request.method == 'POST' :
   
      date = request.form['date']
      expensename = request.form['expensename']
      amount = request.form['amount']
      paymode = request.form['paymode']
      category = request.form['category']
    
      cursor = mysql.connection.cursor()
       
      cursor.execute("UPDATE `expenses` SET `date` = % s , `expensename` = % s , `amount` = % s, `paymode` = % s, `category` = % s WHERE `expenses`.`id` = % s ",(date, expensename, amount, str(paymode), str(category),id))
      mysql.connection.commit()
      print('successfully updated')
      return redirect("/display")
     
      
@app.route("/limit")
def limit():
    if 'loggedin' not in session:
        return redirect('/signin')
    
    debug_info = {}  # For troubleshooting
    try:
        user_id = session['id']
        debug_info['user_id'] = user_id
        
        # 1. Get current limit
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT limitss FROM limits WHERE userid = %s ORDER BY id DESC LIMIT 1', (user_id,))
        limit_data = cursor.fetchone()
        current_limit = float(limit_data[0]) if limit_data else None
        debug_info['raw_limit_data'] = limit_data
        debug_info['current_limit'] = current_limit
        
        # 2. Get current month spending
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM expenses 
            WHERE userid = %s 
            AND MONTH(date) = MONTH(CURRENT_DATE())
            AND YEAR(date) = YEAR(CURRENT_DATE())
        ''', (user_id,))
        spending_data = cursor.fetchone()
        total_spent = float(spending_data[0]) if spending_data else 0
        debug_info['spending_data'] = spending_data
        debug_info['total_spent'] = total_spent
        
        # 3. Calculate metrics
        if current_limit and current_limit > 0:
            usage_percent = min((total_spent / current_limit) * 100, 100)
            remaining = max(current_limit - total_spent, 0)
        else:
            usage_percent = 0
            remaining = 0
        
        debug_info['final_values'] = {
            'current_limit': current_limit,
            'total_spent': total_spent,
            'usage_percent': usage_percent,
            'remaining': remaining
        }
        
        print("DEBUG INFO:", debug_info)  # Check Flask console
        
        return render_template("limit.html",
                            current_limit=current_limit,
                            total_spent=total_spent,
                            usage_percent=usage_percent,
                            remaining=remaining,
                            debug=debug_info)  # Pass debug info to template
        
    except Exception as e:
        print(f"ERROR in /limit: {str(e)}")
        return render_template("limit.html",
                            current_limit=None,
                            total_spent=0,
                            usage_percent=0,
                            remaining=0,
                            error=str(e))
    
@app.route("/set_limit", methods=['POST'])
def set_limit():
    if 'loggedin' not in session:
        return redirect('/signin')
    
    try:
        limit_input = request.form.get('limit_amount')
        print(f"Received limit_amount: {limit_input}")
        
        new_limit = float(limit_input)
        if new_limit <= 0:
            flash("Limit must be greater than 0", "error")
            return redirect('/limit')
        
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO limits (userid, limitss) VALUES (%s, %s)",
            (session['id'], new_limit)
        )
        mysql.connection.commit()
        
        flash("Budget limit set successfully!", "success")
    except ValueError as ve:
        print(f"ValueError in set_limit: {str(ve)}")
        flash("Please enter a valid number", "error")
    except Exception as e:
        print(f"Unexpected error in set_limit: {str(e)}")
        flash("Error setting budget limit", "error")
    
    return redirect('/limit')


# Update the test_set_limit route as well
@app.route('/test_set_limit')
def test_set_limit():
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO limits (userid, limitss) VALUES (%s, %s)', 
                  (session['id'], 1000.00))
    mysql.connection.commit()
    return "Test limit set to 1000.00"
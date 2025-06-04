from flask import Flask, render_template, request, redirect, session, flash, url_for 
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json
from datetime import datetime, timedelta
from flask import jsonify



app = Flask(__name__)


app.secret_key = 'a'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '918273645'
app.config['MYSQL_DB'] = 'expense_tracker'


mysql = MySQL(app)


#HOME--PAGE
@app.route("/home")
def home():
    if 'loggedin' not in session:
        return redirect('/signin')
    
    # Get user's payment methods
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM payment_methods WHERE user_id = %s', (session['id'],))
    payment_methods = cursor.fetchall()
    
    # If no payment methods, initialize with empty list
    if not payment_methods:
        payment_methods = []
    
    # Get total balance from all payment methods
    total_balance = sum(float(method['balance']) for method in payment_methods) if payment_methods else 0
    
    # Get total expenses for current month
    cursor.execute('''
        SELECT SUM(amount) as total_expenses 
        FROM expenses 
        WHERE userid = %s AND MONTH(date) = MONTH(CURRENT_DATE()) AND YEAR(date) = YEAR(CURRENT_DATE())
    ''', (session['id'],))
    result = cursor.fetchone()
    total_expenses = float(result['total_expenses']) if result['total_expenses'] else 0
    
    # For demo purposes, set income as balance + expenses
    total_income = total_balance + total_expenses
    
    # Get budget limit
    cursor.execute('SELECT limits FROM limitss WHERE id = (SELECT MAX(id) FROM limitss WHERE user_id = %s)', (session['id'],))
    limit_result = cursor.fetchone()
    budget_limit = float(limit_result['limits']) if limit_result and limit_result['limits'] else 0

    # Get recent transactions
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
        get_category_icon=get_category_icon
    )

@app.route("/")
def add():
    return render_template("index.html")



#SIGN--UP--OR--REGISTER


@app.route("/signup")
def signup():
    return render_template("signup.html")



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

@app.route('/login', methods=['GET', 'POST'])
def login():
    global userid
    msg = ''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            connection = mysql.connection
            if connection is None:
                flash("Database connection failed", "error")
                return render_template('login.html', msg=msg)

            cursor = connection.cursor()
            cursor.execute('SELECT * FROM register WHERE email = %s AND password = %s', (email, password))
            account = cursor.fetchone()
            print(account)

            if account:
                session['loggedin'] = True
                session['id'] = account[0]
                userid = account[0]
                session['email'] = account[1]
                session['username'] = account[1]
                flash("Login successful", "success")
                return redirect('/home')
            else:
                flash("Invalid credentials", "error")

        except Exception as e:
            print("MySQL Error:", str(e))
            flash("Something went wrong connecting to the database", "error")

    return render_template('login.html', msg=msg)




       





#ADDING----DATA


@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense', methods=['GET', 'POST'])
def addexpense():
    date = request.form['date']
    expensename = request.form['expensename']
    amount = float(request.form['amount'])
    paymode = request.form['paymode']
    category = request.form['category']
    account_id = request.form['account_id']

    # Get latest limit for this user
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT limits FROM limitss WHERE user_id = %s ORDER BY id DESC LIMIT 1', (session['id'],))
    result = cursor.fetchone()

    limit = float(result[0]) if result else None

    # If there's a limit and amount exceeds it
    if limit and amount > limit:
        # Store form data in session temporarily
        session['pending_expense'] = {
            'date': date,
            'expensename': expensename,
            'amount': amount,
            'paymode': paymode,
            'category': category,
            'account_id': account_id
        }
        return render_template('limit_warning.html', amount=amount, limit=limit)

    # Proceed normally if within limit
    cursor.execute(
        'INSERT INTO expenses VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)',
        (session['id'], date, expensename, amount, paymode, category, account_id)
    )
    mysql.connection.commit()

    return redirect("/display")



@app.route('/confirm_expense', methods=['POST'])
def confirm_expense():
    data = session.get('pending_expense')

    if not data:
        return redirect('/add')  # fallback

    cursor = mysql.connection.cursor()
    cursor.execute(
        'INSERT INTO expenses VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)',
        (session['id'], data['date'], data['expensename'], data['amount'],
         data['paymode'], data['category'], data['account_id'])
    )
    mysql.connection.commit()

    session.pop('pending_expense', None)
    return redirect("/display")




#DISPLAY---graph 

@app.route("/display")
def display():
    print(session["username"], session["id"])
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # 👈 DictCursor for dict-like rows
    cursor.execute('SELECT * FROM expenses WHERE userid = %s ORDER BY `expenses`.`date` DESC', (str(session['id']),))
    expense = cursor.fetchall()
    
    return render_template('display.html', expense=expense)



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
def add_payment_method():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    data = request.get_json()
    payment_type = data.get('type')       # 'card' or 'cash'
    name = data.get('name')               # 'Visa Card', 'Wallet', etc.
    balance = data.get('balance')         # 5000.0

    if not all([payment_type, name, balance]):
        return jsonify({'success': False, 'message': 'Missing required fields'})

    try:
        cursor = mysql.connection.cursor()

        # Insert into user_accounts (main account table)
        cursor.execute('''
            INSERT INTO user_accounts (userid, account_name, account_type, balance)
            VALUES (%s, %s, %s, %s)
        ''', (session['id'], name, payment_type, float(balance)))

        # Optionally insert into payment_methods (just for metadata or UI listing)
        cursor.execute('''
            INSERT INTO payment_methods (user_id, type, name, balance)
            VALUES (%s, %s, %s, %s)
        ''', (session['id'], payment_type, name, float(balance)))

        mysql.connection.commit()
        flash("Payment method added sucessfully", "success")
    
    except Exception as e:
        print(e)
        flash("Failed to add payment method", "error")




# Get chart data route
@app.route("/get_chart_data")
def get_chart_data():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    period = request.args.get('period', 'month')
    
    today = datetime.now()
    labels = []
    values = []
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if period == 'week':
        # Last 7 days
        start_date = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        # Generate date labels for the last 7 days
        for i in range(7):
            date = today - timedelta(days=6-i)
            labels.append(date.strftime('%d %b'))
        
        # Get expenses for each day
        cursor.execute(''' 
            SELECT DATE(date) as expense_date, SUM(amount) as total
            FROM expenses
            WHERE userid = %s AND DATE(date) BETWEEN %s AND %s
            GROUP BY DATE(date)
            ORDER BY DATE(date)
        ''', (session['id'], start_date, end_date))
        
        results = cursor.fetchall()
        
        # Create a dictionary of date -> amount
        expense_dict = {result['expense_date'].strftime('%d %b'): float(result['total']) for result in results}
        
        # Fill in values array based on labels
        for label in labels:
            values.append(expense_dict.get(label, 0))
        
    elif period == 'month':
        # Current month
        start_date = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        # Get number of days in current month
        if today.month == 12:
            last_day = datetime(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
        
        days_in_month = last_day.day
        
        # Generate week labels
        for week in range(1, 5):
            labels.append(f'Week {week}')
        
        # Get expenses for each week
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
        
        # Create a dictionary of week -> amount
        expense_dict = {result['week_number']: float(result['total']) for result in results}
        
        # Fill in values array based on labels
        for i in range(1, 5):
            values.append(expense_dict.get(i, 0))
        
    else:  # year
        # Current year
        start_date = datetime(today.year, 1, 1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        # Generate month labels
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        labels = months
        
        # Get expenses for each month
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
        
        # Create a dictionary of month -> amount
        expense_dict = {result['month_number']: float(result['total']) for result in results}
        
        # Fill in values array based on labels
        for i in range(1, 13):
            values.append(expense_dict.get(i, 0))
    
    return jsonify({
        'success': True,
        'labels': labels,
        'values': values,
        'start_date': labels[0] if labels else '',
        'end_date': labels[-1] if labels else ''
    })

# Get transactions by category
@app.route("/get_transactions_by_category")
def get_transactions_by_category():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    category = request.args.get('category', 'all')
    
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
    
    # Format dates for display
    for transaction in transactions:
        if isinstance(transaction['date'], datetime):
            transaction['date'] = transaction['date'].strftime('%d %b, %Y')
    
    return jsonify({
        'success': True,
        'transactions': transactions
    })







@app.route("/add_account", methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        account_name = request.form['account_name']
        account_type = request.form['account_type']  # 'card' or 'cash'
        initial_balance = float(request.form['initial_balance'])
        
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO user_accounts (userid, account_name, account_type, balance) 
                         VALUES (%s, %s, %s, %s)''', 
                      (session['id'], account_name, account_type, initial_balance))
        mysql.connection.commit()
        
        flash('Account added successfully!', 'success')
        return redirect('/dashboard')
    
    return render_template('add_account.html')

# Update account balance
@app.route("/update_balance/<int:account_id>", methods=['POST'])
def update_balance(account_id):
    new_balance = float(request.form['new_balance'])
    
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE user_accounts SET balance = %s WHERE id = %s AND userid = %s', 
                  (new_balance, account_id, session['id']))
    mysql.connection.commit()
    
    flash('Balance updated successfully!', 'success')
    return redirect('/dashboard')

# Delete account
@app.route("/delete_account/<int:account_id>", methods=['POST'])
def delete_account(account_id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM user_accounts WHERE id = %s AND userid = %s', 
                  (account_id, session['id']))
    mysql.connection.commit()
    
    flash('Account deleted successfully!', 'success')
    return redirect('/dashboard')

# API endpoint for chart data
@app.route("/api/expense_data")
def expense_data():
    if 'loggedin' not in session:
        return {'error': 'Not logged in'}, 401
    
    cursor = mysql.connection.cursor()
    
    # Get last 7 days data
    cursor.execute('''SELECT DATE(date) as expense_date, SUM(amount) as daily_total 
                     FROM expenses WHERE userid = %s 
                     AND date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                     GROUP BY DATE(date) ORDER BY DATE(date)''', (session['id'],))
    
    data = cursor.fetchall()
    
    # Format data for Chart.js
    labels = [str(row[0]) for row in data]
    amounts = [float(row[1]) for row in data]
    
    return {
        'labels': labels,
        'data': amounts
    }










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
     
      

            
 
         
    
            
 #limit
@app.route("/limit" )
def limit():
       return redirect('/limitn')

@app.route("/limitnum" , methods = ['POST' ])
def limitnum():
     if request.method == "POST":
         number= request.form['number']
         cursor = mysql.connection.cursor()
         cursor.execute('INSERT INTO limitss VALUES (NULL, % s, % s) ',(session['id'], number))
         mysql.connection.commit()
         return redirect('/limitn')
     
         
@app.route("/limitn") 
def limitn():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT limits FROM `limitss` ORDER BY `limitss`.`id` DESC LIMIT 1')
    x= cursor.fetchone()
    s = x[0]
    
    
    return render_template("limit.html" , y= s)

#REPORT

@app.route("/today")
def today():
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT TIME(date)   , amount FROM expenses  WHERE userid = %s AND DATE(date) = DATE(NOW()) ',(str(session['id']),))
      texpense = cursor.fetchall()
      print(texpense)
      
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT * FROM expenses WHERE userid = % s AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id']),))
      expense = cursor.fetchall()
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
     

@app.route("/month")
def month():
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT DATE(date), SUM(amount) FROM expenses WHERE userid= %s AND MONTH(DATE(date))= MONTH(now()) GROUP BY DATE(date) ORDER BY DATE(date) ',(str(session['id']),))
      texpense = cursor.fetchall()
      print(texpense)
      
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT * FROM expenses WHERE userid = % s AND MONTH(DATE(date))= MONTH(now()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id']),))
      expense = cursor.fetchall()
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
         
@app.route("/year")
def year():
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT MONTH(date), SUM(amount) FROM expenses WHERE userid= %s AND YEAR(DATE(date))= YEAR(now()) GROUP BY MONTH(date) ORDER BY MONTH(date) ',(str(session['id'])))
      texpense = cursor.fetchall()
      print(texpense)
      
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT * FROM expenses WHERE userid = % s AND YEAR(DATE(date))= YEAR(now()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id']),))
      expense = cursor.fetchall()
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

#log-out

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('index.html')

             

if __name__ == "__main__":
    app.run(debug=True)
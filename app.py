from flask import Flask, render_template, request, redirect, session, flash, url_for 
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText




app = Flask(__name__)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value
    return value.strftime(format)



app.secret_key = 'a'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123jklasdf$'
app.config['MYSQL_DB'] = 'expense_tracker'

mysql = MySQL(app)

def send_email(to_email, content):
    from_email = "youremail@gmail.com"
    from_password = "your-email-password"  # Use app password if 2FA is on

    msg = MIMEText(content)
    msg['Subject'] = "Expense Tracker Alert"
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent.")
    except Exception as e:
        print(f"Email failed: {e}")


#HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")

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
        
@app.route('/login',methods =['GET', 'POST'])
def login():
    if request.method == 'POST' :
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM register WHERE email = % s AND password = % s', (email, password ),)
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['email'] = account[2]    # assuming email is in column index 2
            session['username'] = account[1] # username in column index 1
            flash("Login successful","success")
            return redirect('/home')
        else:
            flash("Invalid credentials","error")
    return render_template('login.html')

#ADDING----DATA


@app.route("/add")
def adding():
    user_id = session.get('id')
    has_limit = False

    if user_id:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM limits WHERE userid = %s', (user_id,))
        has_limit = cursor.fetchone()[0] > 0

    return render_template("add.html", has_limit=has_limit)

@app.route('/addexpense', methods=['GET', 'POST'])
def addexpense():
    if request.method == 'POST':
        date = request.form['date']
        expensename = request.form['expensename']
        amount = float(request.form['amount'])
        paymode = request.form['paymode']
        category = request.form['category']
        user_id = session['id']

        # Check if user wants to use previous limit
        use_previous_limit = request.form.get('use_previous_limit') == 'yes'

        # Handle limit setting
        if not use_previous_limit:
            set_limit = request.form.get('set_limit')
            limit_type = request.form.get('limit_type')

            if set_limit and limit_type:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    'INSERT INTO limits (userid, limitss, duration) VALUES (%s, %s, %s)',
                    (user_id, set_limit, limit_type)
                )
                mysql.connection.commit()
                session['has_limit'] = True  # Mark that the user now has a limit
        elif use_previous_limit:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT limitss, duration FROM limits WHERE userid = %s ORDER BY id DESC LIMIT 1', (user_id,))
            limit_data = cursor.fetchone()
            if not limit_data:
                flash("No previous limit found. Please set a new limit.", "error")
                return redirect("/add")
            set_limit = limit_data[0]
            limit_type = limit_data[1]
            session['has_limit'] = True

        # Insert the expense
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO expenses VALUES (NULL, %s, %s, %s, %s, %s, %s)',
                       (user_id, date, expensename, amount, paymode, category))
        mysql.connection.commit()

        # Only check limits if one was set
        if session.get('has_limit') and set_limit and limit_type:
            limit_value = float(set_limit)
            duration = limit_type.lower()

            today = datetime.strptime(date, '%Y-%m-%dT%H:%M')
            if duration == 'daily':
                start_date = today.date()
                end_date = today.date()
            elif duration == 'weekly':
                start_date = (today - timedelta(days=today.weekday())).date()
                end_date = today.date()
            elif duration == 'monthly':
                start_date = today.replace(day=1).date()
                end_date = today.date()
            elif duration == 'yearly':
                start_date = today.replace(month=1, day=1).date()
                end_date = today.date()
            else:
                start_date = today.date()
                end_date = today.date()

            cursor.execute("""
                SELECT SUM(amount) FROM expenses 
                WHERE userid = %s AND DATE(date) BETWEEN %s AND %s
            """, (user_id, start_date, end_date))
            total_spent = cursor.fetchone()[0] or 0

            try:
                if total_spent > limit_value:
                    flash(f"🚨 Limit exceeded! You've spent GH₵{total_spent:.2f} which is over your {duration} limit of GH₵{limit_value:.2f}.", "error")
                    send_email(session['email'], f"🚨 Limit Exceeded: You've spent GH₵{total_spent:.2f} which is over your {duration} limit of GH₵{limit_value:.2f}.")
                elif total_spent >= 0.9 * limit_value:
                    flash(f"⚠️ Warning: You've spent GH₵{total_spent:.2f}, which is 90% of your {duration} limit of GH₵{limit_value:.2f}.", "warning")
                    send_email(session['email'], f"⚠️ Warning: You've spent GH₵{total_spent:.2f}, which is 90% of your {duration} limit of GH₵{limit_value:.2f}.")
                else:
                    flash("Expense added successfully.", "success")
            except Exception as e:
                print(f"Email sending error: {e}")
                flash("Expense added but failed to send email notification.", "warning")
        else:
            flash("Expense added successfully (no limit set).", "success")

        return redirect("/display")

    
@app.route("/check_limit")
def check_limit():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM limits WHERE userid = %s', (session['id'],))
    has_limit = cursor.fetchone()[0] > 0
    
    if has_limit:
        return render_template("add.html", has_existing_limit=True)  # Pass a flag to the template
    return render_template("add.html", has_existing_limit=False)

@app.route("/history")
def history():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM expenses WHERE userid = %s ORDER BY date DESC', (session['id'],))
    expense = cursor.fetchall()
    return render_template('history.html', expense=expense)


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
     
      

                        
 #limit
@app.route("/limit" )
def limit():
       return redirect('/limitn')

@app.route("/limitnum", methods=["POST"])
def limitnum():
    if request.method == "POST":
        number = request.form["number"]
        duration = request.form["limit_type"]  # the select field is still called limit_type in HTML

        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO limits (userid, limitss, duration) VALUES (%s, %s, %s)',
            (session["id"], number, duration)
        )
        mysql.connection.commit()
        return redirect('/limitn')

         
@app.route("/limitn")
def limitn():
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT limitss, duration FROM limits WHERE userid = %s ORDER BY id DESC LIMIT 1',
        (session['id'],)
    )
    x = cursor.fetchone()
    
    if x:
        limit_value = x[0]
        duration = x[1]
    else:
        limit_value = 0
        duration = "Not Set"

    return render_template("limit.html", limit_value=limit_value, limit_type=duration)


#REPORT

@app.route("/today")
def today():
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT TIME(date)   , amount FROM expenses  WHERE userid = %s AND DATE(date) = DATE(NOW()) ',(str(session['id'])))
      texpense = cursor.fetchall()
      print(texpense)
      
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT * FROM expenses WHERE userid = % s AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id'])))
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
      cursor.execute('SELECT DATE(date), SUM(amount) FROM expenses WHERE userid= %s AND MONTH(DATE(date))= MONTH(now()) GROUP BY DATE(date) ORDER BY DATE(date) ',(str(session['id'])))
      texpense = cursor.fetchall()
      print(texpense)
      
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT * FROM expenses WHERE userid = % s AND MONTH(DATE(date))= MONTH(now()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id'])))
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
      cursor.execute('SELECT * FROM expenses WHERE userid = % s AND YEAR(DATE(date))= YEAR(now()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id'])))
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
   return render_template('home.html')

@app.route("/display")
def display():
    return redirect("/history")


             

if __name__ == "__main__":
    app.run(debug=True)
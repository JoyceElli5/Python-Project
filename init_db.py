from app import app, mysql

with app.app_context():
    cursor = mysql.connection.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS register (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        password VARCHAR(100) NOT NULL
    )
    ''')
    
    # Expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        userid INT NOT NULL,
        date DATE NOT NULL,
        expensename VARCHAR(100) NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        paymode VARCHAR(50) NOT NULL,
        category VARCHAR(50) NOT NULL
    )
    ''')
    
    # Budget limits table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS limits (
        id INT AUTO_INCREMENT PRIMARY KEY,
        userid INT NOT NULL,
        limitss DECIMAL(10,2) NOT NULL
    )
    ''')
    
    mysql.connection.commit()
    print("✅ Tables created successfully!")
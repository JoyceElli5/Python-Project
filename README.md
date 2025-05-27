# Money Track

A comprehensive expense tracking web application built with Python Flask that helps users manage their finances effectively.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)

## Features

- User Authentication (Signup/Login)
- Expense Management
  - Add/Edit/Delete expenses
  - Track expenses by category and payment mode
  - Support for multiple currencies
- User Settings
  - Theme customization (White/Dark mode)
  - Currency preferences
- Monthly Spending Limits
  - Set custom monthly spending limits
  - Notifications when approaching/exceeding limits
- Session Management
- Responsive Web Interface

## Project Structure

```
Money-Track/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── expense_tracker.sql    # Database schema
├── sendemail.py          # Email notification handler
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── images/          # Image assets
└── templates/           # HTML templates
    ├── base.html        # Base template
    ├── login.html       # Login page
    ├── register.html    # Registration page
    ├── settings.html    # User settings
    └── add_expense.html # Expense management
```

## Database Schema

The application uses a MySQL database with the following tables:

- `register`
  - id (PK)
  - username
  - email
  - hashed_password

- `user_settings`
  - user_id (FK)
  - theme
  - currency

- `expenses`
  - id (PK)
  - userid (FK)
  - date
  - expensename
  - amount
  - paymode
  - category
  - currency

- `limits`
  - id (PK)
  - userid (FK)
  - limitss (monthly spending limit)

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up MySQL database:
   - Create a database named 'expense_tracker'
   - Import the schema from `expense_tracker.sql`

## Usage

1. Run the application:
   ```
   python app.py
   ```
2. Access the application at `http://localhost:5000`
3. Register a new account or log in with existing credentials
4. Use the dashboard to:
   - Add new expenses
   - View expense history
   - Set monthly spending limits
   - Customize theme and currency preferences

## Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-Login
- MySQL Connector
- Email sending library
- Other web development utilities

## Security Features

- Password hashing for user authentication
- Session management for secure user sessions
- Input validation for form submissions
- Secure database connections
- Protection against SQL injection

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.
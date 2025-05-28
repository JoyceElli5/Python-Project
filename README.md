# Money Track

A comprehensive expense tracking web application built with Python Flask that helps users manage their personal finances effectively. Track expenses, set budgets, and gain insights into your spending habits with an intuitive interface.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### User Authentication
- Secure user registration and login
- Session-based authentication
- Password hashing for security
- Email-based account verification

### Expense Management
- Add, edit, and delete expenses
- Categorize expenses
- Multiple payment modes
- Support for multiple currencies
- Expense history with filtering options
- Export data (CSV/Excel)

### Budgeting & Analytics
- Set monthly spending limits
- Visual expense analytics
- Spending trends and patterns
- Category-wise expense distribution

### User Experience
- Clean, responsive UI
- Light/Dark theme support
- Real-time notifications
- Mobile-friendly interface
- Interactive charts and graphs

## 📁 Project Structure

```
Money-Track/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container configuration
├── expense_tracker.sql       # Database schema
├── sendemail.py              # Email notification handler
│
├── backend/                 # Backend modules
│   └── __init__.py          # Package initialization
│
├── static/                  # Static assets
│   ├── css/                 # Stylesheets
│   │   ├── home.css         # Home page styles
│   │   ├── login.css        # Login page styles
│   │   ├── signup.css       # Signup page styles
│   │   ├── styles.css       # Global styles
│   │   └── dashboard.css    # Dashboard specific styles
│   │
│   ├── js/                  # Client-side scripts
│   │   ├── home.js          # Home page scripts
│   │   ├── landing-script.js # Landing page scripts
│   │   ├── login.js         # Login page scripts
│   │   ├── signup.js        # Signup page scripts
│   │   └── dashboard.js     # Dashboard functionality
│   │
│   └── images/              # Image assets
│       ├── avatars/         # User profile pictures
│       ├── icons/           # Application icons
│       └── screenshots/     # Application screenshots
│
└── templates/               # Jinja2 templates
    ├── base.html           # Base template with common layout
    ├── index.html          # Landing page
    ├── login.html          # Login page
    ├── signup.html         # Registration page
    ├── home.html           # Main dashboard
    ├── homepage.html       # User homepage after login
    ├── add.html            # Add new expense
    ├── add_account.html    # Add new account
    ├── edit.html           # Edit existing expense
    ├── display.html        # View expenses
    ├── month.html          # Monthly view
    ├── year.html           # Yearly view
    ├── today.html          # Today's expenses
    ├── limit.html          # Spending limits
    ├── manage_budgets.html # Budget management
    ├── manage_savings.html # Savings management
    ├── profile.html        # User profile
    └── 404.html           # 404 error page
```

## 🗃️ Database Schema

The application uses a MySQL database with the following tables:

### `register`
Stores user account information
- `id` (INT, PK, AUTO_INCREMENT) - Unique user identifier
- `username` (VARCHAR(255)) - User's display name
- `email` (VARCHAR(255), UNIQUE) - User's email address
- `hashed_password` (VARCHAR(255)) - Secure password hash

### `user_settings`
Stores user preferences
- `user_id` (INT, FK) - References register(id)
- `theme` (ENUM('light', 'dark')) - UI theme preference
- `currency` (VARCHAR(3)) - Preferred currency code (e.g., USD, EUR)

### `expenses`
Tracks all expense entries
- `id` (INT, PK, AUTO_INCREMENT) - Unique expense ID
- `userid` (INT, FK) - References register(id)
- `date` (DATE) - Date of expense
- `expensename` (VARCHAR(255)) - Description of expense
- `amount` (DECIMAL(10,2)) - Expense amount
- `paymode` (VARCHAR(50)) - Payment method (e.g., Cash, Credit Card)
- `category` (VARCHAR(100)) - Expense category
- `currency` (VARCHAR(3)) - Currency code for the amount

### `limits`
Manages monthly spending limits
- `id` (INT, PK, AUTO_INCREMENT)
- `userid` (INT, FK) - References register(id)
- `limitss` (DECIMAL(10,2)) - Monthly spending limit amount

## 🚀 Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/money-track.git
   cd money-track
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   - Install MySQL if not already installed
   - Create a new MySQL database:
     ```sql
     CREATE DATABASE expensetracker;
     ```
   - Import the database schema:
     ```bash
     mysql -u username -p expensetracker < expense_tracker.sql
     ```

5. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   DATABASE_URL=mysql://username:password@localhost/expensetracker
   SECRET_KEY=your-secret-key-here
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-email-password
   ```

## 🖥️ Usage

1. **Start the development server**
   ```bash
   python app.py
   ```
   or with auto-reload:
   ```bash
   flask run --debug
   ```

2. **Access the application**
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. **Getting Started**
   - Register a new account or log in with existing credentials
   - Set up your profile and preferences
   - Start adding your expenses
   - Set monthly spending limits
   - View your spending analytics

## 🌐 API Endpoints

### Authentication
- `POST /signup` - Register a new user
- `POST /login` - User login
- `GET /logout` - User logout

### Expenses
- `GET /` - Dashboard
- `POST /add` - Add new expense
- `POST /edit/<id>` - Update expense
- `GET /delete/<id>` - Delete expense
- `GET /month` - Monthly expenses view
- `GET /display` - Expense records

### Settings
- `GET /settings` - User settings page
- `POST /settings` - Update user settings
- `POST /limit` - Set spending limit

## 📦 Dependencies

### Backend
- Flask - Web framework
- Flask-MySQLdb - MySQL database integration
- Flask-Login - User session management
- Flask-Mail - Email notifications
- python-dotenv - Environment variable management
- passlib - Password hashing

### Frontend
- Bootstrap 5 - Responsive UI components
- Chart.js - Data visualization
- jQuery - DOM manipulation
- Font Awesome - Icons

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
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
# Flask Website

> A professional Flask-based web project following Lanqiao's tutorial, implementing user authentication, database migrations, and more.

![Flask](https://img.shields.io/badge/Flask-2.0.3-blue) ![Python](https://img.shields.io/badge/Python-3.11-yellow) ![Licence](https://img.shields.io/badge/Licence-MIT-green)

## Introduction
This project is a **Flask-based web application**. It aims to implement a fully functional website with user authentication, a blog system, and a clean UI using Flask-Bootstrap.

### Features
- **User Authentication**: Complete functionality for user registration, login, and logout.
- **Email Verification**: Automatic email verification upon registration using `Flask-Mail`, including token generation and email templates.
- **Secure Password Hashing**: Passwords are securely hashed using `werkzeug.security` to protect user credentials.
- **Database Management**: Database migrations are handled by `Flask-Migrate`, allowing for seamless schema changes.
- **Role-Based Access Control**: Implementation of user roles and permissions, ensuring that only authorised users can access specific features.
- **Dynamic User Profiles**: Users can manage their profiles, including attributes such as `age`, `gender`, `phone_number`, `location`, and `about_me`.
- **User Activity Tracking**: Tracks and displays the last seen time for users, enhancing user engagement.
- **Responsive User Interface**: A clean and responsive user interface built with `Flask-Bootstrap`, ensuring a good user experience across devices.
- **Error Handling**: Custom error pages for 404 and 500 errors to improve user experience.
- **Asynchronous Email Sending**: Emails are dispatched in a separate thread to prevent blocking the main application thread.
- **Form Validation**: Utilises `Flask-WTF` for form handling and validation, ensuring user input is properly checked.
- **Dynamic Time Formatting**: Uses `Flask-Moment` for displaying and formatting dates and times dynamically.
- Blog system with posts and comments (coming soon...)
- User profile and settings (coming soon...)

---

## Installation
### 1. Clone the Repository
```sh
git clone https://github.com/fredsun02/flask-website.git
cd flask-website
```

### 2. Create a Virtual Environment
```sh
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

---

## Usage
### 1. Set Up Environment Variables
Before running the application, export the necessary environment variables:
```sh
export FLASK_APP=manage.py
export FLASK_ENV=development
export FLASK_DEBUG=1
```

### 2. Initialise the Database
```sh
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 3. Start the Application
```sh
flask run
```
Now open your browser and visit: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## Project Structure
```
flask-website/
    ├── README.md               # Project documentation and overview
    ├── log.md                  # Development logs and notes
    ├── manage.py               # CLI entry point for managing the application
    ├── migrations               # Database migration files
    ├── requirements.txt         # List of Python dependencies
    └── weblog                   # Main application folder
        ├── __init__.py         # Initialisation for the weblog package
        ├── app.py               # Application factory and main app setup
        ├── configs.py           # Configuration settings for the application
        ├── decorators.py         # Custom decorators for permission checks
        ├── email.py             # Email sending functionality
        ├── forms.py             # Form classes for user input
        └── handlers              # Directory for view functions (blueprints)
            ├── front.py            # Front blueprint
            └── user.py            # User blueprint
        ├── models.py            # Database models and ORM definitions
        └── templates             # HTML templates for rendering views
            ├── 404.html         # Custom 404 error page
            ├── 500.html         # Custom 500 error page
            ├── base.html        # Base template for other templates to extend
            ├── email            # Email templates
            │   ├── confirm_user.html  # HTML template for user confirmation email
            │   ├── confirm_user.txt    # Plain text version of confirmation email
            │   ├── reset_password.html  # HTML template for password reset email
            │   └── reset_password.txt    # Plain text version of password reset email
            ├── index.html       # Homepage template
            ├── login.html       # Login page template
            ├── register.html    # Registration page template
            └── user             # User-related templates
                ├── confirm.html  # User confirmation page template
                ├── edit_profile.html  # User profile editing page template
                └── index.html    # User's personal homepage template
```
---

## Licence
This project is licensed under the MIT Licence - see the [LICENCE](LICENCE) file for details.

---

> *Built with Flask and Love by [fredsun02](https://github.com/fredsun02)*


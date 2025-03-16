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
├── README.md               # Project documentation
├── log.md                 # Development logs
├── manage.py              # CLI entry point
├── migrations/            # Database migrations
├── requirements.txt       # Dependencies
├── scripts/              # Utility scripts
│   └── generate_fake_data.py  # Test data generator
└── weblog/               # Main application package
    ├── handlers/         # View functions (blueprints)
    ├── templates/        # HTML templates
    ├── static/           # Static files (CSS, JS, etc.)
    ├── app.py            # Application factory
    ├── configs.py        # Configuration settings
    ├── decorators.py     # Custom decorators 
    ├── email.py          # Email functionality
    ├── forms.py          # Form definitions
    └── models.py         # Database models
```
---

## Licence
This project is licensed under the MIT Licence - see the [LICENCE](LICENCE) file for details.

---

> *Built with Flask and Love by [fredsun02](https://github.com/fredsun02)*


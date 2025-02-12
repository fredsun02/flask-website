# Flask Website

> A professional Flask-based web project following Lanqiao's tutorial, implementing user authentication, database migrations, and more.

![Flask](https://img.shields.io/badge/Flask-2.0.3-blue) ![Python](https://img.shields.io/badge/Python-3.11-yellow) ![Licence](https://img.shields.io/badge/Licence-MIT-green)

## Introduction
This project is a **Flask-based web application**. It aims to implement a fully functional website with user authentication, a blog system, and a clean UI using Flask-Bootstrap.

### Features
- User authentication (register, login, logout)
- Secure password hashing with `werkzeug.security`
- Database migrations using `Flask-Migrate`
- Bootstrap-based UI with `Flask-Bootstrap`
- Dynamic time formatting using `Flask-Moment`
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
│── weblog/              # Main application folder
│   ├── handlers/        # Views (blueprints)
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JS, images
│   ├── models.py        # Database models
│   ├── app.py           # App factory
│   ├── configs.py       # Configuration settings
│── migrations/          # Flask-Migrate database migrations
│── venv/                # Virtual environment (not included in Git)
│── manage.py            # CLI entry point
│── requirements.txt     # Python dependencies
│── README.md            # Project documentation
```

---

## Licence
This project is licensed under the MIT Licence - see the [LICENCE](LICENCE) file for details.

---

> *Built with Flask and Love by [fredsun02](https://github.com/fredsun02)*

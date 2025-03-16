# Flask Website

> A professional Flask-based web project following Lanqiao's tutorial, implementing user authentication, database migrations, and more.

![Flask](https://img.shields.io/badge/Flask-2.0.3-blue) ![Python](https://img.shields.io/badge/Python-3.11-yellow) ![Licence](https://img.shields.io/badge/Licence-MIT-green)

## Introduction
This is a full-stack web application built with Flask, featuring a modular design and blueprint architecture that delivers a complete user system, blog platform, and permission management. The project utilises SQLAlchemy ORM for database operations, supports Markdown content creation, and implements efficient permission control through bitwise operations. The system integrates email verification, user following, tag management, and other features, whilst providing a responsive interface design that ensures an excellent user experience across various devices.

### Features
- **User Authentication**: Complete functionality for user registration, login, and logout with email verification and password reset support.
- **Permission Management**: Efficient permission control system based on bitwise operations, supporting multiple user roles (administrator, moderator, regular user, etc.).
- **Blog Platform**: Markdown editing and preview support, automatic conversion to safe HTML with XSS attack prevention. 
- **Content Management**: Blog publishing, editing, paginated display, and tag management functionality.
- **User Interaction**: User following system, supporting follow/unfollow actions, status display, and following lists.

### Technology Stack
- **Backend Framework**: Flask
- **Database**: MySQL + SQLAlchemy ORM
- **Fronted Framework**: Bootstrap 3 + CSS + HTML5
- **Template Engine**: Jinja2

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


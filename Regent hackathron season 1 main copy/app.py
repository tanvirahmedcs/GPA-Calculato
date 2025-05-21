# Copyright © tanvir 2025

from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Load users from JSON file
users = load_users()

# Data for courses, units, GLH, and grade points
courses = {
    "btec_l2_it": {
        "name": "Pearson BTEC Level 2 Diploma in Information Technology",
        "units": {
            "Unit 1 Using IT to Support Information and Communication": 60,
            "Unit 6 Introduction to Digital Graphics and Animation": 60,
            "Unit 4 Introduction to Computer Networking": 60,
            "Unit 2 Data and Spreadsheet Modelling": 60,
            "Unit 5 Introduction to Programming": 60,
            "Unit 7 Introduction to Website Development": 60,
            "Unit 8 Introduction to App Development": 60,
            "Unit 10 Introduction to Database Systems": 60,
        },
        "grade_points_per_10_glh": {
            "U": 0,
            "P": 4,
            "M": 6,
            "D": 8,
        },
        "total_glh": 480,
        "grade_thresholds": {
            "U": 0,
            "PP": 192,
            "MP": 234,
            "MM": 276,
            "DM": 318,
            "DD": 360,
            "D*D": 366,
            "DD+": 372,
        }
    },
    "btec_l3_it": {
        "name": "Pearson BTEC Level 3 Extended Diploma in Information Technology",
        "units": {
            "Unit 1 Information Technology Systems – SMI": 120,
            "Unit 2 Creating Systems to Manage Information": 90,
            "Unit 3 Using Social Media in Business": 90,
            "Unit 4 Programming": 90,
            "Unit 5 Data Modelling": 60,
            "Unit 6 Website Development": 60,
            "Unit 8 Computer Games Development": 60,
            "Unit 9 IT Project Management": 90,
            "Unit 11 Cyber Security and Incident Management": 120,
            "Unit 12 IT Technical Support and Management": 60,
            "Unit 15 Cloud storage and Collaboration Tools": 60,
            "Unit 16 Digital 2D and 3D Graphics": 60,
            "Unit 17 Digital Animation and Effects": 60,
            "Unit 18 Internet of Things": 60,
        },
        "unit_points": {
            60: {"U": 0, "P": 6, "M": 10, "D": 16},
            90: {"U": 0, "P": 9, "M": 15, "D": 24},
            120: {"U": 0, "P": 12, "M": 20, "D": 32},
        },
        "total_glh": 1080,
        "grade_thresholds": {
            "U": 0,
            "PPP": 108,
            "MPP": 124,
            "MMP": 140,
            "MMM": 156,
            "DMM": 176,
            "DDM": 196,
            "DDD": 216,
            "DDD+": 234,
            "DDD++": 252,
            "DDD+++": 270,
        }
    },
    "btec_l2_business": {
        "name": "Pearson BTEC Level 2 Diploma in Business",
        "units": {
            "Unit 1: Business Purpose": 30,
            "Unit 2: Business Organizations": 30,
            "Unit 3: Financial Forecasting For Business": 30,
            "Unit 4: The Marketing Plan": 30,
            "Unit 5: People In Organizations": 30,
            "Unit 11: Business Online": 60,
            "Unit 15: Starting A Small Business": 60,
            "Unit 16: Working In Teams": 30,
            "Unit 18: Promoting And Branding In Retail Workplace": 60,
            "Unit 28: Running A Small Business": 60,
            "Unit 29: The Importance Of Enterprise And Entrepreneurship": 30,
            "Unit 30: Social Enterprise": 30,
        },
        "grade_points_per_10_glh": {
            "U": 0,
            "P": 4,
            "M": 6,
            "D": 8,
        },
        "total_glh": 480,
        "grade_thresholds": {
            "U": 0,
            "PP": 192,
            "MP": 234,
            "MM": 276,
            "DM": 318,
            "DD": 360,
            "D*D": 366,
            "DD+": 372,
        }
    },
    "btec_l3_business": {
        "name": "Pearson BTEC Level 3 Extended Diploma in Business",
        "units": {
            "Unit 1: Exploring The Business": 90,
            "Unit 2: Research And Plan Marketing Campaign": 90,
            "Unit 3: Business Finance": 90,
            "Unit 4: Managing An Event": 90,
            "Unit 5: International Business": 60,
            "Unit 6: Principles Of Management": 60,
            "Unit 7: Business Decision Making": 120,
            "Unit 8: Human Resources": 60,
            "Unit 9: Team Building In Business": 60,
            "Unit 10: Recording Financial Transactions": 60,
            "Unit 13: Cost And Management Accounting": 60,
            "Unit 16: Visual Merchandising": 60,
            "Unit 17: Digital Marketing": 60,
            "Unit 19: Pitching for A New Business": 60,
            "Unit 24: Branding": 60,
        },
        "unit_points": {
            60: {"U": 0, "P": 6, "M": 10, "D": 16},
            90: {"U": 0, "P": 9, "M": 15, "D": 24},
            120: {"U": 0, "P": 12, "M": 20, "D": 32},
        },
        "total_glh": 1080,
        "grade_thresholds": {
            "U": 0,
            "PPP": 108,
            "MPP": 124,
            "MMP": 140,
            "MMM": 156,
            "DMM": 176,
            "DDM": 196,
            "DDD": 216,
            "DDD+": 234,
            "DDD++": 252,
            "DDD+++": 270,
        }
    }
}

grade_scale = ["U", "P", "M", "D"]

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            flash('Welcome back, {}!'.format(username), 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not username or not password or not confirm_password:
            flash('All fields are required.', 'danger')
        elif username in users:
            flash('This username is already taken. Please choose another.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match. Please re-enter.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            users[username] = {'password': hashed_password}
            save_users(users)
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        if username in users:
            # Here you could implement actual password reset logic
            flash('Password reset instructions have been sent to your email (simulated).', 'info')
        else:
            flash('Username not found. Please check and try again.', 'danger')
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    return render_template('index.html', courses=courses)

@app.route('/grades/<course_id>', methods=['GET', 'POST'])
@login_required
def grades(course_id):
    if course_id not in courses:
        return redirect(url_for('index'))
    course = courses[course_id]
    if request.method == 'POST':
        grades_input = {}
        for unit in course['units']:
            grade = request.form.get(unit)
            if grade not in grade_scale:
                grade = "U"
            grades_input[unit] = grade
        # Calculate points
        total_points = 0
        if 'grade_points_per_10_glh' in course:
            # Use grade points per 10 GLH
            for unit, glh in course['units'].items():
                grade = grades_input[unit]
                points_per_10 = course['grade_points_per_10_glh'][grade]
                points = (glh / 10) * points_per_10
                total_points += points
        else:
            # Use unit_points based on GLH
            for unit, glh in course['units'].items():
                grade = grades_input[unit]
                points = course['unit_points'][glh][grade]
                total_points += points
        # Determine final grade
        final_grade = "U"
        for grade_name, threshold in sorted(course['grade_thresholds'].items(), key=lambda x: x[1]):
            if total_points >= threshold:
                final_grade = grade_name
        return render_template('result.html', course=course, grades=grades_input, total_points=total_points, final_grade=final_grade)
    return render_template('grades.html', course=course)

if __name__ == '__main__':
    app.run(debug=True, port=5002)

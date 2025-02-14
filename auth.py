from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'  # change to PostgreSQL database later if needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # change to your secret key

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='employee')
    position = db.Column(db.String(100), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

#  Role-Based Access Control: Admin and Employee
@app.route('/report')
@login_required
def report():
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'danger')
        return redirect(url_for('dashboard'))
    
    records =db.session.execute("""
        SELECT User.id, User.name, attendance.punch_in_time, attendance.punch_out_time
        FROM attendance
        JOIN user ON attendance.employee_id = User.id
        ORDER BY attendance.punch_in_time DESC
    """).fetchall()
    

    return render_template('report.html', records=records)


# Render the report in a template (create a 'report.html' in your templates folder)

# Attendance Model (note: consider renaming to "Attendance" for conventional spelling)
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    punch_in_time = db.Column(db.DateTime, default=datetime.utcnow) # Fixed from db.Sting to db.String
    punch_out_time = db.Column(db.DateTime, nullable=True)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----- Authentication Routes -----

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'employee')  # Default to employee

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(name=name, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# ----- Punch In/Out Routes -----

@app.route('/punch_in', methods=['POST'])
@login_required
def punch_in():
    # Check if already punched in (an open record exists)
    open_record = Attendance.query.filter_by(employee_id=current_user.id, punch_out_time=None).first()
    if open_record:
        flash('You are already punched in', 'warning')
        return redirect(url_for('dashboard'))
        
    punch_in_time = datetime.utcnow()
    new_record = Attendance(employee_id=current_user.id, punch_in_time=punch_in_time)
    db.session.add(new_record)
    db.session.commit()
    flash('Punched in successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/punch_out', methods=['POST'])
@login_required
def punch_out():
    # Find the open attendance record (punch_in without punch_out)
    record = Attendance.query.filter_by(employee_id=current_user.id, punch_out_time=None).first()
    if not record:
        flash('You are not punched in', 'warning')
        return redirect(url_for('dashboard'))
        
    record.punch_out_time = datetime.utcnow()
    db.session.commit()
    flash('Punched out successfully', 'success')
    return redirect(url_for('dashboard'))

# Protected Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they do not exist
        app.run(debug=True)
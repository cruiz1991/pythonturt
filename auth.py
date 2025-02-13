from flask import Flask, render_template, request, redirect, url_for, session , flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db' # change to PostgresSQL database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']= 'your_secret_key' # change to your secret key

db= SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#user Model
class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='employee')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Register route

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'employee') #Default to employee

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

#Login route

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user =User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

#Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

#Protected Dashboard 

   
@app.route('/dashboard')
@login_required
def dashboard():
    return f'Welcome {current_user.name}! You are logged in as {current_user.role}.'

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creat tables if they do not exist
        app.run(debug=True)
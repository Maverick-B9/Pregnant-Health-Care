# smart-healthcare-app/app/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import mysql # Import the mysql instance from the app package
from app.models import User # Import User model

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard')) # Redirect to dashboard if already logged in
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html', name=name, email=email)
        
        # Check if user already exists using the User model method
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('Email address already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                        (name, email, hashed_password))
            mysql.connection.commit()
            cur.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            mysql.connection.rollback()
            current_app.logger.error(f"Registration error: {e}", exc_info=True)
            flash('An error occurred during registration. Please try again.', 'danger')
            
    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard')) # Redirect to dashboard if already logged in

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html', email=email)

        user_from_db = User.get_by_email(email) # Use User model method

        # Ensure password_hash was fetched and is checked
        if user_from_db and user_from_db.password_hash and check_password_hash(user_from_db.password_hash, password):
            login_user(user_from_db, remember=request.form.get('remember') == 'true')
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            # Redirect to dashboard after successful login if no next_page
            return redirect(next_page or url_for('main.dashboard')) 
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            
    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home')) # Redirect to the public home/landing page
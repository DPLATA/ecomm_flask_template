from flask import render_template, redirect, url_for, request, flash, session
from app.blueprints.auth import bp
from app.db import get_db_connection
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)

                # Check if username or email already exists
                cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
                existing_user = cursor.fetchone()

                if existing_user:
                    flash('Username or email already exists.')
                    return render_template('register.html')

                # Insert new user
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                               (username, email, hashed_password))
                connection.commit()

                flash('Registration successful. Please log in.')
                return redirect(url_for('auth.login'))
            except Error as e:
                print(f"Error: {e}")
                flash('An error occurred during registration.')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Database connection failed.')

    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['is_admin'] = user['is_admin']  # Store the is_admin flag in the session
                    flash('Logged in successfully.')
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('auth.dashboard'))
                else:
                    flash('Invalid username or password.')
            except Error as e:
                print(f"Error: {e}")
                flash('An error occurred during login.')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Database connection failed.')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT o.id, o.status, o.total_price, o.created_at,
                       p.name as product_name, oi.quantity
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE o.user_id = %s
                ORDER BY o.created_at DESC
            """, (user_id,))
            orders = cursor.fetchall()
            return render_template('dashboard.html', orders=orders)
        except Error as e:
            print(f"Error: {e}")
            flash('An error occurred while fetching your orders.')
        finally:
            cursor.close()
            connection.close()
    else:
        flash('Database connection failed.')

    return redirect(url_for('main.index'))
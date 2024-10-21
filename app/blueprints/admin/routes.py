# app/blueprints/admin/routes.py

from flask import render_template, redirect, url_for, request, flash, session
from app.blueprints.admin import bp
from app.db import get_db_connection
from mysql.connector import Error
from app.blueprints.auth.routes import login_required
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('You need to be an admin to access this page.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@bp.route('/orders')
@login_required
@admin_required
def view_orders():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT o.id, o.user_id, o.status, o.total_price, o.created_at,
                       u.username, u.email
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC
            """)
            orders = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('admin_orders.html', orders=orders)
        except Error as e:
            print(f"Error: {e}")
            flash('An error occurred while fetching orders.')
    return redirect(url_for('admin.admin_dashboard'))

@bp.route('/order/<int:order_id>')
@login_required
@admin_required
def order_details(order_id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT o.id, o.user_id, o.status, o.total_price, o.created_at,
                       u.username, u.email,
                       oi.product_id, oi.quantity, oi.price,
                       p.name as product_name
                FROM orders o
                JOIN users u ON o.user_id = u.id
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE o.id = %s
            """, (order_id,))
            order = cursor.fetchall()
            cursor.close()
            connection.close()
            if order:
                return render_template('admin_order_detail.html', order=order)
            else:
                flash('Order not found.')
        except Error as e:
            print(f"Error: {e}")
            flash('An error occurred while fetching order details.')
    return redirect(url_for('admin.view_orders'))
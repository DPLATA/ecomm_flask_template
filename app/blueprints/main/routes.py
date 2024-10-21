# from flask import render_template, redirect, url_for, request, session
# from app.blueprints.main import bp
# from app.db import get_db_connection
# from mysql.connector import Error
#
# @bp.route('/')
# def product_list():
#     connection = get_db_connection()
#     if connection:
#         try:
#             cursor = connection.cursor(dictionary=True)
#             cursor.execute("SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id")
#             products = cursor.fetchall()
#             cursor.close()
#             connection.close()
#             return render_template('product_list.html', products=products)
#         except Error as e:
#             print(f"Error: {e}")
#             return "An error occurred", 500
#     else:
#         return "Database connection failed", 500
#
# @bp.route('/product/<int:product_id>')
# def product_detail(product_id):
#     connection = get_db_connection()
#     if connection:
#         try:
#             cursor = connection.cursor(dictionary=True)
#             cursor.execute("SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id WHERE p.id = %s", (product_id,))
#             product = cursor.fetchone()
#             cursor.close()
#             connection.close()
#             if product:
#                 return render_template('product_detail.html', product=product)
#             else:
#                 return "Product not found", 404
#         except Error as e:
#             print(f"Error: {e}")
#             return "An error occurred", 500
#     else:
#         return "Database connection failed", 500
#
# @bp.route('/shipping/<int:product_id>', methods=['GET', 'POST'])
# def shipping(product_id):
#     if request.method == 'POST':
#         shipping_info = {
#             'name': request.form.get('name'),
#             'address': request.form.get('address'),
#             'city': request.form.get('city'),
#             'country': request.form.get('country'),
#             'zip_code': request.form.get('zip')
#         }
#         session['shipping_info'] = shipping_info
#         session['product_id'] = product_id
#         return redirect(url_for('orders.create_checkout_session'))
#     return render_template('shipping.html', product_id=product_id)


from flask import render_template, redirect, url_for, request, session
from app.blueprints.main import bp
from app.db import get_db_connection
from mysql.connector import Error

@bp.route('/')
def index():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categories")
            categories = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('index.html', categories=categories)
        except Error as e:
            print(f"Error: {e}")
            return "An error occurred", 500
    else:
        return "Database connection failed", 500

@bp.route('/products')
def product_list():
    category_id = request.args.get('category_id', type=int)
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            if category_id:
                cursor.execute("SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id WHERE p.category_id = %s", (category_id,))
            else:
                cursor.execute("SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id")
            products = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('product_list.html', products=products)
        except Error as e:
            print(f"Error: {e}")
            return "An error occurred", 500
    else:
        return "Database connection failed", 500

@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id WHERE p.id = %s", (product_id,))
            product = cursor.fetchone()
            cursor.close()
            connection.close()
            if product:
                return render_template('product_detail.html', product=product)
            else:
                return "Product not found", 404
        except Error as e:
            print(f"Error: {e}")
            return "An error occurred", 500
    else:
        return "Database connection failed", 500

@bp.route('/shipping/<int:product_id>', methods=['GET', 'POST'])
def shipping(product_id):
    if request.method == 'POST':
        shipping_info = {
            'name': request.form.get('name'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'country': request.form.get('country'),
            'zip_code': request.form.get('zip')
        }
        session['shipping_info'] = shipping_info
        session['product_id'] = product_id
        return redirect(url_for('orders.create_checkout_session'))
    return render_template('shipping.html', product_id=product_id)
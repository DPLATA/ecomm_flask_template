from flask import render_template, redirect, url_for, request, session, flash
from app.blueprints.cart import bp
from app.db import get_db_connection
from mysql.connector import Error
from app.blueprints.auth.routes import login_required

@bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    if 'cart' not in session:
        session['cart'] = {}
    if str(product_id) in session['cart']:
        session['cart'][str(product_id)] += quantity
    else:
        session['cart'][str(product_id)] = quantity
    session.modified = True
    flash('Item added to cart successfully!')
    return redirect(url_for('main.product_detail', product_id=product_id))

@bp.route('/view')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    if cart:
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                for product_id, quantity in cart.items():
                    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                    product = cursor.fetchone()
                    if product:
                        item_total = float(product['price']) * quantity
                        cart_items.append({
                            'product': product,
                            'quantity': quantity,
                            'total': item_total
                        })
                        total += item_total
                cursor.close()
                connection.close()
            except Error as e:
                print(f"Error: {e}")
                flash('An error occurred while retrieving cart items.')
        else:
            flash('Database connection failed.')
    return render_template('cart_view.html', cart_items=cart_items, total=total)

@bp.route('/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 0))
    if 'cart' in session and str(product_id) in session['cart']:
        if quantity > 0:
            session['cart'][str(product_id)] = quantity
        else:
            session['cart'].pop(str(product_id))
    session.modified = True
    flash('Cart updated successfully!')
    return redirect(url_for('cart.view_cart'))

@bp.route('/remove/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session and str(product_id) in session['cart']:
        session['cart'].pop(str(product_id))
        session.modified = True
        flash('Item removed from cart successfully!')
    return redirect(url_for('cart.view_cart'))

@bp.route('/clear')
def clear_cart():
    session.pop('cart', None)
    flash('Cart cleared successfully!')
    return redirect(url_for('cart.view_cart'))
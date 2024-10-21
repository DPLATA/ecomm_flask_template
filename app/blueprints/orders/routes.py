from flask import render_template, redirect, url_for, session, flash
from app.blueprints.orders import bp
from app.db import get_db_connection
from app.extensions import stripe
from app.utils.unique_ids import generate_order_number
from mysql.connector import Error
from app.blueprints.auth.routes import login_required

@bp.route('/create-checkout-session', methods=['GET'])
@login_required
def create_checkout_session():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.')
        return redirect(url_for('cart.view_cart'))

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            line_items = []
            for product_id, quantity in cart.items():
                cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                product = cursor.fetchone()
                if product:
                    line_items.append({
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(float(product['price']) * 100),
                            'product_data': {
                                'name': product['name'],
                                'description': product['description'],
                            },
                        },
                        'quantity': quantity,
                    })
            cursor.close()
            connection.close()

            if not line_items:
                flash('No valid items in cart.')
                return redirect(url_for('cart.view_cart'))

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=url_for('orders.success', _external=True),
                cancel_url=url_for('cart.view_cart', _external=True),
            )
            return redirect(checkout_session.url, code=303)
        except Error as e:
            print(f"Error: {e}")
            return "An error occurred", 500
    else:
        return "Database connection failed", 500

@bp.route('/success')
@login_required
def success():
    order_number = generate_order_number()
    user_id = session.get('user_id')
    cart = session.get('cart', {})

    if not cart:
        flash('Your cart is empty.')
        return redirect(url_for('main.index'))

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            # Calculate total price
            total_price = 0
            for product_id, quantity in cart.items():
                cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
                product = cursor.fetchone()
                if product:
                    total_price += float(product['price']) * quantity

            # Create a new order
            cursor.execute("""
                INSERT INTO orders (user_id, status, total_price)
                VALUES (%s, %s, %s)
            """, (user_id, 'Completed', total_price))
            order_id = cursor.lastrowid

            # Add order items
            for product_id, quantity in cart.items():
                cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
                product = cursor.fetchone()
                if product:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, product_id, quantity, price)
                        VALUES (%s, %s, %s, %s)
                    """, (order_id, product_id, quantity, product['price']))

            connection.commit()
            cursor.close()
            connection.close()

            # Clear cart
            session.pop('cart', None)

            flash('Order placed successfully!')
            return render_template('order_success.html', order_number=order_number)
        except Error as e:
            print(f"Error: {e}")
            return "An error occurred", 500
    else:
        return "Database connection failed", 500
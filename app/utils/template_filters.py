def cart_count(cart):
    if not cart:
        return 0
    return sum(cart.values())

def register_template_filters(app):
    app.jinja_env.filters['cart_count'] = cart_count
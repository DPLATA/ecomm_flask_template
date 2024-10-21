from flask import Flask
from app.extensions import stripe
from app.config import Config
from app.utils.template_filters import register_template_filters

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    stripe.api_key = app.config['STRIPE_API_KEY']

    # Register template filters
    register_template_filters(app)

    # Register blueprints
    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.orders import bp as orders_bp
    app.register_blueprint(orders_bp, url_prefix='/orders')

    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blueprints.cart import bp as cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')

    from app.blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
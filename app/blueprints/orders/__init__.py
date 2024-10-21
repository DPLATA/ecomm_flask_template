from flask import Blueprint

bp = Blueprint('orders', __name__)

from app.blueprints.orders import routes
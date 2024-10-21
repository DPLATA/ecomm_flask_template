# app/blueprints/cart/__init__.py
from flask import Blueprint

bp = Blueprint('cart', __name__)

from app.blueprints.cart import routes

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.blueprints.main import routes
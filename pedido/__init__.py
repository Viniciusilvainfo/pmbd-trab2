from flask import Blueprint
pedido_bp = Blueprint('pedido', __name__)
from . import routes
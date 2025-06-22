from flask import Blueprint
cardapio_bp = Blueprint('cardapio', __name__)
from . import routes
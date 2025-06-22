from flask import render_template, request, redirect, url_for, abort
from . import cardapio_bp
from db.Database import Database
from .dao import CardapioDAO


@cardapio_bp.route('/')
def index():
    
    limit = request.args.get('limit', default=10, type=int)
    if limit <= 0:
        abort(400, description="Limite deve ser um número positivo.")

    page = request.args.get('page', default=1, type=int)

    if page <= 0:
        abort(400, description="Página deve ser um número positivo.")

    db = Database().getConn()
    
    dao = CardapioDAO(db)
    
    offset = (page - 1) * limit
    
    items = dao.get_all(limit=limit,offset=offset)
    
    total_items = dao.count_all()
    
    total_pages = int((total_items + limit - 1) / limit)
    
    return render_template(
        'cardapio/index.html',
        items=items,
        total_items=total_items,
        limit=limit,
        total_pages=total_pages,
        page=page,
        rota='cardapio.index'
    )
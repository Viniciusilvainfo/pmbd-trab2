from flask import render_template, request, redirect, url_for, session, abort
from . import admin_bp
from db.Database import Database
from .dao import AdminDAO

@admin_bp.before_request
def check_admin():
    if not session.get('usuario') or not session['usuario'].get('admin'):
        abort(403)

@admin_bp.route('/')
def dashboard():
    db = Database().getConn()
    dao = AdminDAO(db)
    
    # Estatísticas para o dashboard
    total_pedidos = dao.count_pedidos()
    pedidos_recentes = dao.get_all_pedidos(limit=5)
    
    return render_template('admin/dashboard.html', 
                         total_pedidos=total_pedidos,
                         pedidos_recentes=pedidos_recentes)

@admin_bp.route('/pedidos')
def pedidos():
    limit = request.args.get('limit', default=10, type=int)
    page = request.args.get('page', default=1, type=int)
    
    if limit <= 0 or page <= 0:
        abort(400)
    
    db = Database().getConn()
    dao = AdminDAO(db)
    
    offset = (page - 1) * limit
    pedidos = dao.get_all_pedidos(limit=limit, offset=offset)
    total_pedidos = dao.count_pedidos()
    total_pages = (total_pedidos + limit - 1) // limit
    
    return render_template('admin/pedidos.html',
                         pedidos=pedidos,
                         total_pages=total_pages,
                         limit=limit,
                         page=page)

@admin_bp.route('/estoque')
def estoque():
    db = Database().getConn()
    dao = AdminDAO(db)
    estoque = dao.get_estoque()
    return render_template('admin/estoque.html', estoque=estoque)

@admin_bp.route('/estoque/atualizar', methods=['POST'])
def atualizar_estoque():
    estoque_id = request.form.get('estoque_id', type=int)
    quantidade = request.form.get('quantidade', type=int)
    
    if not estoque_id or quantidade is None:
        abort(400)
    
    db = Database().getConn()
    dao = AdminDAO(db)
    
    try:
        dao.update_estoque(estoque_id, quantidade)
        return redirect(url_for('admin.estoque'))
    except Exception as e:
        abort(500)

@admin_bp.route('/usuarios')
def usuarios():
    db = Database().getConn()
    dao = AdminDAO(db)
    usuarios = dao.get_all_usuarios()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/toggle-admin/<int:usuario_id>')
def toggle_admin(usuario_id):
    db = Database().getConn()
    dao = AdminDAO(db)
    
    usuario = next((u for u in dao.get_all_usuarios() if u['id'] == usuario_id), None)
    if not usuario:
        abort(404)
    
    novo_status = not usuario['admin']
    dao.update_usuario_admin(usuario_id, novo_status)
    
    return redirect(url_for('admin.usuarios'))
from flask import render_template, request, abort,session,jsonify,url_for,redirect
from . import pedido_bp
from db.Database import Database
from .dao import PedidoDAO
from usuario.dao import UsuarioDAO


@pedido_bp.route('/')
def index():

    limit = request.args.get('limit', default=10, type=int)
    if limit <= 0:
        abort(400, description="Limite deve ser um número positivo.")

    page = request.args.get('page', default=1, type=int)

    if page <= 0:
        abort(400, description="Página deve ser um número positivo.")
    
    if session.get('usuario') is None:
        return redirect(url_for('index'))
    
    usuario= session.get('usuario')
    if not usuario or not usuario.get('id'):
        return redirect(url_for('index'))
    
    usuario_id:int = usuario.get('id')

    db = Database().getConn()
    dao = PedidoDAO(db)

    offset = (page - 1) * limit

    total_pedidos = dao.countByUser(user_id=usuario_id)
    
    total_pages = int((total_pedidos + limit - 1) / limit)
    
    pedidos = dao.getManyByUser(user_id=usuario_id,limit=limit, offset=offset)

    return render_template(
        'pedido/index.html',
        pedidos=pedidos,
        total_pages=total_pages,
        limit=limit,
        page=page,
        rota='pedido.index'
    )

@pedido_bp.route('/recent', methods=['GET'])
def get_pedido_recente():
    db = Database().getConn()
    dao = PedidoDAO(db)
    
    if session.get('usuario') is None:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    usuario_id = session['usuario'].get('id')
    if not usuario_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    pedidos = dao.getManyByUser(user_id=usuario_id, limit=1, offset=0)
    
    pedido = pedidos[0] if len(pedidos)>0 else None

    if not pedido:
        return abort(400, 'Nenhum pedido encontrado para o usuário')
    
    return redirect(url_for('pedido.update', pedido_id=pedido.get('id')))

@pedido_bp.route('/<int:pedido_id>', methods=['GET','POST'])
def update(pedido_id:int):

    db = Database().getConn()
    dao = PedidoDAO(db)
    dao_usuario = UsuarioDAO(db)
    
    if not pedido_id:
        abort(400,'Pedido ID é obrigatório')
    
    pedido = dao.getOne(pedido_id)
    if not pedido:
        abort(400,'Pedido não encontrado')

    session_usuario = session.get('usuario')
    if not session_usuario or not session_usuario.get('id'):
        abort(401, 'Usuário não autenticado')

    if session_usuario.get('id') != pedido.get('usuario_id'):
        abort(403, 'Usuário não autorizado a editar este pedido')

    elif session_usuario.get('admin'):
        usuario = dao_usuario.getOne({'id':session_usuario.get('id')})
        if not usuario or not usuario.get('admin'):
            abort(403, 'Usuário não autorizado a editar este pedido')
    
    status= dao.getAllStatusPedido()
    status_id_pendente = next((s for s in status if s['descricao'].lower() == 'pendente'), None)
    status_id_cancelado = next((s for s in dao.getAllStatusPedido() if s['descricao'].lower() == 'cancelado'), None)
    edit:bool = session_usuario.get('admin')
    is_user:bool = session_usuario.get('id') == pedido.get('usuario_id')
    is_pedido_pendente:bool = pedido.get('status_id') == status_id_pendente.get('id') if status_id_pendente else False

    if request.method == 'GET':
        return render_template(
            'pedido/edit.html',
            pedido=pedido,
            edit=edit,
            is_user=is_user,
            is_pedido_pendente=is_pedido_pendente,
            status=status
        )
    
    elif request.method == 'POST':
        if not edit and not is_user:
            abort(403, 'Usuário não autorizado a editar este pedido')

        body = request.form

        if not body:
            abort(400, 'Corpo da requisição é obrigatório')
        
        if body.get('action','') == 'cancel' and is_pedido_pendente and is_user:
            if not status_id_cancelado:
                abort(400, 'Status de cancelamento não encontrado')
            dao.updateStatus(pedido_id, status_id_cancelado.get('id'))
        
        if body.get('status_id'):
            status_id = int(body.get('status_id'))
            if not status_id:
                abort(400, 'Status ID é obrigatório')
            
            if not any(s['id'] == status_id for s in status):
                abort(400, 'Status ID inválido')

            if not dao.updateStatus(pedido_id, status_id):
                abort(500, 'Erro ao atualizar status do pedido')


        return redirect(url_for('pedido.update', pedido_id=pedido_id))

@pedido_bp.route('/add', methods=['POST'])
def create():
    
    if session.get('usuario') is None:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    body = request.json
    if not body:
        return jsonify({'error': 'Corpo da requisição é obrigatório'}), 400

    if not body.get('items',[]):
        return jsonify({'error': 'Lista de itens é obrigatória'}), 400

    if len(body.get('items',[])) == 0:
        return jsonify({'error': 'Lista de itens não pode ser vazia'}), 400

    db = Database().getConn()
    dao = PedidoDAO(db)
    try:
        usuario_id = session['usuario']['id']

        if not usuario_id:
            return jsonify({'error': 'Usuário não autenticado'}), 401
        

        items_id = [item.get('id') for item in body.get('items', [])]
        items_id_no_duplicates = list(set(item.get('id') for item in body.get('items', [])))
        if not dao.checkIfItemsExist(items_id_no_duplicates):
            return jsonify({'error': 'Alguns itens não existem ou não estão disponíveis'}), 400
        
        pedido_id = dao.save(usuario_id, items_id)
        if not pedido_id:
            return jsonify({'error': 'Erro ao criar pedido'}), 500
        
        return jsonify({'message': 'Pedido criado com sucesso', 'pedido_id': pedido_id}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


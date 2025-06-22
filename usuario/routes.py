from flask import render_template, request, abort,session,redirect, url_for
from werkzeug.security import generate_password_hash
from . import usuario_bp
from db.Database import Database
from .dao import UsuarioDAO

@usuario_bp.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        nome:str= request.form.get('nome')

        email:str = request.form.get('email')

        senha:str = request.form.get('senha')

        if not nome or not email or not senha:
            return render_template('usuario/index.html', erros={'msg': 'Todos os campos são obrigatórios'})
        
        if len(senha) < 6:
            return render_template('usuario/index.html', erros={'msg': 'A senha deve ter pelo menos 6 caracteres'})
        
        if not email or '@' not in email or '.' not in email:
            return render_template('usuario/index.html', erros={'msg': 'Email inválido'})
        
        hash_senha = generate_password_hash(senha)
        usuario = {
            'nome': nome,
            'email': email,
            'senha': hash_senha,
            'admin': False
        }

        db = Database().getConn()

        usuario_dao = UsuarioDAO(db)

        if usuario_dao.getOne({'email': email}):
            return render_template('usuario/index.html', erros={'msg': 'Email já cadastrado'})

        usuario = usuario_dao.save(usuario)
        if usuario:
            del usuario['senha']
            session['usuario'] = usuario
            return redirect(url_for('index'))
        
        else:
            return render_template('usuario/index.html', erros={'msg': 'Erro ao cadastrar usuário'})
    
    return render_template('usuario/index.html', usuario=None)
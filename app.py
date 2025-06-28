
from flask import Flask, render_template,redirect, url_for, request, session, flash
from werkzeug.security import check_password_hash
from cardapio import cardapio_bp
from pedido import pedido_bp
from usuario import usuario_bp
from admin import admin_bp
from db.Database import Database
from usuario.dao import UsuarioDAO

app = Flask(__name__)

app.secret_key = 'nao vou usar env nessa porra'

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(cardapio_bp, url_prefix='/cardapio')
app.register_blueprint(pedido_bp, url_prefix='/pedido')
app.register_blueprint(usuario_bp, url_prefix='/usuario')

@app.before_request
def require_login():
    allowed_routes = ['login', 'usuario.index']
    if 'usuario' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db= Database().getConn()
        dao = UsuarioDAO(db)
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not email or not senha:
            flash('Email e senha são obrigatórios')
            return redirect(url_for('login'))
        
        usuario = dao.getOne({'email': email})
        if not usuario:
            flash('Usuário não encontrado')
            return redirect(url_for('login'))
        
        if check_password_hash(usuario.get('senha',''), senha):
            del usuario['senha']
            session['usuario'] = usuario
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos')
    if 'usuario' in session:
        return redirect(url_for('index'))
    
    return render_template('login.html',erros={})


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Você foi desconectado com sucesso.')
    return redirect(url_for('login'))


@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html',is_cozinha=True)

    

if __name__ == '__main__':
    app.run(debug=True)

import secrets
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from flask_mail import Mail, Message
from .modelos import Usuarios
from . import db


login = Blueprint('login', __name__)


@login.route('/entrar')
def entrar():
    return render_template('entrar.html')


@login.route('/entrar', methods=['POST'])
def entrar_post():
    email = request.form.get('email')
    senha = request.form.get('senha')
    lembrar = True if request.form.get('lembrar') else False
    
    usuario = Usuarios.query.filter_by(email=email).first()
    
    if not usuario or not check_password_hash(usuario.senha, senha+app.config['SECRET_KEY']):
        flash('Por favor, verifique seus dados de login e tente novamente.', 'erro')
        return redirect(url_for('login.entrar'))
    
    login_user(usuario, remember=lembrar)
    return redirect(url_for('painel.principal'))


@login.route('/cadastrar')
def cadastrar():
    return render_template('cadastrar.html')


@login.route('/cadastrar', methods=['POST'])
def cadastrar_post():
    email = request.form.get('email')
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    
    usuario = Usuarios.query.filter_by(email=email).first()
    
    if usuario:
        flash('Endereço de e-mail já está cadastrado.', 'erro')
        return redirect(url_for('login.cadastrar'))
        
    novo_usuario = Usuarios(email=email, nome=nome, senha=generate_password_hash(senha+app.config['SECRET_KEY'], method='pbkdf2:sha256'))
    
    db.session.add(novo_usuario)
    db.session.commit()
    
    flash('Seu usuário foi cadastrado. Use seu e-mail e senha para entrar.', 'sucesso')
    return redirect(url_for('login.entrar'))


@login.route('/sair')
@login_required
def sair():
    logout_user()
    return redirect(url_for('painel.index'))


@login.route('/esqueci_senha')
def esqueci_senha():
    return render_template('esqueci_senha.html')


@login.route('/esqueci_senha', methods=['POST'])
def esqueci_senha_post():
    email = request.form.get('email')
    
    usuario = Usuarios.query.filter_by(email=email).first()
    
    if usuario:
        token = secrets.token_urlsafe(16)
        usuario.token_nova_senha = token
        db.session.commit()

        enviar_token(usuario.email, usuario.nome, token)

        flash('Enviamos um e-mail para você com instruções para cadastrar uma nova senha.', 'sucesso')
        return redirect(url_for('login.entrar'))
        
    flash('Não encontramos nenhum usuário com o e-mail informado.', 'erro')
    return redirect(url_for('login.esqueci_senha'))


@login.route('/nova_senha/<token>')
def nova_senha(token):
    usuario = Usuarios.query.filter_by(token_nova_senha=token).first()

    if usuario:
        return render_template('nova_senha.html', token=token, nome=usuario.nome)
    
    flash('Não existe nenhuma solicitação de alteração de senha para o token informado.', 'erro')
    return redirect(url_for('login.esqueci_senha'))


@login.route('/nova_senha', methods=['POST'])
def nova_senha_post():
    token = request.form.get('token')
    usuario = Usuarios.query.filter_by(token_nova_senha=token).first()

    if usuario:
        nova_senha = request.form.get('nova_senha')
        confirmacao_nova_senha = request.form.get('confirmacao_nova_senha')
        
        if nova_senha != confirmacao_nova_senha:
            flash('A senha e a confirmação da senha não conferem. Preencha novamente, por favor.', 'erro')
            return redirect(url_for('login.nova_senha', token=token))
        
        usuario.senha = generate_password_hash(nova_senha+app.config['SECRET_KEY'], method='pbkdf2:sha256')
        usuario.token_nova_senha = None
        db.session.commit()

        flash('Sua senha foi alterada com sucesso. Faça o login abaixo.', 'sucesso')
        return redirect(url_for('login.entrar'))
    
    flash('Não existe nenhuma solicitação de alteração de senha para o token informado.', 'erro')
    return redirect(url_for('login.esqueci_senha'))
        

def enviar_token(email, nome, token):
    mail = Mail(app)

    msg = Message("FreeDiet: Altere a sua senha",
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email])
    
    msg.body = f"Olá {nome}! Recebemos uma solicitação de alteração de senha.\n\nUse o link abaixo para alterar a sua senha:\nhttp://127.0.0.1:5000/nova_senha/{token}\n\nSe você não solicitou alteração de senha, por favor desconsidere essa mensagem.\n\nAté mais!\nEquipe FreeDiet"
    mail.send(msg)


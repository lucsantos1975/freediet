import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv


db = SQLAlchemy()


def create_app():
    load_dotenv()

    mysql_host = os.getenv('MYSQL_HOST')
    mysql_user = os.getenv('MYSQL_USER')
    mysql_password = os.getenv('MYSQL_PASSWORD')
    mysql_database = os.getenv('MYSQL_DATABASE')

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:3306/{mysql_database}"

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'login.entrar'
    login_manager.session_protection = 'strong'
    login_manager.init_app(app)
    
    from .modelos import Usuarios
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuarios.query.get(int(user_id))

    from .login import login as login_blueprint
    app.register_blueprint(login_blueprint)

    from .painel import painel as painel_blueprint
    app.register_blueprint(painel_blueprint)

    return app


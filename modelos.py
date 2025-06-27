import datetime
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin
from .taco.grupos import Grupos
from . import db


class Usuarios(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(255))
    nome = db.Column(db.String(100))
    token_nova_senha = db.Column(db.String(100))
    criado_em = db.Column(db.DateTime, default=datetime.datetime.now)
    atualizado_em = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class Alimentos(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100))
    grupo = db.Column(db.Enum(Grupos))
    umidade = db.Column(db.Float)
    energia_kcal = db.Column(db.Float)
    energia_kj = db.Column(db.Float)
    proteina = db.Column(db.Float)
    lipideos = db.Column(db.Float)
    colesterol = db.Column(db.Float)
    carboidratos = db.Column(db.Float)
    fibra_alimentar = db.Column(db.Float)
    cinzas = db.Column(db.Float)
    calcio = db.Column(db.Float)
    magnesio = db.Column(db.Float)
    manganes = db.Column(db.Float)
    fosforo = db.Column(db.Float)
    ferro = db.Column(db.Float)
    sodio = db.Column(db.Float)
    potassio = db.Column(db.Float)
    cobre = db.Column(db.Float)
    zinco = db.Column(db.Float)
    retinol = db.Column(db.Float)
    re = db.Column(db.Float)
    rae = db.Column(db.Float)
    tiamina = db.Column(db.Float)
    riboflavina = db.Column(db.Float)
    piridoxina = db.Column(db.Float)
    niacina = db.Column(db.Float)
    vitamina_c = db.Column(db.Float)


class Pacientes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    nome = db.Column(db.String(100))
    data_nascimento = db.Column(db.Date)
    email = db.Column(db.String(100))
    token_acesso = db.Column(db.String(50))
    criado_em = db.Column(db.DateTime, default=datetime.datetime.now)
    atualizado_em = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class Refeicoes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_paciente = db.Column(db.Integer)
    descricao = db.Column(db.String(100))
    horario = db.Column(db.Time)
    criado_em = db.Column(db.DateTime, default=datetime.datetime.now)
    atualizado_em = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class AlimentosRefeicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_refeicao = db.Column(db.Integer)
    id_alimento = db.Column(db.Integer)
    quantidade = db.Column(db.Integer)

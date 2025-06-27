import secrets
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from .taco.grupos import Grupos
from .modelos import Alimentos, Pacientes, Refeicoes, AlimentosRefeicao
from . import db


painel = Blueprint('painel', __name__)


@painel.route('/')
def index():
    return render_template('index.html')


@painel.route('/principal')
@login_required
def principal():
    return render_template('principal.html', nome=current_user.nome)


@painel.route('/paciente/<token>')
def paciente(token):
    paciente = Pacientes.query.filter_by(token_acesso=token).first()
    return render_template("paciente.html", paciente=paciente)


@painel.route('/alimentos')
@login_required
def alimentos():
    return render_template('alimentos.html', grupos=Grupos)


@painel.route('/listar_alimentos', methods=['POST'])
@login_required
def listar_alimentos():
    grupo = Grupos[request.form.get('grupo')]
    alimentos = Alimentos.query.filter_by(grupo=grupo.name).all()
    return jsonify([alimento.to_dict() for alimento in alimentos])


@painel.route('/pacientes')
@login_required
def pacientes():
    lista_pacientes = Pacientes.query.filter_by(id_usuario=current_user.id).order_by('nome').all()
    return render_template('pacientes.html', pacientes=lista_pacientes, calcular_idade=calcular_idade)


@painel.route('/novo_paciente')
@login_required
def novo_paciente():
    return render_template('novo_paciente.html', ano_atual=date.today().year)


@painel.route('/novo_paciente', methods=['POST'])
@login_required
def novo_paciente_post():
    nome = request.form.get('nome')
    email = request.form.get('email')
    dia_nasc = request.form.get('dia')
    mes_nasc = request.form.get('mes')
    ano_nasc = request.form.get('ano')

    erro = validar_dados_paciente(nome, dia_nasc, mes_nasc, ano_nasc)

    if erro:
        flash(erro, 'erro')
        return render_template('novo_paciente.html', nome=nome, email=email, dia=dia_nasc, mes=mes_nasc, ano=ano_nasc, ano_atual=date.today().year)

    try:
        paciente = Pacientes()
        paciente.nome = nome
        paciente.email = email
        paciente.data_nascimento = f"{ano_nasc}-{mes_nasc}-{dia_nasc}"
        paciente.token_acesso = secrets.token_urlsafe(8)
        paciente.id_usuario = current_user.id
        db.session.add(paciente)
        db.session.commit()
        flash('Novo paciente incluído com sucesso', 'sucesso')
    except Exception as erro:
        flash('Ocorreu um erro ao incluir o novo paciente: ' + erro, 'erro')

    return redirect(url_for('painel.pacientes'))


@painel.route('/alterar_paciente/<int:id_paciente>')
@login_required
def alterar_paciente(id_paciente):
    paciente = consultar_paciente(id_paciente)
    
    nome = paciente.nome
    email = paciente.email
       
    array_data_nascimento = str(paciente.data_nascimento).split('-')
    dia_nasc = array_data_nascimento[2]
    mes_nasc = array_data_nascimento[1]
    ano_nasc = array_data_nascimento[0]
    
    return render_template('alterar_paciente.html', id_paciente=id_paciente, nome=nome, email=email, dia=dia_nasc, mes=mes_nasc, ano=ano_nasc, ano_atual=date.today().year)


@painel.route('/alterar_paciente/<int:id_paciente>', methods=['GET','POST'])
@login_required
def alterar_paciente_post(id_paciente):
    paciente = consultar_paciente(id_paciente)

    nome = request.form.get('nome')
    email = request.form.get('email')
    dia_nasc = request.form.get('dia')
    mes_nasc = request.form.get('mes')
    ano_nasc = request.form.get('ano')

    erro = validar_dados_paciente(nome, dia_nasc, mes_nasc, ano_nasc)
    if erro:
        flash(erro, 'erro')
        return render_template('alterar_paciente.html', id_paciente=id_paciente, nome=nome, email=email, dia=dia_nasc, mes=mes_nasc, ano=ano_nasc, ano_atual=date.today().year)

    try:
        paciente.nome = nome
        paciente.email = email
        paciente.data_nascimento = f"{ano_nasc}-{mes_nasc}-{dia_nasc}"
        db.session.commit()
        flash('Dados do paciente foram atualizados com sucesso.', 'sucesso')
    except Exception as erro:
        flash('Ocorreu um erro ao atualizar os dados: ' + erro, 'erro')

    return redirect(url_for('painel.pacientes'))


@painel.route('/dados_paciente/<int:id_paciente>')
@login_required
def dados_paciente(id_paciente):
    paciente = consultar_paciente(id_paciente)
    refeicoes = Refeicoes.query.filter_by(id_paciente=id_paciente).order_by('horario').all()

    return render_template('dados_paciente.html', paciente=paciente, refeicoes=refeicoes, calcular_idade=calcular_idade)


@painel.route('/nova_refeicao/<int:id_paciente>')
@login_required
def nova_refeicao(id_paciente):
    paciente = consultar_paciente(id_paciente)
        
    return render_template('nova_refeicao.html', paciente=paciente, calcular_idade=calcular_idade)


@painel.route('/nova_refeicao/<int:id_paciente>', methods=['GET', 'POST'])
@login_required
def nova_refeicao_post(id_paciente):
    paciente = consultar_paciente(id_paciente)

    descricao = request.form.get('descricao')
    hora = request.form.get('hora')
    minuto = request.form.get('minuto')

    erro = validar_dados_refeicao(descricao, hora, minuto)
    if erro:
        flash(erro, 'erro')
        return render_template('nova_refeicao.html', paciente=paciente, calcular_idade=calcular_idade, descricao=descricao, hora=hora, minuto=minuto)
    
    try:
        refeicao = Refeicoes()
        refeicao.descricao = descricao
        refeicao.horario = f"{hora}:{minuto}:00"
        refeicao.id_paciente = id_paciente
        db.session.add(refeicao)
        db.session.commit()
        flash('Nova refeição incluída com sucesso', 'sucesso')
    except Exception as erro:
        print(erro)
        flash('Ocorreu um erro ao incluir a nova refeição: ' + erro, 'erro')
    
    return redirect(url_for('painel.dados_paciente', id_paciente=id_paciente))


@painel.route('/detalhes_refeicao/<int:id_refeicao>', methods=['GET', 'POST'])
@login_required
def detalhes_refeicao(id_refeicao):
    refeicao = Refeicoes.query.filter(Refeicoes.id == id_refeicao).first()

    if not refeicao:
        flash('Não existe refeição com o ID informado.', 'erro')
        return redirect(url_for('painel_pacientes'))

    paciente = consultar_paciente(refeicao.id_paciente)

    return render_template('detalhes_refeicao.html', refeicao=refeicao, paciente=paciente, grupos=Grupos, dados_alimentos=consultar_alimentos_refeicao(id_refeicao), calcular_idade=calcular_idade)


@painel.route('/adicionar_alimento/<int:id_refeicao>', methods=['GET', 'POST'])
@login_required
def adicionar_alimento(id_refeicao):
    refeicao = Refeicoes.query.filter(Refeicoes.id == id_refeicao).first()

    if not refeicao:
        flash('Não existe refeição com o ID informado.', 'erro')
        return redirect(url_for('painel_pacientes'))

    paciente = consultar_paciente(refeicao.id_paciente)

    id_alimento = request.form.get('id_alimento')
    quantidade = request.form.get('quantidade')

    alimento_refeicao = AlimentosRefeicao.query.filter((AlimentosRefeicao.id_refeicao == id_refeicao) & (AlimentosRefeicao.id_alimento == id_alimento)).first()

    if not alimento_refeicao:
        alimento_refeicao = AlimentosRefeicao()
        alimento_refeicao.id_refeicao = id_refeicao
        alimento_refeicao.id_alimento = id_alimento
        alimento_refeicao.quantidade = quantidade
        db.session.add(alimento_refeicao)
    else:
        alimento_refeicao.quantidade = quantidade
    db.session.commit()

    return jsonify(consultar_alimentos_refeicao(id_refeicao))


@painel.route('/excluir_alimento/<int:id_refeicao>', methods=['GET', 'POST'])
@login_required
def excluir_alimento(id_refeicao):
    refeicao = Refeicoes.query.filter(Refeicoes.id == id_refeicao).first()

    if not refeicao:
        flash('Não existe refeição com o ID informado.', 'erro')
        return redirect(url_for('painel_pacientes'))

    paciente = consultar_paciente(refeicao.id_paciente)

    id = request.form.get('id')

    alimento_refeicao = AlimentosRefeicao.query.filter((AlimentosRefeicao.id_refeicao == id_refeicao) & (AlimentosRefeicao.id == id)).first()
    print("==> alimento_refeicao", alimento_refeicao)

    if alimento_refeicao:
        db.session.delete(alimento_refeicao)
        db.session.commit()

    return jsonify(consultar_alimentos_refeicao(id_refeicao))


def consultar_paciente(id_paciente):
    paciente = Pacientes.query.filter((Pacientes.id == id_paciente) & (Pacientes.id_usuario == current_user.id)).first()

    if not paciente:
        flash('Não existe paciente com o ID informado.', 'erro')
        return redirect(url_for('painel.pacientes'))
    
    return paciente


def consultar_alimentos_refeicao(id_refeicao):
    alimentos_refeicao = AlimentosRefeicao.query.filter(AlimentosRefeicao.id_refeicao == id_refeicao).all()

    alimentos = []
    totais = {'quantidade': 0, 'proteina': 0, 'lipideos': 0, 'carboidratos': 0, 'energia_kcal': 0}
    for alimento_refeicao in alimentos_refeicao:
        alimento = Alimentos.query.filter(Alimentos.id == alimento_refeicao.id_alimento).first()
        proteina = (alimento.proteina * (alimento_refeicao.quantidade / 100)) if alimento.proteina else 0
        lipideos = (alimento.lipideos * (alimento_refeicao.quantidade / 100)) if alimento.lipideos else 0
        carboidratos = (alimento.carboidratos * (alimento_refeicao.quantidade / 100)) if alimento.carboidratos else 0
        energia_kcal = (alimento.energia_kcal * (alimento_refeicao.quantidade / 100)) if alimento.energia_kcal else 0
        alimentos.append({
            'id': alimento_refeicao.id, 
            'descricao': alimento.descricao, 
            'quantidade': alimento_refeicao.quantidade,
            'proteina': round(proteina, 2),
            'lipideos': round(lipideos, 2),
            'carboidratos': round(carboidratos, 2),
            'energia_kcal': round(energia_kcal, 2)
        })
        totais['quantidade'] += alimento_refeicao.quantidade
        totais['proteina'] += proteina
        totais['lipideos'] += lipideos
        totais['carboidratos'] += carboidratos
        totais['energia_kcal'] += energia_kcal

    totais['quantidade'] = round(totais['quantidade'], 2)
    totais['proteina'] = round(totais['proteina'], 2)
    totais['lipideos'] = round(totais['lipideos'], 2)
    totais['carboidratos'] = round(totais['carboidratos'], 2)
    totais['energia_kcal'] = round(totais['energia_kcal'], 2)

    return {'alimentos': alimentos, 'totais': totais}


def calcular_idade(data_nascimento):
    delta = date.today() - data_nascimento
    return int(delta.days / 365.25)


def validar_dados_paciente(nome, dia_nasc, mes_nasc, ano_nasc):
    erro = None

    if not nome:
        erro = 'Preencha o nome do paciente.'
    
    if not dia_nasc or not mes_nasc or not ano_nasc:
        erro = 'Preencha a data de nascimento do paciente.'

    return erro


def validar_dados_refeicao(descricao, hora, minuto):
    erro = None

    if not descricao:
        erro = 'Preencha a descrição da refeição.'

    if not hora or not minuto:
        erro = 'Preencha o horário da refeição.'

    return erro
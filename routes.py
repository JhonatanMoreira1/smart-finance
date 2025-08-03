from flask import render_template, request, redirect, url_for, flash, send_file, Blueprint
from sqlalchemy import extract, text
from datetime import datetime
from models import db, Produto, Entrada, Saida, Servico
from flask_login import login_required
from utils import filtros_data, to_float
import os
import subprocess
import tempfile

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/produtos', methods=['GET', 'POST'])
@login_required
def produtos():
    if request.method == 'POST':
        nome = request.form['nome']
        preco_venda = float(request.form['preco_venda'])
        custo = float(request.form['custo'])
        estoque = int(request.form['estoque'])
        novo_produto = Produto(nome=nome, tipo="Produto", preco_venda=preco_venda, custo=custo, estoque=estoque)
        db.session.add(novo_produto)
        db.session.commit()
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('main.produtos'))
    
    query = request.args.get('q')
    if query:
        produtos_query = Produto.query.filter(Produto.nome.ilike(f'%{query}%'))
    else:
        produtos_query = Produto.query

    produtos = produtos_query.order_by(Produto.nome).all()
    
    custo_total_estoque = sum(p.custo * p.estoque for p in produtos)
    valor_total_estoque = sum(p.preco_venda * p.estoque for p in produtos)
    
    return render_template('produtos.html', 
                           produtos=produtos, 
                           custo_total_estoque=custo_total_estoque, 
                           valor_total_estoque=valor_total_estoque,
                           query=query)

@main_bp.route('/entradas', methods=['GET', 'POST'])
@login_required
def entradas():
    if request.method == 'POST':
        produto_id = request.form['produto_id']
        quantidade = int(request.form['quantidade'])
        custo_unitario = float(request.form['custo_unitario'])
        total_custo = quantidade * custo_unitario

        produto = Produto.query.get(produto_id)
        produto.estoque += quantidade

        nova_entrada = Entrada(produto_id=produto_id, quantidade=quantidade, custo_unitario=custo_unitario, total_custo=total_custo)
        db.session.add(nova_entrada)
        db.session.commit()
        flash('Entrada registrada com sucesso!', 'success')
        return redirect(url_for('main.entradas'))

    entradas = Entrada.query.order_by(Entrada.data.desc()).all()
    produtos = Produto.query.all()
    
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    valor_gasto_reposicoes = db.session.query(db.func.sum(Entrada.total_custo)).filter(
        extract('month', Entrada.data) == mes_atual,
        extract('year', Entrada.data) == ano_atual
    ).scalar() or 0
    
    return render_template('entradas.html', entradas=entradas, produtos=produtos, valor_gasto_reposicoes=valor_gasto_reposicoes)

@main_bp.route('/saidas', methods=['GET', 'POST'])
@login_required
def saidas():
    if request.method == 'POST':
        produto_id = request.form['produto_id']
        quantidade = int(request.form['quantidade'])
        preco_unitario = float(request.form['preco_unitario'])
        total_venda = quantidade * preco_unitario
        forma_pagamento = request.form['forma_pagamento']
        cliente = request.form['cliente']

        produto = Produto.query.get(produto_id)
        produto.estoque -= quantidade

        nova_saida = Saida(produto_id=produto_id, quantidade=quantidade, preco_unitario=preco_unitario, total_venda=total_venda, forma_pagamento=forma_pagamento, cliente=cliente)
        db.session.add(nova_saida)
        db.session.commit()
        flash('Saída registrada com sucesso!', 'success')
        return redirect(url_for('main.saidas'))

    saidas = Saida.query.order_by(Saida.data.desc()).all()
    produtos = Produto.query.all()
    return render_template('saidas.html', saidas=saidas, produtos=produtos)

@main_bp.route('/relatorios')
@login_required
def relatorios():
    now = datetime.now()
    mes = request.args.get('mes', default=now.month, type=int)
    ano = request.args.get('ano', default=now.year, type=int)

    # Confere se o checkbox está marcado
    mes_inteiro = 'mes_inteiro' in request.args

    # Define o dia
    if mes_inteiro:
        dia = None
    else:
        dia = request.args.get('dia', type=int)
        if not dia or dia < 1 or dia > 31:
            dia = now.day  # define o dia atual como fallback


    # Filtros e dados
    filtros_saida = filtros_data(Saida, 'data', dia, mes, ano)
    saidas_no_periodo = Saida.query.filter(*filtros_saida).all()

    receita_total_produtos = db.session.query(db.func.sum(Saida.total_venda)).filter(*filtros_saida).scalar() or 0

    filtros_entrada = filtros_data(Entrada, 'data', dia, mes, ano)
    entradas_no_periodo = Entrada.query.filter(*filtros_entrada).all()
    valor_gasto_reposicoes = db.session.query(db.func.sum(Entrada.total_custo)).filter(*filtros_entrada).scalar() or 0

    filtros_servico = filtros_data(Servico, 'data_hora', dia, mes, ano)
    filtros_servico.append(Servico.status == 'Finalizado')
    servicos_finalizados = Servico.query.filter(*filtros_servico).all()

    # Separar Revendas dos outros serviços
    servicos_revenda = [s for s in servicos_finalizados if s.servico_descricao.startswith('[REVENDA]')]
    outros_servicos = [s for s in servicos_finalizados if not s.servico_descricao.startswith('[REVENDA]')]

    # Cálculos para Revendas
    receita_revendas = sum(s.preco_aparelho for s in servicos_revenda)
    custo_revendas = sum(s.custo_pecas for s in servicos_revenda)
    lucro_revendas = receita_revendas - custo_revendas

    # Cálculos para Outros Serviços (Manutenção e Reformas)
    receita_outros_servicos = sum(
        s.preco_aparelho if s.tipo == 'Venda de Aparelho' else s.mao_de_obra
        for s in outros_servicos
    )
    custo_outros_servicos = sum(s.custo_pecas for s in outros_servicos)
    lucro_outros_servicos = receita_outros_servicos - custo_outros_servicos


    custo_total_produtos = sum(saida.produto.custo * saida.quantidade for saida in saidas_no_periodo)
    lucro_produtos = receita_total_produtos - custo_total_produtos

    return render_template(
        'relatorios.html',
        receita_total_produtos=receita_total_produtos,
        custo_total_produtos=custo_total_produtos,
        lucro_produtos=lucro_produtos,
        valor_gasto_reposicoes=valor_gasto_reposicoes,
        
        receita_servicos=receita_outros_servicos,
        custo_servicos=custo_outros_servicos,
        lucro_servicos=lucro_outros_servicos,

        receita_revendas=receita_revendas,
        custo_revendas=custo_revendas,
        lucro_revendas=lucro_revendas,

        dia=dia,
        mes=mes,
        ano=ano,
        now=now,
        mes_inteiro=mes_inteiro
    )

@main_bp.route('/edit_product/<int:id>', methods=['POST'])
@login_required
def edit_product(id):
    produto = Produto.query.get_or_404(id)
    produto.nome = request.form['nome']
    produto.preco_venda = float(request.form['preco_venda'])
    produto.custo = float(request.form['custo'])
    produto.estoque = int(request.form['estoque'])
    db.session.commit()
    flash('Produto atualizado com sucesso!', 'success')
    return redirect(url_for('main.produtos'))


@main_bp.route('/delete_produto/<int:id>', methods=['POST'])
@login_required
def delete_produto(id):
    produto = Produto.query.get_or_404(id)

    entradas_associadas = Entrada.query.filter_by(produto_id=id).first()
    saidas_associadas = Saida.query.filter_by(produto_id=id).first()

    if entradas_associadas or saidas_associadas:
        flash('Existem entradas e/ou saídas desse produto, exclua-as para continuar.', 'danger')
        return redirect(url_for('main.produtos'))

    is_last_product = Produto.query.count() == 1

    db.session.delete(produto)
    db.session.commit()

    if is_last_product:
        try:
            db.session.execute(text('ALTER SEQUENCE produtos_id_seq RESTART WITH 1'))
            db.session.commit()
            flash('Produto deletado e sequência de IDs reiniciada.', 'success')
        except Exception as e:
            flash(f'Produto deletado, mas falha ao reiniciar a sequência de IDs: {e}', 'warning')
    else:
        flash('Produto deletado com sucesso!', 'success')

    return redirect(url_for('main.produtos'))

@main_bp.route('/edit_entrada/<int:id>', methods=['POST'])
@login_required
def edit_entrada(id):
    entrada = Entrada.query.get_or_404(id)
    produto = Produto.query.get(entrada.produto_id)

    quantidade_antiga = entrada.quantidade
    quantidade_nova = int(request.form['quantidade'])
    produto.estoque = produto.estoque - quantidade_antiga + quantidade_nova

    entrada.quantidade = quantidade_nova
    entrada.custo_unitario = float(request.form['custo_unitario'])
    entrada.total_custo = entrada.quantidade * entrada.custo_unitario
    
    db.session.commit()
    flash('Entrada atualizada com sucesso!', 'success')
    return redirect(url_for('main.entradas'))


@main_bp.route('/delete_entrada/<int:id>', methods=['POST'])
@login_required
def delete_entrada(id):
    entrada = Entrada.query.get_or_404(id)
    produto = Produto.query.get(entrada.produto_id)
    produto.estoque -= entrada.quantidade
    db.session.delete(entrada)
    db.session.commit()
    flash('Entrada deletada com sucesso!', 'success')
    return redirect(url_for('main.entradas'))

@main_bp.route('/servicos', methods=['GET', 'POST'])
@login_required
def servicos():
    if request.method == 'POST':
        servico_descricao = request.form['servico_descricao']
        aparelho = request.form.get('aparelho')
        tipo = request.form.get('tipo')
        subtipo_venda = request.form.get('subtipo_venda')

        if tipo == 'Venda de Aparelho' and subtipo_venda == 'Revenda':
            servico_descricao = f"[REVENDA] {servico_descricao}"

        status = request.form['status']
        custo_pecas = float(request.form.get('custo_pecas', 0.0))
        mao_de_obra = 0.0
        preco_aparelho = 0.0

        if tipo == 'Manutenção':
            mao_de_obra = float(request.form.get('mao_de_obra', 0.0))
        elif tipo == 'Venda de Aparelho':
            preco_aparelho = float(request.form.get('preco_aparelho', 0.0))

        forma_pagamento = request.form.get('forma_pagamento')
        cliente = request.form.get('cliente')

        novo_servico = Servico(servico_descricao=servico_descricao, aparelho=aparelho, tipo=tipo,
                               custo_pecas=custo_pecas, mao_de_obra=mao_de_obra,
                               preco_aparelho=preco_aparelho, status=status, forma_pagamento=forma_pagamento, cliente=cliente)
        db.session.add(novo_servico)
        db.session.commit()
        flash('Serviço adicionado com sucesso!', 'success')
        return redirect(url_for('main.servicos'))

    servicos = Servico.query.order_by(Servico.data_hora.desc()).all()
    return render_template('servicos.html', servicos=servicos)


@main_bp.route('/nota_servico/<int:servico_id>')
@login_required
def nota_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    cnpj = os.getenv('CNPJ_LOJA', '00.000.000/0000-00')
    nome_loja = os.getenv('NOME_LOJA', 'Minha Loja')
    telefone = os.getenv('TEL_LOJA', '00 00000-0000')

    return render_template('nota_servico.html',
                           servico=servico,
                           cnpj=cnpj,
                           nome_loja=nome_loja,
                           telefone=telefone)


@main_bp.route('/nota_produto/<int:saida_id>')
@login_required
def nota_produto(saida_id):
    saida = Saida.query.get_or_404(saida_id)
    cnpj = os.getenv('CNPJ_LOJA', '00.000.000/0000-00')
    nome_loja = os.getenv('NOME_LOJA', 'Minha Loja')
    telefone = os.getenv('TEL_LOJA', '00 00000-0000')
    return render_template('nota_produto.html',
                           saida=saida,
                            cnpj=cnpj,
                            nome_loja=nome_loja,
                            telefone=telefone)

@main_bp.route('/edit_saida/<int:id>', methods=['POST'])
@login_required
def edit_saida(id):
    saida = Saida.query.get_or_404(id)
    produto = Produto.query.get(saida.produto_id)

    quantidade_antiga = saida.quantidade
    quantidade_nova = int(request.form['quantidade'])
    produto.estoque = produto.estoque + quantidade_antiga - quantidade_nova

    saida.quantidade = quantidade_nova
    saida.preco_unitario = float(request.form['preco_unitario'])
    saida.total_venda = saida.quantidade * saida.preco_unitario
    saida.forma_pagamento = request.form['forma_pagamento']
    saida.cliente = request.form['cliente']
    
    db.session.commit()
    flash('Saída atualizada com sucesso!', 'success')
    return redirect(url_for('main.saidas'))


@main_bp.route('/delete_saida/<int:id>', methods=['POST'])
@login_required
def delete_saida(id):
    saida = Saida.query.get_or_404(id)
    produto = Produto.query.get(saida.produto_id)
    produto.estoque += saida.quantidade
    db.session.delete(saida)
    db.session.commit()
    flash('Saída deletada com sucesso!', 'success')
    return redirect(url_for('main.saidas'))

@main_bp.route('/edit_servico/<int:id>', methods=['POST'])
@login_required
def edit_servico(id):
    servico = Servico.query.get_or_404(id)
    
    servico_descricao = request.form['servico_descricao'].replace('[REVENDA]', '').strip()
    tipo = request.form['tipo']
    subtipo_venda = request.form.get(f'subtipo_venda_{id}')

    if tipo == 'Venda de Aparelho' and subtipo_venda == 'Revenda':
        servico.servico_descricao = f"[REVENDA] {servico_descricao}"
    else:
        servico.servico_descricao = servico_descricao

    servico.aparelho = request.form.get('aparelho')
    servico.tipo = tipo
    servico.forma_pagamento = request.form.get('forma_pagamento')
    servico.cliente = request.form.get('cliente')
    
    custo_pecas_str = request.form.get('custo_pecas', '0.0')
    servico.custo_pecas = float(custo_pecas_str) if custo_pecas_str.strip() else 0.0
    
    if servico.tipo == 'Manutenção':
        servico.mao_de_obra = to_float(request.form.get('mao_de_obra'))
        servico.preco_aparelho = 0.0
    elif servico.tipo == 'Venda de Aparelho':
        servico.preco_aparelho = to_float(request.form.get('preco_aparelho'))
        servico.mao_de_obra = 0.0
    else:
        servico.mao_de_obra = 0.0
        servico.preco_aparelho = 0.0

    novo_status = request.form['status']
    
    servico.status = novo_status
    
    db.session.commit()
    flash('Serviço atualizado com sucesso!', 'success')
    return redirect(url_for('main.servicos'))

@main_bp.route('/delete_servico/<int:id>', methods=['POST'])
@login_required
def delete_servico(id):
    servico = Servico.query.get_or_404(id)
    db.session.delete(servico)
    db.session.commit()
    flash('Serviço deletado com sucesso!', 'success')
    return redirect(url_for('main.servicos'))


@main_bp.route('/backup', methods=['GET'])
@login_required
def backup_database():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_port = os.getenv('DB_PORT')

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.sql') as temp_file:
        backup_file_path = temp_file.name

    try:
        os.environ['PGPASSWORD'] = db_password
        
        command = [
            'pg_dump',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-F', 'p',
            '-d', db_name,
            '-f', backup_file_path
        ]
        
        process = subprocess.run(command, check=True, capture_output=True)
        flash('Backup do banco de dados criado com sucesso!', 'success')
        return send_file(backup_file_path, as_attachment=True, download_name=f'smart_finance_backup_{datetime.now().strftime("%Y%m%d%H%M%S")}.sql')
    except subprocess.CalledProcessError as e:
        flash(f'Erro ao criar backup: {e.stderr.decode()}', 'danger')
        return redirect(url_for('main.index'))
    except Exception as e:
        flash(f'Ocorreu um erro inesperado ao criar o backup: {str(e)}', 'danger')
        return redirect(url_for('main.index'))
    finally:
        if os.path.exists(backup_file_path):
            os.remove(backup_file_path)
        if 'PGPASSWORD' in os.environ:
            del os.environ['PGPASSWORD']

@main_bp.route('/restore', methods=['POST'])
@login_required
def restore_database():
    if 'backup_file' not in request.files:
        flash('Nenhum arquivo selecionado para restauração.', 'danger')
        return redirect(url_for('main.index'))

    backup_file = request.files['backup_file']
    if backup_file.filename == '':
        flash('Nenhum arquivo selecionado para restauração.', 'danger')
        return redirect(url_for('main.index'))

    if backup_file and backup_file.filename.endswith('.sql'):
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')
        db_port = os.getenv('DB_PORT')

        with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix='.sql') as temp_file:
            temp_file.write(backup_file.read())
            uploaded_file_path = temp_file.name

        try:
            os.environ['PGPASSWORD'] = db_password

            disconnect_command = [
                'psql',
                '-h', db_host,
                '-p', db_port,
                '-U', db_user,
                '-d', 'postgres',
                '-c', f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{db_name}' AND pid <> pg_backend_pid();"
            ]
            subprocess.run(disconnect_command, check=True, capture_output=True)

            drop_db_command = [
                'dropdb',
                '-h', db_host,
                '-p', db_port,
                '-U', db_user,
                db_name
            ]
            subprocess.run(drop_db_command, check=True, capture_output=True)

            create_db_command = [
                'createdb',
                '-h', db_host,
                '-p', db_port,
                '-U', db_user,
                db_name
            ]
            subprocess.run(create_db_command, check=True, capture_output=True)

            restore_command = [
                'psql',
                '-h', db_host,
                '-p', db_port,
                '-U', db_user,
                '-d', db_name,
                '-f', uploaded_file_path
            ]
            
            process = subprocess.run(restore_command, check=True, capture_output=True)
            flash('Banco de dados restaurado com sucesso!', 'success')
        except subprocess.CalledProcessError as e:
            flash(f'Erro ao restaurar banco de dados: {e.stderr.decode()}', 'danger')
        except Exception as e:
            flash(f'Ocorreu um erro inesperado ao restaurar o banco de dados: {str(e)}', 'danger')
        finally:
            if os.path.exists(uploaded_file_path):
                os.remove(uploaded_file_path)
            if 'PGPASSWORD' in os.environ:
                del os.environ['PGPASSWORD']
    else:
        flash('Formato de arquivo inválido. Por favor, envie um arquivo .sql.', 'danger')
    
    return redirect(url_for('main.index'))

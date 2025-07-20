import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from sqlalchemy import extract, text
from datetime import datetime
from models import db, Produto, Entrada, Saida
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import subprocess
import tempfile

load_dotenv()

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'uma_chave_secreta_muito_segura') # Use uma chave forte em produção
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Classe de usuário para Flask-Login (usuário único fixo)
class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    # Como temos um usuário fixo, sempre retornamos o mesmo objeto User
    if user_id == '1': # ID fixo para o usuário único
        return User(1)
    return None

# Usuário e senha fixos (para fins de demonstração)
FIXED_USERNAME = os.getenv('APP_USERNAME', 'admin')
FIXED_PASSWORD = os.getenv('APP_PASSWORD', 'smarttym2023')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == FIXED_USERNAME and password == FIXED_PASSWORD:
            user = User(1)  # ID fixo para o usuário único
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login falhou. Verifique seu usuário e senha.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/produtos', methods=['GET', 'POST'])
@login_required
def produtos():
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        preco_venda = float(request.form['preco_venda'])
        custo = float(request.form['custo'])
        estoque = int(request.form['estoque'])
        novo_produto = Produto(nome=nome, tipo=tipo, preco_venda=preco_venda, custo=custo, estoque=estoque)
        db.session.add(novo_produto)
        db.session.commit()
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('produtos'))
    
    produtos = Produto.query.order_by(Produto.id).all()
    return render_template('produtos.html', produtos=produtos)

@app.route('/entradas', methods=['GET', 'POST'])
@login_required
def entradas():
    if request.method == 'POST':
        produto_id = request.form['produto_id']
        quantidade = int(request.form['quantidade'])
        custo_unitario = float(request.form['custo_unitario'])
        total_custo = quantidade * custo_unitario

        # Atualiza o estoque do produto
        produto = Produto.query.get(produto_id)
        produto.estoque += quantidade

        nova_entrada = Entrada(produto_id=produto_id, quantidade=quantidade, custo_unitario=custo_unitario, total_custo=total_custo)
        db.session.add(nova_entrada)
        db.session.commit()
        flash('Entrada registrada com sucesso!', 'success')
        return redirect(url_for('entradas'))

    entradas = Entrada.query.order_by(Entrada.data.desc()).all()
    produtos = Produto.query.all()
    return render_template('entradas.html', entradas=entradas, produtos=produtos)

@app.route('/saidas', methods=['GET', 'POST'])
@login_required
def saidas():
    if request.method == 'POST':
        produto_id = request.form['produto_id']
        quantidade = int(request.form['quantidade'])
        preco_unitario = float(request.form['preco_unitario'])
        total_venda = quantidade * preco_unitario
        forma_pagamento = request.form['forma_pagamento']
        cliente = request.form['cliente']

        # Atualiza o estoque do produto
        produto = Produto.query.get(produto_id)
        produto.estoque -= quantidade

        nova_saida = Saida(produto_id=produto_id, quantidade=quantidade, preco_unitario=preco_unitario, total_venda=total_venda, forma_pagamento=forma_pagamento, cliente=cliente)
        db.session.add(nova_saida)
        db.session.commit()
        flash('Saída registrada com sucesso!', 'success')
        return redirect(url_for('saidas'))

    saidas = Saida.query.order_by(Saida.data.desc()).all()
    produtos = Produto.query.all()
    return render_template('saidas.html', saidas=saidas, produtos=produtos)

@app.route('/relatorios')
@login_required
def relatorios():
    mes = request.args.get('mes', default=datetime.now().month, type=int)
    ano = request.args.get('ano', default=datetime.now().year, type=int)

    receita_total = db.session.query(db.func.sum(Saida.total_venda)).filter(
        extract('month', Saida.data) == mes,
        extract('year', Saida.data) == ano
    ).scalar() or 0

    custo_total = db.session.query(db.func.sum(Entrada.total_custo)).filter(
        extract('month', Entrada.data) == mes,
        extract('year', Entrada.data) == ano
    ).scalar() or 0

    lucro = receita_total - custo_total

    return render_template('relatorios.html',
                           receita_total=receita_total,
                           custo_total=custo_total,
                           lucro=lucro,
                           mes=mes,
                           ano=ano)


@app.route('/delete_produto/<int:id>', methods=['POST'])
@login_required
def delete_produto(id):
    produto = Produto.query.get_or_404(id)

    # Verifica se existem entradas ou saídas associadas a este produto
    entradas_associadas = Entrada.query.filter_by(produto_id=id).first()
    saidas_associadas = Saida.query.filter_by(produto_id=id).first()

    if entradas_associadas or saidas_associadas:
        flash('Existem entradas e/ou saídas desse produto, exclua-as para continuar.', 'danger')
        return redirect(url_for('produtos'))

    # Verifica se este é o último produto
    is_last_product = Produto.query.count() == 1

    db.session.delete(produto)
    db.session.commit()

    # Se era o último produto, reseta a sequência de IDs
    if is_last_product:
        try:
            # O nome da sequência geralmente é <nome_tabela>_<nome_coluna>_seq
            db.session.execute(text('ALTER SEQUENCE produtos_id_seq RESTART WITH 1'))
            db.session.commit()
            flash('Produto deletado e sequência de IDs reiniciada.', 'success')
        except Exception as e:
            flash(f'Produto deletado, mas falha ao reiniciar a sequência de IDs: {e}', 'warning')
    else:
        flash('Produto deletado com sucesso!', 'success')

    return redirect(url_for('produtos'))

@app.route('/delete_entrada/<int:id>', methods=['POST'])
@login_required
def delete_entrada(id):
    entrada = Entrada.query.get_or_404(id)
    produto = Produto.query.get(entrada.produto_id)
    produto.estoque -= entrada.quantidade # Reverte o estoque
    db.session.delete(entrada)
    db.session.commit()
    flash('Entrada deletada com sucesso!', 'success')
    return redirect(url_for('entradas'))

@app.route('/delete_saida/<int:id>', methods=['POST'])
@login_required
def delete_saida(id):
    saida = Saida.query.get_or_404(id)
    produto = Produto.query.get(saida.produto_id)
    produto.estoque += saida.quantidade # Reverte o estoque
    db.session.delete(saida)
    db.session.commit()
    flash('Saída deletada com sucesso!', 'success')
    return redirect(url_for('saidas'))


@app.route('/backup', methods=['GET'])
@login_required
def backup_database():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_port = os.getenv('DB_PORT')

    # Create a temporary file to store the backup
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.sql') as temp_file:
        backup_file_path = temp_file.name

    try:
        # Set PGPASSWORD environment variable for pg_dump
        os.environ['PGPASSWORD'] = db_password
        
        # pg_dump command
        command = [
            'pg_dump',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-F', 'p', # plain text SQL dump
            '-d', db_name,
            '-f', backup_file_path # output file
        ]
        
        process = subprocess.run(command, check=True, capture_output=True)
        flash('Backup do banco de dados criado com sucesso!', 'success')
        return send_file(backup_file_path, as_attachment=True, download_name=f'smart_finance_backup_{datetime.now().strftime("%Y%m%d%H%M%S")}.sql')
    except subprocess.CalledProcessError as e:
        flash(f'Erro ao criar backup: {e.stderr.decode()}', 'danger')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Ocorreu um erro inesperado ao criar o backup: {str(e)}', 'danger')
        return redirect(url_for('index'))
    finally:
        # Clean up the temporary file
        if os.path.exists(backup_file_path):
            os.remove(backup_file_path)
        if 'PGPASSWORD' in os.environ:
            del os.environ['PGPASSWORD']

@app.route('/restore', methods=['POST'])
@login_required
def restore_database():
    if 'backup_file' not in request.files:
        flash('Nenhum arquivo selecionado para restauração.', 'danger')
        return redirect(url_for('index'))

    backup_file = request.files['backup_file']
    if backup_file.filename == '':
        flash('Nenhum arquivo selecionado para restauração.', 'danger')
        return redirect(url_for('index'))

    if backup_file and backup_file.filename.endswith('.sql'):
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')
        db_port = os.getenv('DB_PORT')

        # Create a temporary file to save the uploaded backup
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix='.sql') as temp_file:
            temp_file.write(backup_file.read())
            uploaded_file_path = temp_file.name

        try:
            # Set PGPASSWORD environment variable for psql
            os.environ['PGPASSWORD'] = db_password

            # Drop existing connections to the database
            # This is crucial for a successful restore
            disconnect_command = [
                'psql',
                '-h', db_host,
                '-p', db_port,
                '-U', db_user,
                '-d', 'postgres', # Connect to a different database to drop connections to the target DB
                '-c', f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{db_name}' AND pid <> pg_backend_pid();"
            ]
            subprocess.run(disconnect_command, check=True, capture_output=True)

            # psql command to restore the database
            # We need to drop and recreate the database for a clean restore
            # This will delete all data in the current database!
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
            # Clean up the temporary file
            if os.path.exists(uploaded_file_path):
                os.remove(uploaded_file_path)
            if 'PGPASSWORD' in os.environ:
                del os.environ['PGPASSWORD']
    else:
        flash('Formato de arquivo inválido. Por favor, envie um arquivo .sql.', 'danger')
    
    return redirect(url_for('index'))

if __name__ == "__main__":
      port = int(os.environ.get("PORT", 5000))
      app.run(host="0.0.0.0", port=port)
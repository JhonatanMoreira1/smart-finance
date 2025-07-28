# Smart Finance
<img src="/static/favicon.ico" alt="Smart Finance Logo" width="215" height="215">

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.2-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-14-blue.svg)
![Bootstrap](https://img.shields.io/badge/bootstrap-5-purple.svg)

**Smart Finance** é uma aplicação web simples e prática para o controle financeiro de loja, com foco em gestão de produtos, controle de estoque e relatórios financeiros.

## ✨ Funcionalidades

- **Gestão de Produtos/Serviços:** Adicione, liste e delete produtos ou serviços, definindo nome, tipo, preço de venda, custo e estoque inicial.
- **Controle de Estoque:**
  - **Entradas:** Registre compras de produtos, atualizando automaticamente o estoque.
  - **Saídas:** Registre vendas, subtraindo a quantidade do estoque.
- **Relatórios Financeiros:** Visualize a receita total, custos e lucro, com filtros por mês e ano.
- **Autenticação de Usuário:** Sistema de login com usuário único para proteger o acesso aos dados.
- **Backup e Restauração:**
  - **Backup:** Gere e baixe um backup completo do banco de dados em formato `.sql` com um único clique.
  - **Restauração:** Restaure o banco de dados a partir de um arquivo de backup `.sql`.

---

## 🚀 Tecnologias Utilizadas

- **Backend:** Flask (Python)
- **Banco de Dados:** PostgreSQL com SQLAlchemy
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Autenticação:** Flask-Login
- **Servidor de Produção:** Gunicorn

---

## ⚙️ Configuração e Instalação

Siga os passos abaixo para configurar e rodar o projeto em um ambiente local.

### **Pré-requisitos**

- Python 3.10+
- PostgreSQL
- Git

### **Passos**

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd smart-finance
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Para Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    - Copie o arquivo de exemplo:
      ```bash
      cp .env.example .env
      ```
    - Edite o arquivo `.env` com suas credenciais. Ele deve se parecer com isto:
      ```makefile
      # Configuração do Banco de Dados (PostgreSQL)
      DB_HOST=localhost
      DB_NAME=smart_finance
      DB_USER=seu_usuario_aqui
      DB_PASSWORD=sua_senha_aqui
      DB_PORT=5432

      # Chave Secreta da Aplicação (use um valor longo e aleatório)
      SECRET_KEY=sua_chave_secreta_super_segura_aqui

      # Credenciais de Login da Aplicação
      APP_USERNAME=admin
      APP_PASSWORD=admin123
      ```
    - **Importante:** A `SECRET_KEY` deve ser uma string longa e aleatória para segurança.

5.  **Crie o banco de dados no PostgreSQL:**
    - Certifique-se de que seu servidor PostgreSQL está rodando.
    - Crie um banco de dados com o mesmo nome que você definiu em `DB_NAME`.

6.  **Inicialize as tabelas do banco de dados:**
    - Este comando criará todas as tabelas necessárias para a aplicação.
    ```bash
    python init_db.py
    ```

7.  **Rode a aplicação:**
    ```bash
    python app.py
    ```
    - A aplicação estará disponível em `http://127.0.0.1:5000`.

---

## 📖 Como Usar

### **Login**

- Acesse a aplicação no seu navegador.
- Use as credenciais (`APP_USERNAME` e `APP_PASSWORD`) definidas no seu arquivo `.env` para fazer login.

### **Gestão de Dados**

- Navegue pelas seções **Produtos**, **Entradas** e **Saídas** usando o menu superior.
- Em cada seção, você pode:
  - Clicar em **"Adicionar Novo"** para registrar um novo item.
  - Clicar no botão **"Deletar"** ao lado de cada registro para removê-lo.
    - **Aviso:** Não é possível deletar um produto se ele estiver associado a alguma entrada ou saída.

### **Backup e Restauração**

- Na página inicial, você encontrará as opções de gerenciamento do banco de dados:
  - **Fazer Backup:** Clique para baixar um arquivo `.sql` com o estado atual do banco de dados.
  - **Restaurar:** Faça o upload de um arquivo `.sql` para restaurar o banco.
    - **⚠️ CUIDADO:** A restauração é uma operação destrutiva. Ela apagará todos os dados atuais e os substituirá pelo conteúdo do arquivo de backup.

---

## ☁️ Deploy

Este projeto está pronto para ser implantado em plataformas como o Render, usando um banco de dados como o Neon.

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`


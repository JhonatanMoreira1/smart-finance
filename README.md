# Smart Finance - Sistema de Gestão Financeira
<img src="/static/favicon.ico" alt="Smart Finance Logo" width="215" height="215">

Smart Finance é uma aplicação web desenvolvida em Flask, projetada para auxiliar pequenos negócios no controle de suas operações diárias. O sistema oferece uma interface simples e intuitiva para gerenciar produtos, serviços, estoque e finanças, além de fornecer relatórios detalhados e funcionalidades de segurança de dados.

## ✨ Funcionalidades Principais

O sistema conta com um conjunto robusto de funcionalidades para uma gestão completa:

- **🔐 Autenticação de Usuário:** Acesso seguro à aplicação através de um sistema de login.
- **📦 Gestão de Produtos e Estoque:**
  - Cadastro, edição e exclusão de produtos.
  - Pesquisa de produtos por nome (com busca "contém" para maior flexibilidade).
  - Controle de entradas (compras) e saídas (vendas), com atualização automática do estoque.
  - Cálculo em tempo real do custo e do valor total do inventário.
- **🛠️ Gestão de Serviços:**
  - Registro de serviços de **Manutenção**.
  - Registro de **Venda de Aparelhos**, com subtipos para **Reforma** e **Revenda**.
  - Geração de notas de serviço para impressão, com textos de garantia customizados para cada tipo de serviço.
- **📊 Relatórios Financeiros Detalhados:**
  - Filtros por dia, mês e ano para análises precisas.
  - Resumo financeiro para **Produtos**, incluindo receita, custo e lucro.
  - Resumo financeiro para **Serviços** (Manutenção e Reformas).
  - Bloco separado para análise de **Revenda de Aparelhos**, permitindo uma visão clara da lucratividade deste segmento.
- **⚙️ Segurança e Manutenção:**
  - **Backup:** Crie e baixe um backup completo do banco de dados com um único clique.
  - **Restauração:** Restaure o estado da aplicação a partir de um arquivo de backup.
  - **Tratamento de Erros:** Exibição de uma página de erro amigável em caso de perda de conexão com o banco de dados por inatividade, com a opção de recarregar a página.

## 🚀 Tecnologias Utilizadas

- **Backend:** Flask, SQLAlchemy
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript, jQuery
- **Banco de Dados:** PostgreSQL
- **Autenticação:** Flask-Login
- **Dependências:** `python-dotenv`, `psycopg2-binary`, `gunicorn`

## 🔧 Instalação e Configuração

Para executar o projeto localmente, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd smart-finance
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    - Crie uma cópia do arquivo `.env.example` e renomeie para `.env`.
    - Preencha as variáveis com as suas credenciais do banco de dados PostgreSQL e outras informações:
      ```env
      # Chave secreta para segurança da sessão Flask
      SECRET_KEY='uma_chave_super_secreta'

      # Credenciais do Banco de Dados (PostgreSQL)
      DB_HOST=localhost
      DB_PORT=5432
      DB_NAME=smart_finance_db
      DB_USER=seu_usuario
      DB_PASSWORD=sua_senha

      # Credenciais de Login da Aplicação
      APP_USERNAME=admin
      APP_PASSWORD=suasenhadeadmin

      # Informações da Loja (para as notas de impressão)
      NOME_LOJA="Nome da Sua Loja"
      CNPJ_LOJA="00.000.000/0001-00"
      TEL_LOJA="(00) 90000-0000"
      ```

5.  **Inicialize o banco de dados:**
    - Certifique-se de que o banco de dados especificado no arquivo `.env` exista.
    - Execute o script de inicialização para criar as tabelas:
    ```bash
    python init_db.py
    ```

6.  **Execute a aplicação:**
    ```bash
    python app.py
    ```
    A aplicação estará disponível em `http://127.0.0.1:5000`.
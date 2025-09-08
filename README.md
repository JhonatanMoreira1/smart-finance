# Smart Finance - Gestão para Assistências Técnicas

<p align="center">
  <img src="/static/favicon.ico" alt="Smart Finance Logo" width="200">
</p>

**Smart Finance** é um sistema de gestão completo, desenvolvido sob medida para as necessidades de **assistências técnicas de eletrônicos, técnicos autônomos e pequenas lojas de reparo de celulares e etc**. A aplicação centraliza o controle de serviços, estoque de peças, vendas e o fluxo de caixa em uma interface web rápida, intuitiva e escalável.

## Para Quem é o Smart Finance?

Este sistema foi projetado para resolver os desafios diários de quem trabalha com reparos e vendas no ramo de eletrônicos. Se você precisa:

-   Gerenciar ordens de serviço de **manutenção** e **reparos**.
-   Controlar um inventário de **peças e acessórios** com atualização automática.
-   Registrar a **venda de aparelhos**, diferenciando entre **revendas** e **aparelhos reformados**.
-   Ter uma visão clara do **fluxo de caixa**, com entradas e saídas manuais e automáticas.
-   Entender de forma precisa a **lucratividade** de cada área do seu negócio (serviços, vendas, etc.).

... então o Smart Finance foi feito para você.

## ✨ Funcionalidades em Destaque

-   **📠 Gestão de Serviços Especializada:**
    -   Crie e gerencie ordens de serviço, diferenciando entre **Manutenção**, **Reforma** e **Revenda**.
    -   Gere **notas de serviço** para impressão com termos de garantia específicos para cada tipo de trabalho, passando profissionalismo ao seu cliente.
    -   A data do serviço é atualizada automaticamente ao finalizar um reparo, mantendo um histórico preciso.

-   **📦 Inventário Inteligente:**
    -   Controle total sobre o estoque de peças e produtos.
    -   O estoque é **atualizado automaticamente** em cada entrada (compra de peças) e saída (venda ou uso em um reparo).
    -   Pesquisa rápida e eficiente em todo o inventário.

-   **💵 Controle de Caixa Integrado:**
    -   Uma tela dedicada para o gerenciamento do fluxo de caixa.
    -   Registre entradas (aportes) e retiradas (sangrias) manuais.
    -   As vendas e serviços pagos em dinheiro são **automaticamente registrados como entradas** no caixa, eliminando a necessidade de dupla digitação.

-   **📊 Relatórios Financeiros Claros:**
    -   Filtre suas finanças por dia, mês ou ano.
    -   Visualize de forma separada a receita, o custo e o lucro de:
        -   Venda de Produtos
        -   Serviços de Manutenção e Reforma
        -   Revenda de Aparelhos
    -   Entenda rapidamente quais áreas do seu negócio são mais lucrativas.

-   **🔒 Privacidade e Segurança:**
    -   Oculte valores sensíveis (saldo do caixa, totais de estoque) com um clique, ideal para quando a tela está visível para clientes.
    -   Sistema de **Backup e Restauração** do banco de dados para garantir a segurança das suas informações.

## 🚀 Recursos Técnicos e de Performance

O Smart Finance foi construído com foco em performance e usabilidade a longo prazo.

-   **Escalabilidade O(1):** Todas as telas de listagem (Produtos, Serviços, Caixa, etc.) carregam em **tempo constante**, independentemente do número de registros no banco de dados. Seja com 100 ou 100.000 itens, a aplicação permanece rápida e fluida, graças à paginação inteligente no backend.
-   **Interface Reativa:** O carregamento de novos itens é feito de forma assíncrona, sem a necessidade de recarregar a página, proporcionando uma experiência de uso moderna.
-   **Tratamento de Erros:** Uma página de erro amigável é exibida em caso de falha de conexão com o banco de dados, orientando o usuário a simplesmente recarregar a página.

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
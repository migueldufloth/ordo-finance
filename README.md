# Ordo Finance

Sistema de gestão financeira pessoal desenvolvido com foco em arquitetura orientada a serviços e escalabilidade.

## Visão Geral

A aplicação permite o controle de receitas e despesas, categorização de lançamentos e visualização de balanços financeiros. O projeto foi estruturado para demonstrar a coexistência de um monolito robusto (Django) conectado a um banco de dados na nuvem (PostgreSQL) com microserviços especializados (FastAPI), utilizando conteinerização para orquestração do ambiente.

## Estrutura de Produção e Arquitetura do Sistema

O sistema é composto de serviços dockerizados independentes para facilitar o *deploy* em plataformas na nuvem como **Render.com** ou **Railway**.

*   **App Principal (Django Monolito):** Responsável pelo gerenciamento de usuários, regras de negócio principais e renderização da interface. Em produção, ele opera atrás do **Gunicorn** (multi-workers) e gerencia ativos estáticos através do **WhiteNoise**, impulsionado por um `entrypoint.sh` seguro que realiza as rotinas de banco.
*   **Microserviço (FastAPI):** Unidade focada no isolamento de tarefas intensivas, executado assincronamente através do servidor **Uvicorn**, comunicando-se com o Core via API HTTP.
*   **Banco de Dados (PostgreSQL - Supabase):** Armazenamento relacional centralizado servido como PaaS gratuito.

## Arquitetura C4

Os diagramas abaixo utilizam o padrão **C4 Model** (Context, Container, Component) suportado nativamente pelo Mermaid no GitHub para representar como a aplicação funciona e quem são os envolvidos.

### Nível 1: Diagrama de Contexto

Visão de alto nível mostrando o sistema Ordo Finance, o usuário principal e o provedor de nuvem (Supabase).

```mermaid
C4Context
    title Nível 1: Diagrama de Contexto de Sistema - Ordo Finance
    
    Person(usuario, "Usuário do Sistema", "Acompanha suas finanças, receitas e cartões.")
    
    System(ordo, "Ordo Finance", "Plataforma instalada em PaaS (Ex: Render.com). Entregue via Docker.")
    
    SystemExt(supabase, "Supabase (PostgreSQL)", "PaaS Database que hospeda o Postgres para armazenamento seguro na nuvem.")

    Rel_R(usuario, ordo, "Acessa a interface web via", "HTTPS")
    Rel_R(ordo, supabase, "Lê e grava dados via", "PostgreSQL Protocol")
    
    UpdateElementStyle(usuario, $fontColor="white", $bgColor="#08427B", $borderColor="#052E56")
    UpdateElementStyle(ordo, $fontColor="white", $bgColor="#1168BD", $borderColor="#0B4884")
    UpdateElementStyle(supabase, $fontColor="white", $bgColor="#555555", $borderColor="#333333")
```

### Nível 2: Diagrama de Containers

Decomposição interna do sistema, detalhando o monolito principal (Django), o banco de dados e o microserviço projetado.

```mermaid
C4Container
    title Nível 2: Diagrama de Containers - Ordo Finance
    
    Person(usuario, "Usuário", "Pessoa monitorando finanças")

    System_Boundary(c1, "Nuvem de Hospedagem (Render / Fly.io)") {
        Container(webapp, "App Web Principal", "Docker, Django, Gunicorn", "Monolito SSR responsável pelo Core. Servido confiavelmente com WhiteNoise.")
        Container(api, "Microserviço de Relatórios", "Docker, FastAPI, Uvicorn", "Backend isolado para rotinas sem afetar o Core Web.")
    }
    
    System_Boundary(c2, "Supabase") {
        ContainerDb(db, "Banco de Dados", "PostgreSQL", "Armazena transações, usuários e hashes.")
    }
    
    Rel_R(usuario, webapp, "Acessa páginas via", "HTTPS")
    Rel_D(webapp, api, "Delega geração de PDF via", "REST")
    Rel_D(webapp, db, "Consultas transacionais via", "Django ORM")
    Rel_L(api, db, "Agrega dados via", "SQL puro")
    
    UpdateElementStyle(webapp, $fontColor="white", $bgColor="#1168BD", $borderColor="#0B4884")
    UpdateElementStyle(api, $fontColor="white", $bgColor="#1168BD", $borderColor="#0B4884")
    UpdateElementStyle(db, $fontColor="white", $bgColor="#2D882D", $borderColor="#1B5E1B")
```

### Nível 3: Diagrama de Componentes (Aplicação Web Principal)

Decomposição interna do Container "Aplicação Web Principal", mapeando exatamente como o código do Django está estruturado no repositório.

```mermaid
C4Component
    title Nível 3: Diagrama de Componentes - Monolito Django
    
    Container_Boundary(webapp, "App Web Core (Django)") {
        Component(views, "Controladores (views.py)", "FBV / CBV", "Lógica central: dashboard, transacao_views, categoria_views e cartao_views.")
        Component(templates, "Templates SSR (.html)", "Tailwind + Alpine", "Arquivos base.html, includes/ e painéis injetados com contexto nativo.")
        Component(auth, "Segurança (contrib.auth)", "Decorators", "Uso do @login_required e sessões de usuário isoladas no banco.")
        Component(forms, "Validadores (forms.py)", "Django Forms", "Classes TransacaoForm, CartaoCreditoForm e CategoriaForm.")
        Component(models, "Domínios (models.py)", "Django ORM", "Classes Transacao, Categoria e CartaoCredito com suas FKs.")
    }
    
    ContainerDb(db, "PostgreSQL", "Supabase", "Armazena as tabelas espelhadas do ORM.")

    Rel_R(views, templates, "Injeta contexto renderizado em", "HTTP Response")
    Rel_D(views, auth, "Bloqueia acesso sem sessão via")
    Rel_D(views, forms, "Despacha requisições POST para")
    Rel_D(views, models, "Faz Queries / Filtros através de")
    Rel_L(forms, models, "Cria ou Atualiza instâncias em")
    Rel_R(auth, models, "Lê chaves e profiles usando")
    Rel_D(models, db, "Sincroniza schema e dados via", "SQL (Psycopg2)")
    
    UpdateElementStyle(auth, $fontColor="white", $bgColor="#4A90D9", $borderColor="#2C6FAC")
    UpdateElementStyle(views, $fontColor="white", $bgColor="#4A90D9", $borderColor="#2C6FAC")
    UpdateElementStyle(forms, $fontColor="white", $bgColor="#4A90D9", $borderColor="#2C6FAC")
    UpdateElementStyle(models, $fontColor="white", $bgColor="#4A90D9", $borderColor="#2C6FAC")
    UpdateElementStyle(templates, $fontColor="white", $bgColor="#E67E22", $borderColor="#C0651A")
```

## Requisitos Funcionais

*   **RF01:** Autenticação segura com login/logout
*   **RF02:** CRUD de transações (receitas e despesas) com data, descrição, valor, categoria e cartão opcional
*   **RF03:** Gerenciamento de cartões de crédito (nome, limite, fechamento, vencimento, cor)
*   **RF04:** Categorização personalizada de transações por usuário
*   **RF05:** Dashboard com saldo total, resumo mensal e últimos 5 lançamentos
*   **RF06:** Histórico completo de transações com paginação
*   **RF07:** Isolamento de dados por usuário (sem vazamento entre contas)
*   **RF08:** Exportação de relatórios em PDF via microserviço

## Requisitos Não Funcionais

*   **RNF01:** Arquitetura híbrida (Django monolito + FastAPI microserviço)
*   **RNF02:** Backend em Python 3.12+ com Django 5.x e FastAPI
*   **RNF03:** Frontend Server-Side Rendering (Django Templates + TailwindCSS + Alpine.js)
*   **RNF04:** Rotas protegidas por autenticação obrigatória
*   **RNF05:** Integridade referencial com proteção de histórico (PROTECT) e deleção em cascata (CASCADE)
*   **RNF06:** Paginação de listagens (máximo 10 itens/página)
*   **RNF07:** Infraestrutura containerizada via Docker Compose com banco de dados remoto (Supabase/PostgreSQL) para escalabilidade

## Tecnologias Utilizadas

*   **Backend:** Python 3.12+, Django 5.x, FastAPI
*   **Servidores de Produção:** Gunicorn (Django), Uvicorn (FastAPI), WhiteNoise (Assets HD)
*   **Frontend:** TailwindCSS, Alpine.js
*   **Infraestrutura e Deploy:** Docker (Imagens Multi-container), Render.com / Railway
*   **Banco de Dados:** PostgreSQL Cloud (Supabase)

## Como Fazer o Deploy para Produção (Render.com)

Graças ao encapsulamento em Docker puro e configuração universal das Variáveis de Ambiente, a plataforma do **Render.com** (que possui *Tier Gratuito*) é a nossa opção de infraestrutura Cloud recomendada!

### Passo a Passo

1. Tenha o `DATABASE_URL` do seu projeto Supabase em mãos.
2. Acesse sua conta no **Render.com** e crie um novo **Web Service**.
3. Vincule seu repositório do Github contendo o Ordo Finance.
4. Em *Environment*, selecione **Docker**. O Render fará a leitura automática e construirá o app pelas diretrizes do seu `Dockerfile`.
5. Preencha as Variáveis (*Environment Variables*):
   - `DATABASE_URL` = [A connection string que você obteve no Supabase]
   - `SECRET_KEY` = [Gere um passkey/hash aleatório para proteger seu Django]
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `*`
6. Clique em **Deploy**! A plataforma subirá instâncias Linux e em minutos você terá acesso seguro via `https://ordo-finance-suaconta.onrender.com`.

---

## Como Executar o Projeto (Localmente para Testes)

### Via Docker Compose (Recomendado)

O projeto possui de forma nativamente acoplada um `docker-compose.prod.yml` arquitetado para Nuvem e também suporta devs locais.

1. Clone o projeto e crie um arquivo `.env` na raiz informando o `DATABASE_URL`.
2. Rode no bash:
    ```bash
    docker-compose up --build
    ```

4.  Acesse a aplicação principal em: `http://localhost:8000`

---

### Execução Local (Sem Docker)

Caso necessite rodar localmente para testes rápidos:
1. Crie e ative um ambiente virtual: `python -m venv venv`
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure a `DATABASE_URL` no `.env`
4. Execute: `python manage.py runserver`

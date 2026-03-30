# Ordo Finance

Sistema de gestão financeira pessoal com arquitetura híbrida: monolito Django para o core da aplicação e microserviço FastAPI para relatórios. Totalmente containerizado via Docker e implantável no Render.com.

## Visão Geral

A aplicação permite controle de receitas e despesas, categorização de lançamentos, gerenciamento de cartões de crédito e visualização de balanços financeiros. O projeto demonstra a coexistência de um monolito robusto (Django + Gunicorn) com um microserviço especializado (FastAPI + Uvicorn), utilizando conteinerização Docker para orquestração dos ambientes de desenvolvimento e produção.

---

## Arquitetura do Sistema

### Nível 1 — Contexto

Visão de alto nível: quem usa o sistema e com o que ele se comunica.

```mermaid
flowchart TD
    U["👤 Usuário\n──────────────\nAcompanha finanças\nvia navegador web"]
    O["🏦 Ordo Finance\n──────────────\nAplicação Web\nRender.com · Docker"]
    DB[("🗄️ PostgreSQL\n──────────────\nBanco de Dados\nRender · Free Tier")]

    U -- "HTTPS" --> O
    O -- "SQL · psycopg2" --> DB

    style U  fill:#08427B,color:#FFFFFF,stroke:#052E56
    style O  fill:#1168BD,color:#FFFFFF,stroke:#0B4884
    style DB fill:#2D882D,color:#FFFFFF,stroke:#1B5E1B
```

---

### Nível 2 — Containers

Decomposição dos serviços que compõem o sistema em produção.

```mermaid
flowchart TD
    U["👤 Usuário"]

    subgraph RENDER["☁️  Render.com"]
        direction TB
        WEB["🐍 App Principal\n──────────────\nDjango 5 · Gunicorn · WhiteNoise\nDocker · porta 8000\n\nAutenticação · CRUD · Dashboard\nTemplates SSR · Assets estáticos"]
        API["⚡ Microserviço de Relatórios\n──────────────\nFastAPI · Uvicorn\nDocker · porta 8001\n\nGeração de PDFs (planejado)"]
    end

    subgraph DB_HOST["🗄️  Banco de Dados"]
        DB[("PostgreSQL\nRender Free DB\n\ntransacoes · categorias\ncartoes · users")]
    end

    U        -- "HTTPS · navegador"           --> WEB
    WEB      -- "REST · HTTP (delegação)"     --> API
    WEB      -- "Django ORM · psycopg2"       --> DB
    API      -- "SQL puro · psycopg2"         --> DB

    style U   fill:#08427B,color:#FFFFFF,stroke:#052E56
    style WEB fill:#1168BD,color:#FFFFFF,stroke:#0B4884
    style API fill:#1168BD,color:#FFFFFF,stroke:#0B4884
    style DB  fill:#2D882D,color:#FFFFFF,stroke:#1B5E1B
```

---

### Nível 3 — Componentes (App Django)

Estrutura interna do monolito Django, mapeando os arquivos reais do repositório.

```mermaid
flowchart TD
    REQ["🌐 Requisição HTTP\nnavegador do usuário"]

    subgraph DJANGO["🐍  financas/  —  App Django"]
        direction TB
        AUTH["🔐 contrib.auth\n──────────────\n@login_required\nLoginRequiredMixin\nSessões isoladas por usuário"]

        VIEWS["📋 views.py\n──────────────\nFBV: dashboard · lista_transacoes\n      adicionar · editar · remover\nCBV: CartaoCredito(List·Create·Update·Delete)\n     Categoria(List·Create·Update·Delete)\nBase mixins: BaseCartaoCreditoView\n             BaseCategoriaView"]

        FORMS["📝 forms.py\n──────────────\nTransacaoForm\n  └─ querysets filtrados por usuário\nCartaoCreditoForm\nCategoriaForm\n  └─ widgets com classes Tailwind"]

        MODELS["🗂️ models.py\n──────────────\nTransacao\n  ├─ tipo: RECEITA · DESPESA\n  ├─ FK → Categoria (PROTECT)\n  └─ FK → CartaoCredito (CASCADE, nullable)\nCartaoCredito\n  └─ cor: BLUE·GREEN·RED·PURPLE\n         BLACK·ORANGE·GRAY\nCategoria\n  └─ unique_together: (usuario, nome)"]

        TEMPLATES["🎨 templates/\n──────────────\nbase.html + includes/\n  head.html · navbar.html · scripts.html\nfinancas/\n  dashboard.html\n  lista_transacoes.html\n  adicionar_transacao.html\n  cartao_credito_*.html\n  categoria_*.html\n  confirm_delete.html\nregistration/login.html\n\nTailwindCSS · Alpine.js"]
    end

    DB[("🗄️ PostgreSQL")]

    REQ    -- "verifica sessão"            --> AUTH
    AUTH   -- "redireciona ou permite"     --> VIEWS
    VIEWS  -- "valida dados POST"          --> FORMS
    VIEWS  -- "queries filtradas\npor request.user" --> MODELS
    VIEWS  -- "injeta contexto"            --> TEMPLATES
    FORMS  -- "cria / atualiza instâncias" --> MODELS
    MODELS -- "ORM · psycopg2"             --> DB

    style AUTH      fill:#4A90D9,color:#FFFFFF,stroke:#2C6FAC
    style VIEWS     fill:#1168BD,color:#FFFFFF,stroke:#0B4884
    style FORMS     fill:#4A90D9,color:#FFFFFF,stroke:#2C6FAC
    style MODELS    fill:#4A90D9,color:#FFFFFF,stroke:#2C6FAC
    style TEMPLATES fill:#D4820A,color:#FFFFFF,stroke:#A0600A
    style DB        fill:#2D882D,color:#FFFFFF,stroke:#1B5E1B
```

---

### Modelo de Dados (ER)

Relacionamentos e campos das tabelas gerenciadas pelo Django ORM.

```mermaid
erDiagram
    User ||--o{ Categoria      : "possui"
    User ||--o{ CartaoCredito  : "possui"
    User ||--o{ Transacao      : "registra"

    Categoria     ||--o{ Transacao : "classifica (PROTECT)"
    CartaoCredito |o--o{ Transacao : "vincula (CASCADE · opcional)"

    Categoria {
        int    id        PK
        int    usuario   FK
        string nome         "max_length=100 · unique por usuário"
    }

    CartaoCredito {
        int     id             PK
        int     usuario        FK
        string  nome              "max_length=100"
        decimal limite            "max_digits=10 · decimal_places=2"
        int     dia_fechamento
        int     dia_vencimento
        string  cor               "BLUE|GREEN|RED|PURPLE|BLACK|ORANGE|GRAY"
    }

    Transacao {
        int     id              PK
        int     usuario         FK
        int     categoria       FK  "on_delete=PROTECT"
        int     cartao_credito  FK  "nullable · on_delete=CASCADE"
        date    data
        string  tipo               "RECEITA|DESPESA"
        string  descricao          "max_length=200"
        decimal valor              "max_digits=10 · decimal_places=2"
        bool    fatura_paga        "default=False"
    }
```

---

## Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| RF01 | Autenticação segura com login e logout |
| RF02 | CRUD de transações com data, descrição, valor, categoria e cartão opcional |
| RF03 | Gerenciamento de cartões de crédito (nome, limite, fechamento, vencimento, cor) |
| RF04 | Categorização personalizada de transações por usuário |
| RF05 | Dashboard com saldo total, resumo mensal e últimos 5 lançamentos |
| RF06 | Histórico completo de transações com paginação (10 itens/página) |
| RF07 | Isolamento total de dados por usuário |
| RF08 | Exportação de relatórios em PDF via microserviço *(planejado)* |

## Requisitos Não Funcionais

| ID | Requisito |
|----|-----------|
| RNF01 | Arquitetura híbrida: Django monolito + FastAPI microserviço |
| RNF02 | Python 3.12+ · Django 5.x · FastAPI |
| RNF03 | Frontend SSR: Django Templates + TailwindCSS + Alpine.js |
| RNF04 | Todas as rotas protegidas por autenticação obrigatória |
| RNF05 | Integridade referencial: PROTECT para categorias, CASCADE para cartões |
| RNF06 | Infraestrutura containerizada via Docker Compose |

---

## Tecnologias

| Camada | Tecnologias |
|--------|------------|
| Backend | Python 3.12 · Django 5.x · FastAPI |
| Servidores | Gunicorn (Django) · Uvicorn (FastAPI) · WhiteNoise + Brotli (assets) |
| Frontend | Django Templates · TailwindCSS · Alpine.js |
| Banco de Dados | PostgreSQL · psycopg2 · dj-database-url |
| Infraestrutura | Docker · Docker Compose · Render.com |

---

## Deploy no Render.com (Free Tier)

O projeto está **100% pronto** para deploy no Render. O `entrypoint.sh` executa automaticamente as migrations, coleta os arquivos estáticos e inicia o Gunicorn.

### Passo a Passo

1. Acesse [render.com](https://render.com) e crie um **PostgreSQL** gratuito. Copie a *Internal Database URL*.
2. Crie um novo **Web Service** e vincule este repositório.
3. Em *Settings*, selecione **Docker** como ambiente de build.
4. Configure as variáveis de ambiente:

   | Variável | Valor |
   |----------|-------|
   | `DATABASE_URL` | URL interna do PostgreSQL criado no passo 1 |
   | `SECRET_KEY` | Hash aleatório e seguro |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `*` ou seu domínio |

5. Clique em **Deploy**. Em alguns minutos a aplicação estará disponível em `https://seu-servico.onrender.com`.

> **Atenção:** No free tier, o web service dorme após 15 minutos de inatividade e leva ~30s para acordar. O PostgreSQL gratuito expira em 90 dias.

---

## Execução Local

### Via Docker Compose (recomendado)

```bash
docker-compose up --build
```

Serviços disponíveis:

| Serviço | URL |
|---------|-----|
| Django (app principal) | http://localhost:8000 |
| FastAPI (microserviço) | http://localhost:8001 |
| PostgreSQL | localhost:5432 |

### Sem Docker

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
# configure DATABASE_URL no .env ou exporte a variável
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

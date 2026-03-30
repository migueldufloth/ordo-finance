# Ordo Finance

Sistema de gestão financeira pessoal com arquitetura híbrida: monolito Django para o core da aplicação e microserviço FastAPI para relatórios. Totalmente containerizado via Docker e implantável no Render.com.

## Visão Geral

A aplicação permite controle de receitas e despesas, categorização de lançamentos, gerenciamento de cartões de crédito e visualização de balanços financeiros. O projeto demonstra a coexistência de um monolito robusto (Django + Gunicorn) com um microserviço especializado (FastAPI + Uvicorn), utilizando conteinerização Docker para orquestração dos ambientes de desenvolvimento e produção.

---

## Arquitetura do Sistema

### Nível 1: Contexto

Visão de alto nível: quem usa o sistema e com o que ele se comunica.

```mermaid
flowchart TD
    classDef person fill:#08427B,stroke:#66B2FF,stroke-width:2px,color:#fff;
    classDef system fill:#1168BD,stroke:#66B2FF,stroke-width:2px,color:#fff;
    classDef db fill:#2D882D,stroke:#55FF55,stroke-width:2px,color:#fff;

    User(["<b>👤 Usuário</b><br/><span style='font-size:12px; color:#ddd'>Controla receitas, despesas e cartões<br/>de crédito pelo navegador</span>"]):::person
    Ordo["<b>⚙️ Ordo Finance</b><br/><span style='font-size:12px; color:#ddd'>Aplicação web de gestão financeira pessoal<br/>hospedada na Oracle Cloud via Docker Compose</span>"]:::system
    DB[("<b>🗄️ PostgreSQL</b><br/><span style='font-size:12px; color:#ddd'>Banco de dados em container<br/>com volume persistente</span>")]:::db

    User -- "Acessa via HTTPS" --> Ordo
    Ordo -- "Lê e grava dados" --> DB

    linkStyle default stroke:#66B2FF,stroke-width:2px,color:#E0E0E0,font-size:13px;
```

---

### Nível 2: Containers

Decomposição dos serviços que compõem o sistema em produção.

```mermaid
flowchart LR
    classDef person fill:#08427B,stroke:#66B2FF,stroke-width:2px,color:#fff;
    classDef container fill:#1168BD,stroke:#66B2FF,stroke-width:2px,color:#fff;
    classDef db fill:#2D882D,stroke:#55FF55,stroke-width:2px,color:#fff;
    classDef boundary fill:transparent,stroke:#888,stroke-dasharray: 5 5,color:#ccc,font-weight:bold;

    User(["<b>👤 Usuário</b><br/><span style='font-size:12px; color:#ddd'>Acessa a interface web<br/>pelo navegador</span>"]):::person

    subgraph Oracle ["☁️ Oracle Cloud — Always Free VM"]
        direction TB
        Web["<b>🖥️ App Principal</b><br/><span style='font-size:12px; color:#99CCFF'>[Django 5 · Gunicorn · WhiteNoise]</span><br/><span style='font-size:12px; color:#ddd'>Monolito SSR. Gerencia autenticação,<br/>transações, cartões e categorias.</span>"]:::container
        API["<b>⚙️ Microserviço de Relatórios</b><br/><span style='font-size:12px; color:#99CCFF'>[FastAPI · Uvicorn]</span><br/><span style='font-size:12px; color:#ddd'>Serviço isolado para geração<br/>de PDFs. Planejado.</span>"]:::container
        DB[("<b>🗄️ PostgreSQL</b><br/><span style='font-size:12px; color:#99CCFF'>[Container · Volume Persistente]</span><br/><span style='font-size:12px; color:#ddd'>Armazena usuários, transações,<br/>categorias e cartões.</span>")]:::db
        Web -- "Delega geração de PDF<br/>[REST / HTTP]" --> API
        Web -- "Consulta e persiste<br/>[Django ORM]" --> DB
        API -- "Agrega relatórios [SQL]" --> DB
    end
    class Oracle boundary;

    User -- "Navega [HTTPS]" --> Web

    linkStyle default stroke:#66B2FF,stroke-width:2px,color:#E0E0E0,font-size:13px;
```

---

### Nível 3: Componentes

Estrutura interna do monolito Django, mapeando os arquivos reais do repositório.

```mermaid
flowchart LR
    classDef person fill:#08427B,stroke:#66B2FF,stroke-width:2px,color:#fff;
    classDef comp fill:#4A90D9,stroke:#99CCFF,stroke-width:2px,color:#fff;
    classDef compAlt fill:#D4820A,stroke:#FFB266,stroke-width:2px,color:#fff;
    classDef db fill:#2D882D,stroke:#55FF55,stroke-width:2px,color:#fff;
    classDef boundary fill:transparent,stroke:#888,stroke-dasharray: 5 5,color:#ccc,font-weight:bold;

    User(["<b>👤 Usuário autenticado</b><br/><span style='font-size:12px; color:#ddd'>Interage com as páginas<br/>da aplicação</span>"]):::person
    DB[("<b>🗄️ PostgreSQL</b><br/><span style='font-size:12px; color:#ddd'>Render Free DB</span>")]:::db

    subgraph App ["📦 App Principal — financas/"]
        direction TB
        Auth["<b>🔐 Autenticação</b><br/><span style='font-size:12px; color:#cce5ff'>[contrib.auth]</span><br/><span style='font-size:12px; color:#eee'>Decorators @login_required e<br/>LoginRequiredMixin. Isola<br/>sessão por usuário.</span>"]:::comp
        Views["<b>🎛️ Views</b><br/><span style='font-size:12px; color:#cce5ff'>[FBV + CBV · views.py]</span><br/><span style='font-size:12px; color:#eee'>dashboard, lista_transacoes, adicionar,<br/>editar, remover. CBVs para<br/>CartaoCredito e Categoria.</span>"]:::comp
        Forms["<b>📝 Formulários</b><br/><span style='font-size:12px; color:#cce5ff'>[Django Forms]</span><br/><span style='font-size:12px; color:#eee'>TransacaoForm, CartaoCreditoForm<br/>e CategoriaForm. Querysets<br/>filtrados por usuário.</span>"]:::comp
        Templates["<b>🎨 Templates</b><br/><span style='font-size:12px; color:#ffe6cc'>[Tailwind · Alpine.js]</span><br/><span style='font-size:12px; color:#eee'>base.html, dashboard, lista_transacoes<br/>e formulários de CRUD.</span>"]:::compAlt
        Models["<b>📊 Modelos</b><br/><span style='font-size:12px; color:#cce5ff'>[Django ORM]</span><br/><span style='font-size:12px; color:#eee'>Transacao, CartaoCredito e Categoria.<br/>Todos isolados por FK do usuário.</span>"]:::comp

        Auth  -- "Permite acesso"  --> Views
        Views -- "Valida POST"     --> Forms
        Views -- "Renderiza HTML"  --> Templates
        Views -- "Consulta dados"  --> Models
        Forms -- "Cria e atualiza" --> Models
    end
    class App boundary;

    User   -- "Requisição HTTP"  --> Auth
    Models -- "ORM · psycopg2"   --> DB

    linkStyle default stroke:#66B2FF,stroke-width:2px,color:#E0E0E0,font-size:13px;
```

---

### Modelo de Dados (ER)

Estrutura completa das tabelas gerenciadas pelo Django ORM, com todos os campos, tipos e relacionamentos.

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'fontSize': '16px', 'primaryColor': '#1168BD', 'primaryBorderColor': '#66B2FF', 'lineColor': '#66B2FF', 'fontFamily': 'sans-serif'}}}%%
erDiagram
    User ||--o{ Categoria     : "possui"
    User ||--o{ CartaoCredito : "possui"
    User ||--o{ Transacao     : "registra"

    Categoria     ||--o{ Transacao : "classifica"
    CartaoCredito |o--o{ Transacao : "vincula (opcional)"

    User {
        int    id           PK
        string username
        string email
        string password        "hash"
        bool   is_active
    }

    Categoria {
        int    id           PK
        int    usuario_id   FK
        string nome            "max_length=100"
    }

    CartaoCredito {
        int    id               PK
        int    usuario_id       FK
        string nome                "max_length=100"
        decimal limite             "max_digits=10, decimal_places=2"
        int    dia_fechamento
        int    dia_vencimento
        string cor                 "BLUE|GREEN|RED|PURPLE|BLACK|ORANGE|GRAY"
    }

    Transacao {
        int    id                   PK
        int    usuario_id           FK
        int    categoria_id         FK  "on_delete=PROTECT"
        int    cartao_credito_id    FK  "nullable, on_delete=CASCADE"
        date   data
        string tipo                   "RECEITA|DESPESA"
        string descricao              "max_length=200"
        decimal valor                 "max_digits=10, decimal_places=2"
        bool   fatura_paga            "default=False"
    }
```

> **Regras de integridade:** deletar uma `Categoria` que possui transações é bloqueado (`PROTECT`). Deletar um `CartaoCredito` remove em cascata suas transações vinculadas (`CASCADE`). Deletar um `User` remove em cascata todos os seus dados.

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
| Infraestrutura | Docker · Docker Compose · Oracle Cloud Always Free |

---

## Deploy na Oracle Cloud (Always Free)

Toda a aplicação sobe via `docker-compose.prod.yml` em uma VM gratuita e permanente da Oracle Cloud. O banco de dados roda como container com volume persistente — sem serviços externos.

### 1. Criar a VM na Oracle Cloud

1. Acesse [cloud.oracle.com](https://cloud.oracle.com) e crie uma conta (Always Free não exige cartão de crédito em uso).
2. Crie uma **Compute Instance** com as configurações Always Free:
   - Shape: `VM.Standard.A1.Flex` (ARM) — até 4 OCPUs e 24 GB RAM, ou `VM.Standard.E2.1.Micro` (AMD)
   - Imagem: **Ubuntu 22.04**
3. Salve a chave SSH gerada e anote o IP público da VM.

### 2. Configurar a VM

Conecte via SSH e instale Docker:

```bash
ssh ubuntu@<IP_DA_VM>

# Instalar Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
newgrp docker

# Instalar Docker Compose plugin
sudo apt-get install -y docker-compose-plugin
docker compose version
```

Libere as portas no Security List da Oracle (VCN → Security Lists → Ingress Rules):

| Porta | Protocolo | Origem |
|-------|-----------|--------|
| 22    | TCP       | 0.0.0.0/0 (SSH) |
| 8000  | TCP       | 0.0.0.0/0 (Django) |
| 8001  | TCP       | 0.0.0.0/0 (FastAPI) |

E no firewall da própria VM:

```bash
sudo iptables -I INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 8001 -j ACCEPT
sudo netfilter-persistent save
```

### 3. Subir a Aplicação

```bash
# Clonar o repositório
git clone <URL_DO_REPO>
cd ordo-finance

# Criar o arquivo de variáveis de ambiente
cat > .env <<EOF
POSTGRES_DB=ordo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=suasenhaforte
SECRET_KEY=suachavesecreta
ALLOWED_HOSTS=*
EOF

# Subir todos os containers (DB + Django + FastAPI)
docker compose -f docker-compose.prod.yml up -d --build
```

A aplicação estará disponível em `http://<IP_DA_VM>:8000`.

### Comandos Úteis

```bash
docker compose -f docker-compose.prod.yml logs -f          # Ver logs
docker compose -f docker-compose.prod.yml ps               # Status dos containers
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d --build  # Atualizar
```

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

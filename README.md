# Ordo Finance

Sistema de gestão financeira pessoal com arquitetura híbrida: monolito Django para o core da aplicação e microserviço FastAPI para relatórios. Totalmente containerizado via Docker e implantado na Oracle Cloud Always Free.

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

    User -- "Acessa via HTTP" --> Ordo
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

    User -- "Navega [HTTP]" --> Web

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
    DB[("<b>🗄️ PostgreSQL</b><br/><span style='font-size:12px; color:#ddd'>Container · Oracle Cloud</span>")]:::db

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
        string nome            "max_length=100, unique por usuário"
    }

    CartaoCredito {
        int    id               PK
        int    usuario_id       FK
        string nome                "max_length=100"
        decimal limite             "max_digits=10, decimal_places=2"
        int    dia_fechamento      "1–31"
        int    dia_vencimento      "1–31"
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

## Screenshots

### Login
![Login](imgs/login.png)

### Dashboard
Exibe receitas e despesas do mês atual, saldo total e os últimos lançamentos registrados.

![Dashboard](imgs/dashboard.png)

### Lançamentos
Lista completa de transações com data, descrição, categoria, valor e tipo (receita/despesa).

![Lançamentos](imgs/lancamentos.png)

### Novo Lançamento
Formulário para registrar uma transação com tipo, data, descrição, valor, categoria e cartão de crédito opcional.

![Novo Lançamento](imgs/criar-lancamento.png)

### Cartões de Crédito
Visualização dos cartões cadastrados com limite, dia de fechamento e vencimento.

![Cartões de Crédito](imgs/cartoes.png)

### Novo Cartão de Crédito
Formulário para cadastrar um cartão com nome, cor, limite, dia de fechamento e vencimento.

![Novo Cartão](imgs/criar-cartao.png)

---

## Rotas da Aplicação

### Django (porta 8000)

| Método | URL | Nome | Descrição |
|--------|-----|------|-----------|
| GET | `/` | `home` | Dashboard com saldo, resumo mensal e últimos lançamentos |
| GET/POST | `/accounts/login/` | `login` | Login |
| POST | `/accounts/logout/` | `logout` | Logout |
| GET | `/transacoes/` | `lista_transacoes` | Lista paginada de transações (10/página) |
| GET/POST | `/transacoes/adicionar/` | `adicionar_transacao` | Formulário de nova transação |
| GET/POST | `/transacoes/<pk>/editar/` | `editar_transacao` | Editar transação existente |
| GET/POST | `/transacoes/<pk>/remover/` | `remover_transacao` | Confirmar e remover transação |
| GET | `/transacoes/cartoes/` | `cartao_credito_list` | Lista de cartões de crédito |
| GET/POST | `/transacoes/cartoes/adicionar/` | `cartao_credito_create` | Novo cartão de crédito |
| GET/POST | `/transacoes/cartoes/<pk>/editar/` | `cartao_credito_update` | Editar cartão |
| GET/POST | `/transacoes/cartoes/<pk>/remover/` | `cartao_credito_delete` | Remover cartão |
| GET | `/transacoes/categorias/` | `categoria_list` | Lista de categorias |
| GET/POST | `/transacoes/categorias/adicionar/` | `categoria_create` | Nova categoria |
| GET/POST | `/transacoes/categorias/<pk>/editar/` | `categoria_update` | Editar categoria |
| GET/POST | `/transacoes/categorias/<pk>/remover/` | `categoria_delete` | Remover categoria |
| GET | `/admin/` | — | Django Admin |

### FastAPI (porta 8001)

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/` | Status do serviço |
| GET | `/health` | Health check do microserviço |
| POST | `/relatorio/pdf` | Gera relatório PDF a partir de lista de transações |

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
| RF08 | Exportação de relatórios em PDF via microserviço FastAPI |

## Requisitos Não Funcionais

| ID | Requisito |
|----|-----------|
| RNF01 | Arquitetura híbrida: Django monolito + FastAPI microserviço |
| RNF02 | Python 3.12+ · Django 5.x · FastAPI |
| RNF03 | Frontend SSR: Django Templates + TailwindCSS + Alpine.js |
| RNF04 | Todas as rotas protegidas por autenticação obrigatória |
| RNF05 | Integridade referencial: PROTECT para categorias, CASCADE para cartões |
| RNF06 | Infraestrutura containerizada via Docker Compose |
| RNF07 | Pipeline CI/CD automatizado via GitHub Actions com self-hosted runner |

---

## Tecnologias

| Camada | Tecnologias |
|--------|------------|
| Backend | Python 3.12 · Django 5.x · FastAPI |
| Servidores | Gunicorn (Django) · Uvicorn (FastAPI) · WhiteNoise + Brotli (assets) |
| Frontend | Django Templates · TailwindCSS · Alpine.js · Lucide Icons |
| Banco de Dados | PostgreSQL 15 · psycopg2 · dj-database-url |
| Infraestrutura | Docker · Docker Compose · Oracle Cloud Always Free |
| CI/CD | GitHub Actions · Self-hosted Runner |

---

## Variáveis de Ambiente

O projeto usa um arquivo `.env` na raiz. Abaixo todas as variáveis suportadas:

| Variável | Obrigatória em Prod | Padrão | Descrição |
|----------|--------------------:|--------|-----------|
| `SECRET_KEY` | Sim | insecure key | Chave secreta do Django |
| `DEBUG` | — | `False` | Ativar modo debug (`True` apenas local) |
| `ALLOWED_HOSTS` | Sim | `localhost,127.0.0.1` | Hosts permitidos, separados por vírgula |
| `DATABASE_URL` | Sim | SQLite local | URL de conexão do banco (`postgres://user:pass@host:port/db`) |
| `POSTGRES_DB` | Sim (Docker) | `ordo` | Nome do banco (usado pelo container PostgreSQL) |
| `POSTGRES_USER` | Sim (Docker) | `postgres` | Usuário do banco |
| `POSTGRES_PASSWORD` | Sim (Docker) | — | Senha do banco |

**Exemplo de `.env` para desenvolvimento local (sem Docker):**

```env
DEBUG=True
SECRET_KEY=qualquer-chave-local
ALLOWED_HOSTS=localhost,127.0.0.1
# Sem DATABASE_URL → usa SQLite automático
```

**Exemplo de `.env` para produção (Oracle Cloud):**

```env
DEBUG=False
SECRET_KEY=chave-secreta-longa-e-aleatoria
ALLOWED_HOSTS=<IP_DA_VM>,seu-dominio.com
POSTGRES_DB=ordo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=senha-forte-aqui
```

> Em produção, `DATABASE_URL` é montado automaticamente pelo `docker-compose.prod.yml` a partir das variáveis `POSTGRES_*` — não precisa definir manualmente.

---

## CI/CD

O pipeline é gerenciado pelo **GitHub Actions** com um **self-hosted runner** instalado diretamente na VM de produção.

```
git push origin main
       │
       ▼
  Job: test (ubuntu-latest)
  ├── pip install -r requirements.txt
  ├── manage.py check
  └── manage.py test financas
       │ (somente se passar)
       ▼
  Job: deploy (self-hosted — VM Oracle Cloud)
  ├── git pull origin main
  ├── docker compose -f docker-compose.prod.yml up -d --build
  └── manage.py migrate --noinput
```

O runner roda como serviço `systemd` na VM, conectando-se ao GitHub via HTTPS de saída — sem portas abertas para automação.

---

## Execução Local (sem Docker)

```bash
# Criar e ativar virtualenv
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Criar o .env (sem DATABASE_URL usa SQLite automaticamente)
echo "DEBUG=True" > .env
echo "SECRET_KEY=dev-secret" >> .env

# Aplicar migrations e criar superusuário
python manage.py migrate
python manage.py createsuperuser

# Rodar
python manage.py runserver
```

Acesse em `http://localhost:8000`.

---

## Deploy na Oracle Cloud (Always Free)

Toda a aplicação sobe via `docker-compose.prod.yml` em uma VM gratuita e permanente da Oracle Cloud. O banco de dados roda como container com volume persistente — sem serviços externos pagos.

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
cd ordo_django

# Criar o arquivo de variáveis de ambiente
cat > .env <<EOF
DEBUG=False
SECRET_KEY=sua-chave-secreta-longa
ALLOWED_HOSTS=<IP_DA_VM>
POSTGRES_DB=ordo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=senha-forte-aqui
EOF

# Build e subida de todos os containers (PostgreSQL + Django + FastAPI)
docker compose -f docker-compose.prod.yml up -d --build

# Criar superusuário (primeira vez)
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

A aplicação estará disponível em `http://<IP_DA_VM>:8000`.

### 4. Comportamento do Entrypoint

Ao subir, o container `web` executa automaticamente via `entrypoint.sh`:

1. `python manage.py migrate --noinput` — aplica migrations pendentes
2. `python manage.py collectstatic --noinput` — coleta arquivos estáticos para WhiteNoise
3. `gunicorn ordo_project.wsgi:application --bind 0.0.0.0:8000 --workers 3` — sobe o servidor com 3 workers

O container `web` só sobe após o `db` passar no health check (`pg_isready`), evitando falhas de conexão na inicialização.

### Comandos Úteis

```bash
# Ver logs em tempo real
docker compose -f docker-compose.prod.yml logs -f

# Status dos containers
docker compose -f docker-compose.prod.yml ps

# Criar superusuário
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Atualizar para nova versão
git pull
docker compose -f docker-compose.prod.yml up -d --build

# Acessar shell do Django
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Backup do banco de dados
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres ordo > backup.sql
```

---

## Estrutura do Projeto

```
ordo-finance/
├── .github/workflows/
│   └── deploy.yml              # Pipeline CI/CD (testes + deploy automático)
├── api/                        # Microserviço FastAPI (relatórios PDF)
│   ├── main.py                 # Endpoints FastAPI
│   ├── requirements.txt
│   └── Dockerfile
├── financas/                   # App Django principal
│   ├── models.py               # Transacao, CartaoCredito, Categoria
│   ├── views.py                # FBVs + CBVs
│   ├── forms.py                # TransacaoForm, CartaoCreditoForm, CategoriaForm
│   ├── urls.py                 # Rotas do app
│   └── templates/financas/     # Templates HTML
├── ordo_project/
│   ├── settings.py             # Configurações (dj-database-url, WhiteNoise)
│   ├── urls.py                 # Roteador raiz
│   └── wsgi.py
├── docker-compose.yml          # Ambiente de desenvolvimento local
├── docker-compose.prod.yml     # Ambiente de produção (Oracle Cloud)
├── Dockerfile                  # Imagem do container Django
├── entrypoint.sh               # migrate + collectstatic + gunicorn
└── requirements.txt
```

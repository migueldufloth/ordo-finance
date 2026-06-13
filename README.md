# Ordo Finance

Sistema de gestão financeira pessoal com arquitetura híbrida: monolito Django para o core da aplicação e microserviço FastAPI para relatórios. Totalmente containerizado via Docker e implantado na Oracle Cloud Always Free.

## Visão Geral

A aplicação permite controle de receitas e despesas, categorização de lançamentos, gerenciamento de cartões de crédito, orçamentos mensais por categoria, transações recorrentes e faturas de cartão. O projeto demonstra a coexistência de um monolito robusto (Django + Gunicorn) com um microserviço especializado (FastAPI + Uvicorn), utilizando conteinerização Docker para orquestração dos ambientes de desenvolvimento e produção.

---

## Arquitetura do Sistema

### Nível 1: Contexto

Visão de alto nível: quem usa o sistema e com o que ele se comunica.

![C4 Nível 1 — Contexto](docs/diagramas/png/c1_contexto.png)

---

### Nível 2: Containers

Decomposição dos serviços que compõem o sistema em produção.

![C4 Nível 2 — Containers](docs/diagramas/png/c2_containers.png)

---

### Nível 3: Componentes — App Django

Estrutura interna do monolito Django, mapeando os arquivos reais do repositório.

![C4 Nível 3 — Componentes Django](docs/diagramas/png/c3_componentes_django.png)

### Nível 3: Componentes — Microserviço FastAPI

Estrutura interna do microserviço de geração de PDFs.

![C4 Nível 3 — Componentes FastAPI](docs/diagramas/png/c3_componentes_fastapi.png)

---

### Modelo de Dados

Entidades, atributos tipados, enums e regras de integridade referencial.

![Diagrama de Classes — Modelos](docs/diagramas/png/uml_classes_modelos.png)

> **Regras de integridade:** deletar uma `Categoria` que possui transações é bloqueado (`PROTECT`). Deletar um `CartaoCredito` remove em cascata suas transações vinculadas (`CASCADE`). Deletar um `User` remove em cascata todos os seus dados.

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
| POST | `/transacoes/relatorio/` | `gerar_relatorio` | Gera relatório PDF via microserviço FastAPI |
| GET | `/transacoes/exportar-csv/` | `exportar_csv` | Exporta transações filtradas em CSV |
| GET | `/transacoes/cartoes/` | `cartao_credito_list` | Lista de cartões de crédito |
| GET/POST | `/transacoes/cartoes/adicionar/` | `cartao_credito_create` | Novo cartão de crédito |
| GET/POST | `/transacoes/cartoes/<pk>/editar/` | `cartao_credito_update` | Editar cartão |
| GET/POST | `/transacoes/cartoes/<pk>/remover/` | `cartao_credito_delete` | Remover cartão |
| GET | `/transacoes/cartoes/<pk>/fatura/` | `fatura_cartao` | Fatura mensal do cartão com transações vinculadas |
| POST | `/transacoes/faturas/<pk>/pagar/` | `marcar_fatura_paga` | Marca fatura como paga |
| GET | `/transacoes/categorias/` | `categoria_list` | Lista de categorias |
| GET/POST | `/transacoes/categorias/adicionar/` | `categoria_create` | Nova categoria |
| GET/POST | `/transacoes/categorias/<pk>/editar/` | `categoria_update` | Editar categoria |
| GET/POST | `/transacoes/categorias/<pk>/remover/` | `categoria_delete` | Remover categoria |
| GET | `/transacoes/orcamentos/` | `orcamento_list` | Lista de orçamentos com gasto mensal por categoria |
| GET/POST | `/transacoes/orcamentos/adicionar/` | `orcamento_create` | Novo orçamento |
| GET/POST | `/transacoes/orcamentos/<pk>/editar/` | `orcamento_update` | Editar orçamento |
| GET/POST | `/transacoes/orcamentos/<pk>/remover/` | `orcamento_delete` | Remover orçamento |
| GET | `/transacoes/recorrentes/` | `transacao_recorrente_list` | Lista de transações recorrentes |
| GET/POST | `/transacoes/recorrentes/adicionar/` | `transacao_recorrente_create` | Nova transação recorrente |
| GET/POST | `/transacoes/recorrentes/<pk>/editar/` | `transacao_recorrente_update` | Editar transação recorrente |
| GET/POST | `/transacoes/recorrentes/<pk>/remover/` | `transacao_recorrente_delete` | Remover transação recorrente |
| GET | `/health/` | `health` | Health check da aplicação e do banco de dados |
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
| RF09 | Orçamentos mensais por categoria com acompanhamento de gasto e percentual |
| RF10 | Transações recorrentes com frequência configurável (mensal, quinzenal, semanal, anual) |
| RF11 | Faturas de cartão de crédito por mês com controle de pagamento |
| RF12 | Exportação de transações em CSV |

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
| RNF08 | Observabilidade com rastreamento de erros (Sentry) e monitoramento de uptime (Better Stack) |

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
| Observabilidade | Sentry (erros) · Better Stack (uptime) |

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
| `REPORTS_API_URL` | — | `http://api:8000` | URL base do microserviço FastAPI |
| `SENTRY_DSN` | — | desativado | DSN do Sentry para rastreamento de erros em produção |

> Em produção, `DATABASE_URL` é montado automaticamente pelo `docker-compose.prod.yml` a partir das variáveis `POSTGRES_*`. `SENTRY_DSN` é opcional — o Sentry só inicializa se a variável estiver definida.

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

## Observabilidade

| Ferramenta | Função |
|---|---|
| **Sentry** | Captura exceções em tempo real com stacktrace completo, contexto de request e agrupamento automático. Ativo quando `SENTRY_DSN` está definido no ambiente. |
| **Better Stack** | Monitoramento de uptime externo via `/health/`. Dispara alertas se a aplicação ou o banco de dados ficarem indisponíveis. |

O endpoint `/health/` retorna `{"status": "ok", "database": "ok"}` (HTTP 200) quando tudo está operacional, ou `{"status": "degraded", "database": "error"}` (HTTP 503) se o banco não responder.

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
│   ├── models.py               # Transacao, CartaoCredito, Categoria, Orcamento, FaturaCartao, TransacaoRecorrente
│   ├── views.py                # FBVs + CBVs
│   ├── forms.py                # TransacaoForm, CartaoCreditoForm, CategoriaForm, OrcamentoForm, TransacaoRecorrenteForm
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

---

## Diagramas Adicionais

Os arquivos fonte `.puml` estão em [`docs/diagramas/src/`](docs/diagramas/src/).
O workflow [Generate Diagrams](.github/workflows/generate-diagrams.yml) regenera os PNGs automaticamente a cada push que modifique os `.puml`.

### Diagrama de Classes — Views, Forms e Mixins

![Classes — Views](docs/diagramas/png/uml_classes_views.png)

### Diagrama de Classes — Schemas FastAPI

![Classes — FastAPI](docs/diagramas/png/uml_classes_fastapi.png)

### Sequência — Autenticação (Login)

![Sequência — Autenticação](docs/diagramas/png/seq_autenticacao.png)

### Sequência — Adicionar Transação

![Sequência — Adicionar Transação](docs/diagramas/png/seq_adicionar_transacao.png)

### Sequência — Geração de Relatório PDF

![Sequência — Relatório PDF](docs/diagramas/png/seq_relatorio_pdf.png)

### Sequência — Dashboard

![Sequência — Dashboard](docs/diagramas/png/seq_dashboard.png)

### Sequência — CI/CD Deploy Automático

![Sequência — CI/CD](docs/diagramas/png/seq_cicd_deploy.png)

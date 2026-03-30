# Ordo Finance

Sistema de gestão financeira pessoal com arquitetura híbrida: monolito Django para o core da aplicação e microserviço FastAPI para relatórios. Totalmente containerizado via Docker e implantável no Render.com.

## Visão Geral

A aplicação permite controle de receitas e despesas, categorização de lançamentos, gerenciamento de cartões de crédito e visualização de balanços financeiros. O projeto demonstra a coexistência de um monolito robusto (Django + Gunicorn) com um microserviço especializado (FastAPI + Uvicorn), utilizando conteinerização Docker para orquestração dos ambientes de desenvolvimento e produção.

---

## Arquitetura do Sistema

### Nível 1: Contexto

Visão de alto nível: quem usa o sistema e com o que ele se comunica.

```mermaid
C4Context
    title Nível 1: Contexto do Sistema

    Person(user, "Usuário", "Controla receitas, despesas e cartões de crédito pelo navegador")
    System(ordo, "Ordo Finance", "Aplicação web de gestão financeira pessoal hospedada no Render.com via Docker")
    SystemDb_Ext(db, "PostgreSQL", "Banco de dados relacional no Render Free Tier")

    Rel_D(user, ordo, "Acessa via HTTPS")
    Rel_D(ordo, db, "Lê e grava dados")

    UpdateElementStyle(user, $fontColor="white", $bgColor="#08427B", $borderColor="#052E56")
    UpdateElementStyle(ordo, $fontColor="white", $bgColor="#1168BD", $borderColor="#0B4884")
    UpdateElementStyle(db,   $fontColor="white", $bgColor="#2D882D", $borderColor="#1B5E1B")
    UpdateRelStyle(user, ordo, $textColor="white", $lineColor="#aaaaaa")
    UpdateRelStyle(ordo, db,   $textColor="white", $lineColor="#aaaaaa")
```

---

### Nível 2: Containers

Decomposição dos serviços que compõem o sistema em produção.

```mermaid
C4Container
    title Nível 2: Containers

    Person(user, "Usuário", "Acessa a interface web pelo navegador")

    System_Boundary(render, "Render.com") {
        Container(web, "App Principal", "Django 5 · Gunicorn · WhiteNoise", "Monolito SSR. Gerencia autenticação, transações, cartões e categorias.")
        Container(api, "Microserviço de Relatórios", "FastAPI · Uvicorn", "Serviço isolado para geração de PDFs. Planejado.")
    }

    SystemDb_Ext(db, "PostgreSQL", "Render Free DB", "Armazena usuários, transações, categorias e cartões.")

    Rel_D(user, web, "Navega", "HTTPS")
    Rel_D(web, api, "Delega geração de PDF", "REST / HTTP")
    Rel_D(web, db, "Consulta e persiste", "Django ORM")
    Rel_D(api, db, "Agrega relatórios", "SQL")

    UpdateElementStyle(user, $fontColor="white", $bgColor="#08427B", $borderColor="#052E56")
    UpdateElementStyle(web,  $fontColor="white", $bgColor="#1168BD", $borderColor="#0B4884")
    UpdateElementStyle(api,  $fontColor="white", $bgColor="#1168BD", $borderColor="#0B4884")
    UpdateElementStyle(db,   $fontColor="white", $bgColor="#2D882D", $borderColor="#1B5E1B")
    UpdateRelStyle(user, web, $textColor="white", $lineColor="#aaaaaa")
    UpdateRelStyle(web, api,  $textColor="white", $lineColor="#aaaaaa")
    UpdateRelStyle(web, db,   $textColor="white", $lineColor="#aaaaaa")
    UpdateRelStyle(api, db,   $textColor="white", $lineColor="#aaaaaa")
```

---

### Nível 3: Componentes

Estrutura interna do monolito Django, mapeando os arquivos reais do repositório.

```mermaid
C4Component
    title Nível 3: Componentes do App Principal (financas/)

    Person(user, "Usuário autenticado", "Interage com as páginas da aplicação")

    Container_Boundary(django, "App Principal — financas/") {
        Component(auth,      "Autenticação",  "contrib.auth",        "Decorators @login_required e LoginRequiredMixin. Isola sessão por usuário.")
        Component(views,     "Views",         "FBV + CBV · views.py","dashboard, lista_transacoes, adicionar, editar, remover. CBVs para CartaoCredito e Categoria.")
        Component(forms,     "Formulários",   "Django Forms",        "TransacaoForm, CartaoCreditoForm e CategoriaForm. Querysets filtrados por usuário.")
        Component(models,    "Modelos",       "Django ORM",          "Transacao, CartaoCredito e Categoria. Todos isolados por FK do usuário.")
        Component(templates, "Templates",     "Tailwind · Alpine.js","base.html, dashboard, lista_transacoes e formulários de CRUD.")
    }

    SystemDb_Ext(db, "PostgreSQL", "Render Free DB")

    Rel_D(user,      auth,      "Requisição HTTP")
    Rel_D(auth,      views,     "Permite acesso")
    Rel_D(views,     forms,     "Valida POST")
    Rel_D(views,     models,    "Consulta dados")
    Rel_D(views,     templates, "Renderiza HTML")
    Rel_D(forms,     models,    "Cria e atualiza")
    Rel_D(models,    db,        "ORM · psycopg2")

    UpdateElementStyle(user,      $fontColor="white", $bgColor="#08427B", $borderColor="#052E56")
    UpdateElementStyle(auth,      $fontColor="white", $bgColor="#4A90D9", $borderColor="#2C6FAC")
    UpdateElementStyle(views,     $fontColor="white", $bgColor="#1168BD", $borderColor="#0B4884")
    UpdateElementStyle(forms,     $fontColor="white", $bgColor="#4A90D9", $borderColor="#2C6FAC")
    UpdateElementStyle(models,    $fontColor="white", $bgColor="#4A90D9", $borderColor="#2C6FAC")
    UpdateElementStyle(templates, $fontColor="white", $bgColor="#D4820A", $borderColor="#A0600A")
    UpdateElementStyle(db,        $fontColor="white", $bgColor="#2D882D", $borderColor="#1B5E1B")
    UpdateRelStyle(user,      auth,      $textColor="white", $lineColor="#aaaaaa")
    UpdateRelStyle(auth,      views,     $textColor="white", $lineColor="#aaaaaa")
    UpdateRelStyle(views,     forms,     $textColor="white", $lineColor="#aaaaaa")
    UpdateRelStyle(views,     models,    $textColor="white", $lineColor="#aaaaaa")
    UpdateRelStyle(views,     templates, $textColor="white", $lineColor="#aaaaaa")
    UpdateRelStyle(forms,     models,    $textColor="white", $lineColor="#aaaaaa")
    UpdateRelStyle(models,    db,        $textColor="white", $lineColor="#aaaaaa")
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

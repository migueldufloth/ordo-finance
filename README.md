# Ordo Finance

Sistema de gestão financeira pessoal desenvolvido com foco em arquitetura orientada a serviços e escalabilidade.

## Visão Geral

A aplicação permite o controle de receitas e despesas, categorização de lançamentos e visualização de balanços financeiros. O projeto foi estruturado para demonstrar a coexistência de um monolito robusto (Django) conectado a um banco de dados na nuvem (PostgreSQL) com microserviços especializados (FastAPI), utilizando conteinerização para orquestração do ambiente.

## Arquitetura do Sistema

O sistema é composto pelos seguintes serviços:

*   **App Principal (Django):** Responsável pelo gerenciamento de usuários, regras de negócio principais (CRUD de transações), autenticação e renderização da interface (Server-Side Rendering).
*   **Microserviço de Relatórios (FastAPI):** Unidade isolada para processamento de tarefas intensivas (geração de PDF e exportação de dados), comunicando-se com o Core via API HTTP.
*   **Banco de Dados (PostgreSQL):** Armazenamento relacional centralizado.

## Arquitetura C4

### Nível 1 — Diagrama de Contexto

Visão de alto nível mostrando o sistema Ordo Finance e seus atores externos.

```mermaid
flowchart TD
    U["<b>Usuário</b><br/>Gerencia suas finanças pessoais"]
    O["<b>Ordo Finance</b><br/>Sistema de gestão financeira"]
    S["<b>Supabase</b><br/>PostgreSQL na nuvem"]

    U -->|"HTTPS"| O
    O -->|"PostgreSQL / SSL"| S

    style U fill:#08427B,stroke:#052E56,color:#fff
    style O fill:#1168BD,stroke:#0B4884,color:#fff
    style S fill:#777,stroke:#555,color:#fff
```

### Nível 2 — Diagrama de Containers

Decomposição interna do sistema, mostrando os containers que compõem a aplicação.

```mermaid
flowchart LR
    U["<b>Usuário</b><br/>Navegador Web"]

    subgraph boundary ["Sistema Ordo Finance"]
        direction TB
        DJ["<b>Aplicação Web</b><br/>Django 5.x · TailwindCSS · Alpine.js<br/><i>Auth, CRUD, Dashboard SSR</i>"]
        FA["<b>Microserviço de Relatórios</b><br/>FastAPI<br/><i>Geração de PDF e exportação</i>"]
        PG[("<b>Banco de Dados</b><br/>PostgreSQL · Supabase")]
    end

    U -->|"HTTPS"| DJ
    DJ -->|"HTTP / REST"| FA
    DJ -->|"ORM / SQL"| PG
    FA -->|"SQL"| PG

    style U fill:#08427B,stroke:#052E56,color:#fff
    style DJ fill:#1168BD,stroke:#0B4884,color:#fff
    style FA fill:#1168BD,stroke:#0B4884,color:#fff
    style PG fill:#2D882D,stroke:#1B5E1B,color:#fff
    style boundary fill:#f5f5f5,stroke:#999,color:#333
```

### Nível 3 — Diagrama de Componentes (Aplicação Web Django)

Decomposição interna do container principal, mostrando os módulos que compõem a aplicação Django.

```mermaid
flowchart TD
    subgraph django ["Aplicação Web — Django 5.x"]
        AUTH["<b>Autenticação</b><br/><i>django.contrib.auth</i>"] ~~~ DASH["<b>Dashboard</b><br/><i>views.dashboard</i>"]
        TRANS["<b>Transações</b><br/><i>FBV + Forms</i>"] ~~~ CART["<b>Cartões</b><br/><i>CBV + Forms</i>"]
        AUTH & DASH & TRANS & CART --> TPL["<b>Templates SSR</b><br/><i>TailwindCSS · Alpine.js</i>"]
    end

    PG[("<b>Banco de Dados</b><br/>PostgreSQL · Supabase")]
    django -->|"ORM / SQL"| PG

    style AUTH fill:#4A90D9,stroke:#2C6FAC,color:#fff
    style DASH fill:#4A90D9,stroke:#2C6FAC,color:#fff
    style TRANS fill:#4A90D9,stroke:#2C6FAC,color:#fff
    style CART fill:#4A90D9,stroke:#2C6FAC,color:#fff
    style TPL fill:#E67E22,stroke:#C0651A,color:#fff
    style PG fill:#2D882D,stroke:#1B5E1B,color:#fff
    style django fill:#f5f5f5,stroke:#999,color:#333
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
*   **Frontend:** TailwindCSS, Alpine.js
*   **Infraestrutura:** Docker, Docker Compose
*   **Banco de Dados:** PostgreSQL (nuvem via Supabase)

## Como Executar o Projeto

### Pré-requisitos

*   Docker e Docker Compose instalados
*   Python 3.12+ (para execução local opcional)
*   Git

### Passo a Passo (Via Docker)

1.  Clone o repositório:
    ```bash
    git clone https://github.com/migueldufloth/ordo-finance.git
    cd ordo-finance
    ```
2. Crie o arquivo `.env` na raiz do projeto com base nas suas credenciais do banco de dados na nuvem (`DATABASE_URL`).

3.  Suba os containers da aplicação:
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

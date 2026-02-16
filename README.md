# Ordo Finance

Sistema de gestão financeira pessoal desenvolvido com foco em arquitetura orientada a serviços e escalabilidade.

## Visão Geral

A aplicação permite o controle de receitas e despesas, categorização de lançamentos e visualização de balanços financeiros. O projeto foi estruturado para demonstrar a coexistência de um monolito robusto (Django) com microserviços especializados (FastAPI), utilizando conteinerização para orquestração do ambiente.

## Arquitetura do Sistema

O sistema é composto pelos seguintes serviços:

*   **App Principal (Core - Django):** Responsável pelo gerenciamento de usuários, regras de negócio principais (CRUD de transações), autenticação e renderização da interface (Server-Side Rendering).
*   **Microserviço de Relatórios (FastAPI):** Unidade isolada para processamento de tarefas intensivas (geração de PDF e exportação de dados), comunicando-se com o Core via API HTTP.
*   **Banco de Dados (PostgreSQL):** Armazenamento relacional centralizado.

## Tecnologias Utilizadas

*   **Backend:** Python 3.12+, Django 5.x, FastAPI
*   **Frontend:** TailwindCSS, Alpine.js
*   **Infraestrutura:** Docker, Docker Compose
*   **Banco de Dados:** PostgreSQL

## Como Executar o Projeto

### Pré-requisitos

*   Docker e Docker Compose instalados
*   Git

### Passo a Passo

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/seu-usuario/ordo-finance.git](https://github.com/seu-usuario/ordo-finance.git)
    cd ordo-finance
    ```

2.  Suba os containers da aplicação:
    ```bash
    docker-compose up --build
    ```

3.  Acesse a aplicação principal em: `http://localhost:8000`

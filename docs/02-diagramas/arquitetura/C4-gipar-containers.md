# Diagramas de Arquitetura — Modelo C4: GIPAR

Este documento documenta os níveis 1 (Contexto) e 2 (Contêineres) da arquitetura do GIPAR com base no modelo C4, renderizado em Mermaid.js.

---

## 1. C4 Model — Nível 1: Contexto do Sistema

Ilustra os usuários do sistema, as fronteiras da aplicação GIPAR e seus limites externos.

```mermaid
flowchart TB
    subgraph Atores["Atores e Usuários"]
        Aluno["Aluno / Estudante<br/><i>[Usuário Acadêmico]</i><br/>Consulta acervo, solicita reservas e usa Chatbot"]
        Prof["Professor / Pesquisador<br/><i>[Usuário Acadêmico]</i><br/>Reserva equipamentos para aulas e projetos"]
        Tec["Técnico de Laboratório<br/><i>[Operador]</i><br/>Registra retiradas, devoluções e manutenções"]
        Admin["Administrador<br/><i>[Gestão]</i><br/>Configura usuários, permissões e parâmetros"]
    end

    subgraph FronteiraGIPAR["Fronteira do Sistema GIPAR"]
        GIPAR["GIPAR (Gestão de Patrimônio e Recursos)<br/><i>[Aplicação Web Containerizada]</i><br/>Gerencia patrimônio, acervo laboratorial, empréstimos e chatbot"]
    end

    subgraph Armazenamento["Persistência"]
        MySQL[("Banco de Dados MySQL 8.0<br/><i>[Base Relacional]</i><br/>Tabelas de equipamentos, categorias, usuários e movimentações")]
    end

    Aluno -->|"Interage via browser e chat"| GIPAR
    Prof -->|"Solicita reservas e gerencia turmas"| GIPAR
    Tec -->|"Controla empréstimos físicos"| GIPAR
    Admin -->|"Administra sistema"| GIPAR
    GIPAR -->|"Lê e grava dados relacionais"| MySQL
```

---

## 2. C4 Model — Nível 2: Contêineres da Aplicação

Detalhamento dos contêineres Docker, tecnologias em execução e portas de comunicação.

```mermaid
flowchart TB
    subgraph ClientLayer["Cliente (Browser Web)"]
        Browser["Navegador Web<br/><i>[React 19 SPA]</i><br/>Interface responsiva e componente ChatWidget"]
    end

    subgraph DockerHost["Ambiente Docker (docker-compose)"]
        subgraph FrontContainer["gipar-frontend (Container Nginx Alpine)"]
            Nginx["Nginx Web Server<br/><i>[Porta 80 / 3000]</i><br/>Serve os assets estáticos do React e atua como Reverse Proxy em /api/"]
        end

        subgraph BackContainer["gipar-backend (Container Python 3.11-slim)"]
            FastAPI["FastAPI REST API<br/><i>[Uvicorn - Porta 8000]</i><br/>Composition root, CORS e tratamento global de erros"]
            Routers["Routers por domínio<br/><i>[FastAPI APIRouter]</i><br/>Auth, patrimônio, movimentações, relatórios e sistema"]
            Dependencies["Dependências compartilhadas<br/><i>[api/dependencies.py]</i><br/>Repositórios, configuração MySQL e permissões"]
            NLP["Pipeline NLP Chatbot<br/><i>[Scikit-Learn + RapidFuzz]</i><br/>Classificador de intenções e extrator de similaridade"]
            DBClient["Gerenciador DB<br/><i>[PyMySQL]</i><br/>Execução de queries SQL parametrizadas"]
        end

        subgraph DBContainer["gipar-mysql (Container MySQL 8.0)"]
            DB[("MySQL Database<br/><i>[Porta 3306 interna]</i><br/>Schema gipar_db e volume mysql_data")]
        end
    end

    Browser -->|"HTTP/HTTPS (Porta 3000)"| Nginx
    Nginx -->|"Proxy reverso /api/* (Porta 8000)"| FastAPI
    FastAPI --> Routers
    Routers --> Dependencies
    Routers --> NLP
    Dependencies --> DBClient
    DBClient -->|"Conexão TCP MySQL (Porta 3306)"| DB
```

---

## 3. Rastreabilidade
- **Requisitos:** `REQ-001`, `REQ-002`, `REQ-003`, `REQ-004`
- **ADRs:** `ADR-001`, `ADR-002`, `ADR-004`

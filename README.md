# GIPAR - Sistema de Controle de Componentes e Equipamentos

<p align="center">
  <img src="frontend/src/assets/imagens/LOGO-CLARO.png" alt="Logo GIPAR" width="220">
</p>

Sistema desenvolvido para o **Grupo de Inovação e Pesquisa em Automação e Robótica (GIPAR)** do **Instituto Federal da Bahia (IFBA) - Campus Vitória da Conquista**, com o objetivo de gerenciar equipamentos, componentes eletrônicos, empréstimos, devoluções, manutenções e usuários do laboratório.

> [!NOTE]
> **Sobre este Repositório (Fork Acadêmico):**  
> Este projeto é uma evolução direta e continuada a partir do repositório original [cepedi-capacita04-grupo3](https://github.com/Vandamelloz/cepedi-capacita04-grupo3).  
> 
> A **Etapa 1** do sistema foi desenvolvida durante a residência tecnológica do **Programa Bolsa Futuro Digital (CEPEDI)**.  
> A partir do fork, a **Etapa 2** dá continuidade ao projeto como **Trabalho de Conclusão de Curso (TCC)** do curso de **Bacharelado em Sistemas de Informação** do **IFBA - Campus Vitória da Conquista**:
> - **Discente:** Luiz Carlos Pereira Caetité
> - **Docente Orientador:** Prof. Dr. Crescencio Rodrigues Lima Neto

---

# Sobre o Projeto

O GIPAR é um sistema web para gerenciamento patrimonial do laboratório.

A aplicação permite controlar:

- 📦 Equipamentos
- 🔌 Componentes
- 📋 Empréstimos
- ↩️ Devoluções
- 📅 Reservas
- 🛠️ Manutenções
- 👥 Usuários
- 📊 Relatórios
- 💬 Assistência Inteligente via Chatbot *(Adicionado na Etapa 2)*

Toda a aplicação utiliza uma arquitetura desacoplada, onde o Frontend consome uma API REST desenvolvida em FastAPI.

---

# Principais Funcionalidades

### 👨‍💼 Administrador

- Cadastro de usuários
- Cadastro de equipamentos
- Cadastro de categorias
- Cadastro de componentes
- Controle de manutenções
- Controle de empréstimos
- Dashboard administrativo
- Geração de relatórios

### 👨‍🔧 Estagiário

- Registrar empréstimos
- Registrar devoluções
- Visualizar equipamentos
- Dashboard

### 👨‍🏫 Professor

- Consultar equipamentos
- Consultar empréstimos
- Consultar manutenções

### 🎓 Aluno

- Visualizar catálogo de equipamentos
- Consultar empréstimos
- Acompanhar devoluções
- Consultar regras do laboratório e disponibilidade de itens via Chatbot

---

## 🛠️ Tecnologias Utilizadas

### Backend & Inteligência Artificial
- **Linguagem:** Python 3.12+
- **Framework Web:** FastAPI & Uvicorn
- **Banco de Dados:** PyMySQL (Driver com queries parametrizadas)
- **Validação de Dados:** Pydantic
- **Autenticação & Segurança:** JWT (PyJWT), Argon2, Passlib
- **Processamento de Linguagem Natural (NLP):** Scikit-Learn (TF-IDF + Classificador Logístico) *(Etapa 2)*
- **Correspondência Aproximada de Texto:** RapidFuzz *(Etapa 2)*

### Frontend
- **Framework:** React 19
- **Build Tool:** Vite
- **Estilização:** TailwindCSS & CSS Vanilla
- **Roteamento:** React Router DOM
- **Ícones:** Lucide React
- **Componentes:** ChatWidget inteligente integrado *(Etapa 2)*

### Banco de Dados & Infraestrutura
- **SGBD:** MySQL 8.0
- **Containerização:** Docker & Docker Compose *(Etapa 2)*
- **Servidor Web & Proxy Reverso:** Nginx *(Etapa 2)*

### Governança & Documentação
- **Controle de Versão:** Git & GitHub (Fluxo de Fork)
- **Modelagem & Diagramas:** Mermaid.js (C4, Sequência e Domínio) *(Etapa 2)*
- **Base de Conhecimento:** Obsidian Vault com sincronização determinística (`generate_wiki.py`) *(Etapa 2)*

---

# Estrutura do Projeto

```
📦 cepedi-capacita04-grupo3
│
├── 📁 backend/                  # API REST em FastAPI e Módulo de Chat
│   ├── 📁 chat/                 # Pipeline de NLP, catálogo e regras do Chatbot (Etapa 2)
│   ├── 📁 gerenciador_db/       # Camada de persistência (MySQL)
│   ├── 📁 models/               # Modelos Pydantic
│   ├── 📁 servicos/             # Regras de negócio e serviços auxiliares
│   ├── 📁 tests/                # Testes unitários do backend e IA
│   ├── Dockerfile               # Imagem Docker do Backend (Etapa 2)
│   └── main.py                  # Ponto de entrada da API
│
├── 📁 frontend/                 # Single Page Application (React + Vite)
│   ├── 📁 src/
│   │   ├── 📁 components/       # Componentes reutilizáveis (inclui ChatWidget)
│   │   ├── 📁 pages/            # Telas do sistema (Login, Dashboard, Catálogo, etc.)
│   │   └── 📁 services/         # Clientes HTTP e serviços de API
│   ├── Dockerfile               # Build multi-estágio do Frontend (Etapa 2)
│   └── nginx.conf               # Configuração do Nginx com proxy /api/ (Etapa 2)
│
├── 📁 docker/                   # Recursos de containerização (Etapa 2)
│   └── 📁 mysql/
│       └── init.sql             # DDL unificado e carga de 445 equipamentos
│
├── 📁 docs/                     # Documentação viva do projeto
│   ├── 📁 01-requisitos/        # Requisitos evolutivos (REQ) e regras de negócio (Etapa 2)
│   ├── 📁 02-diagramas/         # Diagramas C4 e de arquitetura em Mermaid (Etapa 2)
│   ├── 📁 03-adrs/              # Architecture Decision Records (Etapa 2)
│   ├── 📁 manuais/              # Manuais de uso (inclui manual do Chatbot)
│   └── 📁 scripts/              # Gerador de Wiki Obsidian (generate_wiki.py)
│
├── docker-compose.yml           # Orquestração de containers (Etapa 2)
├── docker-compose.override.yml  # Configuração de portas para desenvolvimento local
├── LICENSE                      # Licença MIT
└── README.md
```

---

# 🚀 Como Executar o Projeto

### Opção 1: Execução com Docker (Recomendada — Etapa 2)

A forma mais rápida e padronizada de executar todo o ecossistema (MySQL, Backend e Frontend com Nginx):

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/DevLuizin/gipar-tcc.git
   cd gipar-tcc
   ```

2. **Inicie os containers:**
   ```bash
   docker compose up -d --build
   ```

3. **Acesse as aplicações:**
   - **Frontend:** [http://localhost:5173](http://localhost:5173) (ou porta 80)
   - **API FastAPI (Documentação Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **MySQL:** Porta `3307` (mapeada no localhost via `docker-compose.override.yml`)

---

### Opção 2: Execução Manual Local (Etapa 1)

Caso prefira executar os serviços diretamente na sua máquina hospedeira:

#### 1 - Ambiente Virtual do Backend

```bash
cd backend
python -m venv venv
```

Ativação do ambiente:
- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (CMD):** `venv\Scripts\activate`
- **Linux/macOS:** `source venv/bin/activate`

Instale as dependências:
```bash
pip install -r requirements.txt
```

#### 2 - Banco de Dados MySQL

Crie a base de dados `gipar_db` no seu servidor MySQL local e carregue o script inicial contido em `docker/mysql/init.sql` (ou `backend/banco.txt`).

Configure as variáveis no arquivo `backend/.env` (baseie-se no `backend/.env.example`):
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=gipar_db
```

#### 3 - Executar o Backend

```bash
python -m uvicorn main:app --reload
```
A API estará rodando em [http://127.0.0.1:8000](http://127.0.0.1:8000).

#### 4 - Executar o Frontend

Em outro terminal:
```bash
cd frontend
npm install
npm run dev
```
A aplicação abrirá em [http://localhost:5173](http://localhost:5173).

---

## 👥 Perfis de Usuário

| Perfil | Permissões |
| :--- | :--- |
| 👨‍💼 **Administrador** | Controle total do sistema, usuários, relatórios e auditoria |
| 👨‍🏫 **Professor** | Consulta equipamentos, reservas, manutenções e empréstimos |
| 👨‍🔧 **Estagiário** | Operacionalização de empréstimos, devoluções e vistorias |
| 🎓 **Aluno** | Consulta do catálogo, regras do laboratório e acompanhamento de empréstimos |

---

# Funcionalidades do Sistema

### 📋 Funcionalidades da Base (Etapa 1 — CEPEDI)
- Dashboard Administrativo e Operacional
- Autenticação e Controle de Sessão via JWT
- Gestão completa de usuários, equipamentos, categorias e componentes
- Fluxo de empréstimos, devoluções e reservas
- Controle e acompanhamento de manutenções
- Histórico de movimentações e trilha de auditoria
- Exportação de dados em formatos PDF e CSV
- API REST com endpoints documentados

---

### 🚀 Extensões Implementadas na Etapa 2 (TCC — Em Andamento)

As seguintes extensões foram implementadas a partir dos commits da continuidade do projeto:

1. **🤖 Módulo de Assistente Virtual / Chatbot Inteligente (NLP Local):**
   - **Classificação Supervisionada de Intenções:** Pipeline de Processamento de Linguagem Natural treinado com Scikit-Learn (`TfidfVectorizer` + `LogisticRegression`), operando 100% offline, sem custos de API e com inferência instantânea.
   - **Busca Aproximada no Catálogo (Fuzzy Matching):** Integração com `RapidFuzz` para busca inteligente sobre os 445 equipamentos cadastrados, tolerando erros de digitação e ausência de acentos.
   - **Base de Regras Laboratoriais:** Respostas automáticas sobre procedimentos de empréstimo, prazos e normas de utilização do laboratório GIPAR.
   - **Interface Conversacional Flutuante:** Componente React `ChatWidget.jsx` integrado ao frontend, com histórico na sessão e sugestões de perguntas.

2. **🐳 Orquestração e Containerização Completa:**
   - Padronização em Docker para MySQL 8.0, Backend FastAPI e Frontend React/Nginx.
   - Configuração de proxy reverso `/api/` no Nginx, eliminando falhas de CORS e simplificando rotas.
   - Inicialização resiliente (`entrypoint.sh`) com detecção de prontidão do banco e carga de sementes de usuários de teste.

3. **📐 Engenharia de Requisitos, Arquitetura e Governança:**
   - Catalogação formal de requisitos evolutivos (`docs/01-requisitos/requisitos/REQ-001.md` a `REQ-003.md`) e regras de negócio (`regras-negocio.md`).
   - Registros de Decisão de Arquitetura (`docs/03-adrs/ADR-001.md` a `ADR-003.md`).
   - Diagramas C4 (Contexto, Container e Componente) e diagramas de sequência em Mermaid.js.
   - Manual completo de uso do Chatbot (`docs/manuais/manual-usuario-chatbot.md`).
   - Script determinístico de sincronização para Wiki em cofre Obsidian (`docs/scripts/generate_wiki.py`).

---

# 👨‍💻 Equipe e Autoria do Projeto

### 🏛️ Etapa 1: Desenvolvimento da Base (CEPEDI)
Projeto concebido e desenvolvido durante a 2ª fase da residência tecnológica do **Programa Bolsa Futuro Digital (CEPEDI)**.

**Backend:**
- Alexandro Costa Santos
- Francis Ricardo Silva Conceição
- Helen da Cruz Nascimento
- Pedro Paulo Santos Silva
- Vanderléia dos Santos Mello (Scrum Master)
- Yan Mangabeira

**Frontend:**
- Hiago Alves da Silva
- Isabela Sousa Damasceno
- Paulo Victor Almeida de Oliveira
- Paulo Vitor Dias Soares

---

### 🎓 Etapa 2: Extensão e Continuidade (TCC — IFBA)
Continuidade e expansão técnica desenvolvidas como Trabalho de Conclusão de Curso (TCC) no **Bacharelado em Sistemas de Informação** do **Instituto Federal da Bahia (IFBA) - Campus Vitória da Conquista**.

- **Discente:** Luiz Carlos Pereira Caetité
- **Docente Orientador:** Prof. Dr. Crescencio Rodrigues Lima Neto
- **Repositório Original:** [Vandamelloz/cepedi-capacita04-grupo3](https://github.com/Vandamelloz/cepedi-capacita04-grupo3)
- **Escopo das Extensões:** Assistente virtual inteligente com NLP local, arquitetura conteinerizada com Docker/Nginx e governança viva de arquitetura e requisitos.

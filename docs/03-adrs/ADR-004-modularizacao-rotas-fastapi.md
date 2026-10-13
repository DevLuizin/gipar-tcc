# ADR-004: Modularização das Rotas FastAPI com APIRouter

**Status:** Aprovada
**Data:** 2026-10-12
**Decisores:** Luiz
**Requisitos Relacionados:** Não aplicável — refatoração sem mudança funcional

---

## 1. Contexto do Problema

O arquivo `backend/main.py` concentrava a configuração da aplicação, middlewares,
dependências de banco e todas as rotas de negócio. Com mais de mil linhas e 45
operações HTTP próprias, essa concentração aumentava o acoplamento, dificultava a
navegação por domínio e ampliava o risco de conflitos durante manutenção.

A reorganização precisava preservar integralmente o contrato HTTP consumido pelo
frontend, inclusive caminhos, métodos, modelos, permissões, respostas e os dois
prefixos existentes do chatbot.

## 2. Decisão Adotada

Adotar `APIRouter` e organizar as rotas por domínio em
`backend/api/routers/`. O arquivo `backend/main.py` permanece como composition
root, responsável por criar a aplicação FastAPI, configurar CORS e tratamento
global de erros e registrar os routers.

As instâncias compartilhadas dos repositórios, a configuração de banco e as
dependências de autorização ficam em `backend/api/dependencies.py`. Essa camada
evita que os routers importem `main.py` e, consequentemente, evita dependências
circulares.

Nesta etapa, os corpos das operações, queries SQL e regras existentes foram
somente movidos. A aplicação continua usando PyMySQL e o comando de inicialização
permanece `uvicorn main:app`.

## 3. Alternativas Consideradas

### Alternativa A: Manter todas as rotas em `main.py`

- **Vantagens:** Nenhuma movimentação imediata de código.
- **Desvantagens:** Mantém o alto acoplamento e o custo de manutenção do arquivo
  monolítico.
- **Motivo do descarte:** Não atende à necessidade de organização por domínio.

### Alternativa B: Introduzir simultaneamente services, repositories e ORM

- **Vantagens:** Produziria uma separação arquitetural mais profunda em um único
  ciclo.
- **Desvantagens:** Alteraria persistência e regras ao mesmo tempo que as rotas,
  dificultando a identificação de regressões.
- **Motivo do descarte:** O objetivo desta decisão é uma refatoração incremental,
  com o mínimo de mudanças comportamentais.

### Alternativa C: Um único módulo de rotas separado de `main.py`

- **Vantagens:** Reduziria o tamanho do ponto de entrada.
- **Desvantagens:** Apenas transferiria o arquivo monolítico para outro local.
- **Motivo do descarte:** Não melhora a coesão por domínio.

## 4. Consequências e Impactos

### Consequências Positivas

- `main.py` passa a representar claramente a composição da aplicação.
- Rotas relacionadas ficam agrupadas por domínio.
- Novos testes podem substituir dependências compartilhadas de forma localizada.
- A divisão prepara ciclos futuros de extração de regras para serviços.

### Consequências Negativas / Trade-offs

- Os routers ainda contêm regras, SQL direto e efeitos colaterais herdados.
- `api/dependencies.py` mantém singletons globais para preservar o ciclo de vida
  existente.
- Há mais módulos Python para navegar e registrar.

## 5. Rastreabilidade e Conformidade

- **Requisitos:** Não aplicável; não há requisito funcional novo.
- **Regras de Negócio:** Todas as regras existentes permanecem inalteradas.
- **Implementação:** `backend/main.py`, `backend/api/dependencies.py`,
  `backend/api/routers/` e `backend/tests/test_api_contract.py`.
- **Diagramas Relacionados:**
  `docs/02-diagramas/arquitetura/C4-gipar-containers.md`.

## Notas manuais

<!-- MANUAL:START -->
_Espaço preservado para anotações manuais e complementos do desenvolvedor._
<!-- MANUAL:END -->



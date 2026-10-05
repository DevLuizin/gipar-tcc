# Diagrama de Sequência — SEQ-01: Fluxos Conversacionais do Chatbot

Este documento detalha os fluxos temporais de troca de mensagens entre o Aluno, o componente de interface React, a API FastAPI, o pipeline NLP (Scikit-Learn + RapidFuzz) e o banco MySQL.

---

## 1. Fluxo Principal: Consulta de Item Específico

```mermaid
sequenceDiagram
    autonumber
    actor Aluno as Aluno / Bolsista
    participant UI as React UI (ChatWidget)
    participant API as FastAPI (/api/chat)
    participant NLP as Pipeline NLP (Scikit-Learn)
    participant Fuzz as Extrator Entidade (RapidFuzz)
    participant DB as MySQL (gipar_db)

    Aluno->>UI: Digita: "Tem Arduino Mega disponivel?"
    UI->>API: POST /api/chat { "message": "Tem Arduino Mega disponivel?" }
    
    API->>NLP: predict_intent("Tem Arduino Mega disponivel?")
    NLP-->>API: Intenção: "consultar_disponibilidade" (0.95)

    API->>Fuzz: match_item("Tem Arduino Mega disponivel?", acervo)
    Fuzz-->>API: Match Único: "Arduino mega2560" (Score: 92%)

    API->>DB: SELECT quantidade, status FROM equipamento WHERE nome = 'Arduino mega2560'
    DB-->>API: { quantidade: 42, status: 'DISPONIVEL' }

    API->>API: Formata resposta direta
    API-->>UI: 200 OK { "reply": "Sim! Temos 42 unidades de 'Arduino mega2560' disponíveis no laboratório." }
    UI-->>Aluno: Exibe balão de resposta na tela
```

---

## 2. Fluxo de Desambiguação Proativa (Termo Genérico: Ex. "jumper")

```mermaid
sequenceDiagram
    autonumber
    actor Aluno as Aluno / Bolsista
    participant UI as React UI (ChatWidget)
    participant API as FastAPI (/api/chat)
    participant Fuzz as Extrator Entidade (RapidFuzz)
    participant DB as MySQL (gipar_db)

    Aluno->>UI: Digita: "Tem jumper pra bancada?"
    UI->>API: POST /api/chat { "message": "Tem jumper pra bancada?" }

    API->>Fuzz: match_items("jumper", acervo)
    Note over Fuzz: Detecta múltiplos itens com termo "jumper"
    Fuzz-->>API: Matches: ["jumper femea x femea", "jumper macho x macho", "jumper macho x femea"]

    API->>DB: SELECT nome, quantidade FROM equipamento WHERE nome IN (...) AND status = 'DISPONIVEL'
    DB-->>API: [ { femea x femea: 950 }, { macho x macho: 165 }, { macho x femea: 1 } ]

    API->>API: Monta lista desambiguadora com contagens
    API-->>UI: 200 OK { "reply": "Temos as seguintes opções de jumper disponíveis:\n- jumper femea x femea: 950 unidades\n- jumper macho x macho: 165 unidades\n- jumper macho x femea: 1 unidade\nQual dessas opções você precisa?" }
    UI-->>Aluno: Exibe opções e aguarda escolha do aluno
```

---

## 3. Fluxo de Exceção: Item Indisponível (Esgotado / Em Manutenção)

```mermaid
sequenceDiagram
    autonumber
    actor Aluno as Aluno / Bolsista
    participant UI as React UI (ChatWidget)
    participant API as FastAPI (/api/chat)
    participant Fuzz as Extrator Entidade (RapidFuzz)
    participant DB as MySQL (gipar_db)

    Aluno->>UI: Digita: "Tem Placa de fenolite livre?"
    UI->>API: POST /api/chat { "message": "Tem Placa de fenolite livre?" }

    API->>Fuzz: match_item("Placa de fenolite", acervo)
    Fuzz-->>API: Match: "Placa de fenolite" (Score: 100%)

    API->>DB: SELECT quantidade, status FROM equipamento WHERE nome = 'Placa de fenolite'
    DB-->>API: { quantidade: 0, status: 'MANUTENCAO' }

    Note over API: Aplica RN-010 (Resposta Simples e Objetiva)
    API-->>UI: 200 OK { "reply": "Item indisponível no momento." }
    UI-->>Aluno: Exibe: "Item indisponível no momento."
```

---

## 4. Fluxo de Exceção: Item Não Cadastrado no Acervo

```mermaid
sequenceDiagram
    autonumber
    actor Aluno as Aluno / Bolsista
    participant UI as React UI (ChatWidget)
    participant API as FastAPI (/api/chat)
    participant Fuzz as Extrator Entidade (RapidFuzz)

    Aluno->>UI: Digita: "Tem ferro de solda de 100W?"
    UI->>API: POST /api/chat { "message": "Tem ferro de solda de 100W?" }

    API->>Fuzz: match_item("ferro de solda de 100W", acervo)
    Note over Fuzz: Similaridade máxima < 75%
    Fuzz-->>API: Nenhum match qualificado (None)

    Note over API: Aplica RN-010 (Resposta Simples e Objetiva)
    API-->>UI: 200 OK { "reply": "Item não cadastrado no acervo." }
    UI-->>Aluno: Exibe: "Item não cadastrado no acervo."
```

---

## 5. Rastreabilidade
- **Requisito:** [[docs/01-requisitos/requisitos/REQ-001-chatbot-atendimento|REQ-001]]
- **Regras de Negócio:** `RN-008`, `RN-009`, `RN-010`, `RN-011`
- **Diagrama de Casos de Uso:** [[docs/02-diagramas/casos-de-uso/UC-01-atendimento-chatbot|UC-01]]

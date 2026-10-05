# ADR-002: Arquitetura de Processamento de Linguagem Natural (NLP) do Chatbot

**Status:** Aprovada  
**Data:** 2026-10-04  
**Decisores:** Equipe de Desenvolvimento GIPAR  
**Requisitos Relacionados:** REQ-001  
**Regras de Negócio:** RN-008, RN-009, RN-010  

---

## 1. Contexto do Problema
O GIPAR necessita de um chatbot conversacional para que alunos, professores e técnicos possam consultar o status e a disponibilidade de 445 itens de laboratório diretamente em linguagem natural. A solução precisa rodar em hardware institucional compartilhado, ter latência mínima (<500ms), alta acurácia com pequeno volume de dados de treino e capacidade de tolerar erros ortográficos frequentes nos nomes de equipamentos (ex: *"osciloscopio"*, *"multimetro dijital"*, *"ardúino"*).

## 2. Decisão Adotada
Adotar uma arquitetura híbrida em Python composta por duas etapas desacopladas:
1. **Classificação de Intenção com Scikit-Learn:** Vetorização de texto utilizando `TfidfVectorizer` (com n-gramas de caracteres/palavras) combinada com classificador supervisionado linear (`LogisticRegression` ou `MultinomialNB`). Essa etapa determina o que o usuário quer fazer (ex: saudar, consultar disponibilidade, consultar localização, pedir regras).
2. **Extração de Entidades por Similaridade com RapidFuzz:** Algoritmo de correspondência aproximada (`fuzz.token_sort_ratio`) executado sobre o dicionário dos 445 itens de patrimônio cadastrados no MySQL, com limiar mínimo de similaridade de 75%.
3. **Orquestração via FastAPI:** Exposição do endpoint `/api/chat` executando a inferência em memória e consultas dinâmicas otimizadas no MySQL.
4. **Interface Visual:** Biblioteca `@chatscope/chat-ui-kit-react` no frontend React.

## 3. Alternativas Consideradas
### Alternativa A: Redes Neurais Profundas com TensorFlow / Keras (LSTM / Transformers)
- **Vantagens:** Capacidade de aprendizado profundo de contexto longo.
- **Desvantagens:** Alto consumo de memória RAM (>500MB a 2GB), dependência pesada de CPU/GPU, tempo de inferência elevado, risco de overfitting com datasets pequenos (<500 frases) e complexidade de manutenção.
- **Motivo do descarte:** Conforme detalhado no estudo de viabilidade técnica ([`docs/estudo_viabilidade_chatbot.md`](file:///c:/Users/Luiz/Documents/BSI/TCC/Projeto/cepedi-capacita04-grupo3/docs/estudo_viabilidade_chatbot.md)), o TensorFlow é desnecessariamente pesado e inviável para servidores institucionais de baixo custo.

### Alternativa B: Modelos de Linguagem Generativos Proprietários (OpenAI GPT, Gemini API)
- **Vantagens:** Fluência conversacional extrema.
- **Desvantagens:** Dependência de conexão com internet externa, custos recorrentes por token (inviável para projeto público/acadêmico sem verba dedicada), risco de alucinação de dados patrimoniais e latência de rede.
- **Motivo do descarte:** O sistema deve operar localmente e de forma totalmente determinística e auditável.

## 4. Consequências e Impactos
### Consequências Positivas
- Consumo mínimo de memória (<50MB) e uso desprezível de CPU.
- Execução local dentro do próprio container existente do backend FastAPI (`gipar-backend`).
- Treinamento instantâneo do modelo (<2 segundos) quando novas intenções forem adicionadas.
- Tolerância robusta a erros de digitação e acentuação nos 445 itens através do RapidFuzz.

### Consequências Negativas / Trade-offs
- Diálogos limitados a interações estruturadas de pergunta-resposta (não suporta conversas abertas e divagações filosóficas fora do domínio).

## 5. Rastreabilidade e Conformidade
- **Requisitos:** `REQ-001`.
- **Regras de Negócio:** `RN-008`, `RN-009`, `RN-010`.
- **Estudo Técnico:** [`docs/estudo_viabilidade_chatbot.md`](file:///c:/Users/Luiz/Documents/BSI/TCC/Projeto/cepedi-capacita04-grupo3/docs/estudo_viabilidade_chatbot.md).
- **Diagramas:** `docs/02-diagramas/sequencia/SEQ-01-consulta-chatbot.md`.

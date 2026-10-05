# Estudo de Viabilidade Técnica e Arquitetura: Chatbot GIPAR

> **Documento de Análise e Especificação de Arquitetura**  
> **Objetivo:** Implementação de Assistente Virtual para consulta de disponibilidade de itens, regras e empréstimos do laboratório GIPAR.  
> **Restrição de Projeto:** Custo zero com APIs externas de IA e consumo mínimo de recursos de hardware em servidor de produção.

---

## 1. Resumo Executivo e Veredito

| Critério | Avaliação | Justificativa Técnica |
| :--- | :--- | :--- |
| **Viabilidade Técnica** | **100% Viável** | A stack proposta resolve exatamente o problema sem complexidade excessiva. |
| **Consumo de Recursos** | **Extremamente Leve** | Modelo ocupa < 2 MB em disco e roda com ~30-50 MB de RAM. |
| **Custo Financeiro** | **R$ 0,00** | Funciona 100% *on-premises* / no servidor local sem dependência de nuvem. |
| **Precisão de Resposta** | **Alta (Determinística)** | Não "alucina" dados: busca o estoque e os status reais no MySQL. |
| **Tempo de Resposta** | **Ultra Rápido (< 10 ms)** | O processamento TF-IDF e Levenshtein roda em microssegundos no CPU. |

---

## 2. Comparativo Tecnológico: Por que sua proposta é a ideal?

```
┌───────────────────────────┬──────────────────┬───────────────┬────────────────────────┐
│ Abordagem                 │ Consumo de RAM   │ Custo         │ Risco de Alucinação   │
├───────────────────────────┼──────────────────┼───────────────┼────────────────────────┤
│ LLM Local (Ollama / 8B)   │ 6 GB a 16 GB     │ Requer GPU    │ Médio                  │
│ API Paga (OpenAI / Claude)│ ~50 MB (Cliente) │ Pago em dólar │ Baixo (com RAG)        │
│ TensorFlow Tradicional    │ 1.5 GB a 2 GB    │ Zero          │ Zero (se classificação)│
│ TF-IDF + RapidFuzz (Sua)  │ ~30 MB a 50 MB   │ Zero          │ Zero                   │
└───────────────────────────┴──────────────────┴───────────────┴────────────────────────┘
```

A abordagem proposta ganha com folga de qualquer outra para o contexto institucional do IFBA.

---

## 3. Como Funciona o Pipeline de Processamento da Mensagem

O fluxo de funcionamento do chatbot opera em **5 etapas sequenciais**:

```
Usuário digita: "Tem algum arduino uno pra pegar hoje?"
   │
   ▼
[Etapa 1: Pré-processamento e TF-IDF]
Transforma a frase em vetor matemático de frequência de palavras.
   │
   ▼
[Etapa 2: Classificação de Intenção (scikit-learn)]
Identifica: INTENCAO = "consultar_disponibilidade" (Probabilidade: 98%)
   │
   ▼
[Etapa 3: Extração de Entidade via Fuzzy Matching (RapidFuzz)]
Compara tokens contra a lista de 445 itens do banco de dados.
Encontra: "arduino uno" -> Equipamento ID: 12 ("Arduino uno", Similaridade: 100%)
   │
   ▼
[Etapa 4: Consulta Dinâmica no Banco MySQL]
Executa: SELECT quantidade, status FROM equipamento WHERE id = 12;
Calcula: Total (6) - Emprestados (2) - Reservados (1) = 3 Disponíveis.
   │
   ▼
[Etapa 5: Resposta Formatada ao Usuário]
"✅ Temos 3 unidades de 'Arduino uno' disponíveis para empréstimo no momento!"
```

---

## 4. As 5 Intenções Principais do Chatbot

Para um modelo baseado em classificação supervisionada, treinamos o classificador com exemplos de frases organizadas em classes (*intents*):

1. **`consultar_disponibilidade`**
   - *"Tem multímetro sobrando?"*
   - *"Posso pegar um ESP32?"*
   - *"O osciloscópio está livre?"*
2. **`meus_emprestimos`** (Exige JWT / Usuário Logado)
   - *"O que eu tenho emprestado?"*
   - *"Tenho algum item atrasado?"*
   - *"Qual o prazo de devolução dos meus itens?"*
3. **`regras_laboratorio`**
   - *"Quantos itens posso pegar ao mesmo tempo?"*
   - *"Como funciona a reserva?"*
   - *"O que acontece se eu atrasar a devolução?"*
4. **`horario_localizacao`**
   - *"Onde fica o GIPAR?"*
   - *"Qual o horário de funcionamento do laboratório?"*
5. **`saudacao_e_ajuda`**
   - *"Olá", "Bom dia", "O que você sabe fazer?"*

---

## 5. Análise de Ajustes Necessários na Aplicação Atual

Para que o chatbot funcione de maneira integrada e sem fricções, os seguintes ajustes na aplicação existente são recomendados:

### No Backend (FastAPI / Banco de Dados)
1. **Cache de Nomes de Itens para o RapidFuzz**:
   - Para não fazer `SELECT nome FROM equipamento` a cada mensagem que o usuário envia, carregar os 445 nomes dos equipamentos em memória (lista/dicionário Python) na inicialização da API ou atualizar a cada 10 minutos.
2. **Cálculo Real de Disponibilidade**:
   - Como vimos na análise anterior, a tabela `equipamento` possui `quantidade` e `status`. A consulta do bot deve checar os empréstimos ativos para saber a disponibilidade líquida:
     $$\text{Disponíveis} = \text{Quantidade Total} - \text{Empréstimos Ativos} - \text{Reservas Ativas}$$
3. **Autenticação no endpoint `/chat`**:
   - O endpoint do chat deve receber o cabeçalho `Authorization: Bearer <token>` via injeção `Depends(obter_usuario_atual)` para que o bot saiba quem é o aluno/professor quando ele perguntar *"O que eu peguei emprestado?"*.
4. **PyMySQL vs SQLAlchemy**:
   - Como o seu backend já utiliza **PyMySQL com DictCursor** de forma padronizada em todos os repositórios (`backend/gerenciador_db/`), **não é estritamente necessário adicionar o SQLAlchemy**. É perfeitamente viável e mais coeso manter o padrão com PyMySQL criando o `ChatbotRepositorio`. Se preferir SQLAlchemy, pode instalá-lo pontualmente sem conflitos.

### No Frontend (React)
1. **Interface do Chat**:
   - Adicionar um botão flutuante redondo (ícone de balão de mensagem) no canto inferior direito do [`LayoutUsuario.jsx`](file:///c:/Users/Luiz/Documents/BSI/TCC/Projeto/cepedi-capacita04-grupo3/frontend/src/layouts/usuario/LayoutUsuario.jsx).
   - Utilizar a biblioteca `@chatscope/chat-ui-kit-react` ou construir um componente nativo em React com TailwindCSS (com balões de mensagem, rolagem automática e indicador de digitação).

---

## 6. Roteiro Passo a Passo para Futura Implementação

Quando formos implementar, as etapas serão:

### Fase 1: Criação do Dataset de Treino e Pipeline de ML (Backend)
- Criar um arquivo simples `backend/chatbot/dados_treinamento.json` com ~20 a 30 variações de frases por intenção.
- Criar script `treinar_modelo.py` que usa `TfidfVectorizer(ngram_range=(1,2))` + `LogisticRegression()` e salva o modelo compilado em `modelo_chatbot.joblib` (tamanho: ~200 KB).
- Tempo de treino do modelo: **menos de 0,5 segundo**!

### Fase 2: Implementação do Extrator com RapidFuzz
- Implementar a função `extrair_item(texto_usuario, lista_itens)` utilizando `rapidfuzz.process.extractOne()` com pontuação de corte (threshold de confiança, ex: 65%).
- Se o usuário digitar *"arduinno uno"* com dois 'n', o RapidFuzz encontra *"Arduino uno"* com ~93% de similaridade.

### Fase 3: Rota e Orquestrador FastAPI
- Criar módulo `backend/chatbot/chatbot_service.py` e a rota `POST /chat` no `main.py`.
- Formatar as respostas com emojis e clareza.

### Fase 4: Integração no Frontend
- Instalar ou criar o componente de chat flutuante no React.
- Consumir o endpoint `/api/chat` usando o mesmo token de sessão já existente no `AuthContext`.

---

## 7. Conclusão

A ideia é **altamente recomendada** para um trabalho acadêmico e institucional: demonstra maturidade de engenharia de software ao escolher a ferramenta certa para o tamanho certo do problema, sem onerar a infraestrutura do IFBA com custos de nuvem ou servidores pesados.

---

## 8. Seção Comparativa Específica: Scikit-Learn (+ RapidFuzz) vs. TensorFlow

Esta seção apresenta um comparativo técnico aprofundado entre a solução proposta (**Scikit-Learn com TF-IDF + Regressão Logística e RapidFuzz**) e o uso de uma rede neural com **TensorFlow / Keras**, orientando a decisão de projeto para o ambiente institucional do IFBA.

### 8.1. Tabela Comparativa de Métricas Técnicas

| Métrica / Aspecto | Scikit-Learn + RapidFuzz (Proposta) | TensorFlow / Keras (Rede Neural) | Impacto no Projeto GIPAR |
| :--- | :--- | :--- | :--- |
| **Tamanho da Imagem Docker** | Adiciona **~80 MB** à imagem | Adiciona **~1.5 GB a 2.2 GB** à imagem | Scikit-Learn mantém o container leve e o deploy rápido. |
| **Consumo de Memória RAM** | **~30 MB a 50 MB** | **~800 MB a 1.5 GB** | TensorFlow pode derrubar servidores modestos (VPS com 1-2 GB de RAM). |
| **Tempo de Treinamento** | **< 0,5 segundo** (na CPU) | **30 a 120 segundos** (por épocas) | Scikit-Learn permite retreinar o bot dinamicamente a cada deploy. |
| **Tempo de Inferência (Resposta)** | **< 2 milissegundos** | **30 a 100 milissegundos** (na CPU) | Resposta do Scikit-Learn é imperceptível para o usuário final. |
| **Volume de Dados para Treino** | **15 a 30 frases** por intenção já dão 95%+ de acurácia | Exige **centenas/milhares** de frases para não sofrer *overfitting* | O GIPAR possui um vocabulário restrito e focado no laboratório. |
| **Extração de Itens do Catálogo** | **Nativa e Tolerante** (Levenshtein do RapidFuzz com 445 itens) | **Não resolve sozinho** (Exige modelo de NER separado ou o próprio RapidFuzz) | O TensorFlow sozinho só descobre a intenção, não extrai o item com tolerância a erros. |
| **Dependências de Sistema** | Padrão Python (rodando em qualquer Linux/Alpine) | Exige compiladores pesados, libc compatível e binários de GPU/AVX | TensorFlow frequentemente gera incompatibilidades em builds Docker slim. |

---

### 8.2. Análise de Vantagens e Desvantagens

#### A) TensorFlow (Deep Learning / Keras)
* **Vantagens:**
  * **Poder de Representação em Grande Escala:** Excelente para cenários de Big Data com milhões de conversas, análise sentimental complexa ou geração de linguagem livre (Seq2Seq).
  * **Embeddings Neurais Complexos:** Capaz de aprender dependências sintáticas e semânticas não-lineares em textos longos.
* **Desvantagens:**
  * **"Canhão para matar mosquito" (*Overkill*):** Para classificar apenas 5 a 8 intenções bem delimitadas de um laboratório (disponibilidade, meus empréstimos, regras, horários), uma rede neural profunda introduz complexidade e peso desnecessários.
  * **Problema de *Overfitting* com Poucos Dados:** Com poucas amostras de texto (como é o caso de um bot de lab com ~150 frases de exemplo), redes neurais profundas tendem a memorizar os dados de treino e falham em generalizar variações reais de usuários.
  * **Falta de Suporte a Busca Aproximada de Catálogo:** Uma rede neural de classificação apenas aponta a classe (`consultar_disponibilidade`). Para identificar que *"arduinno uno"* refere-se ao item `ID 12`, você ainda teria que instalar uma biblioteca como o RapidFuzz ou treinar um modelo pesado de *Named Entity Recognition* (NER).

#### B) Scikit-Learn com TF-IDF + RapidFuzz (Abordagem Proposta)
* **Vantagens:**
  * **Alta Precisão com Poucos Dados:** Modelos lineares probabilísticos (como Regressão Logística ou Naive Bayes) com n-gramas do TF-IDF convergem perfeitamente mesmo com pouquíssimas frases de treino.
  * **Eficiência Operacional Extrema:** O bot pode rodar dentro do próprio container do backend FastAPI existente sem elevar o uso de CPU ou memória do servidor da instituição.
  * **Combinação Híbrida Ideal:** O Scikit-Learn resolve o problema da **intenção** (*o que o aluno quer*) e o RapidFuzz resolve o problema da **entidade do acervo** (*qual dos 445 itens ele quer, mesmo se escreveu errado*).
  * **Custo de Manutenção Mínimo:** Se a equipe quiser adicionar uma nova intenção (ex: *"como descartar baterias"*), basta adicionar 5 linhas em um JSON e o modelo se atualiza em milissegundos.
* **Desvantagens:**
  * Não processa contextos conversacionais profundos de múltiplos turnos complexos (mas o escopo de consulta patrimonial do GIPAR opera em turnos diretos de pergunta e resposta).

---

### 8.3. Veredito: Qual a Melhor Solução para a Atividade?

> **Veredito Técnico:** Para o projeto GIPAR, a melhor solução é sem dúvidas o **Scikit-Learn com TF-IDF e Regressão Logística em conjunto com o RapidFuzz**.

**Motivos da escolha:**
1. **Adequação ao Domínio:** O universo do GIPAR é fechado e transacional (consultar itens, prazos e regras). Ele não necessita de redes neurais generativas ou convolucionais.
2. **Sustentabilidade Institucional:** A aplicação rodará em servidor institucional com recursos computacionais finitos que devem ser compartilhados com o MySQL, a API e o Frontend. O Scikit-Learn garante que o chatbot não consumirá mais de 5% da memória da máquina.
3. **Maturidade de Engenharia (Defesa no TCC):** Em bancas acadêmicas e avaliações de software, adotar a arquitetura mais simples, rápida e barata que resolva 100% do problema é considerado um sinal de maturidade técnica e boa prática de engenharia (*Princípio KISS - Keep It Simple, Stupid* e navalha de Occam), ao passo que utilizar TensorFlow para classificar 5 intenções seria classificado como superdimensionamento desnecessário de arquitetura (*overengineering*).

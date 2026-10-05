---
id: REQ-001
titulo: "Chatbot de Atendimento e Consulta de Patrimônio"
status: "🟡 Em análise"
tipo: "Nova funcionalidade"
modulo: "Chatbot"
origem: "Nova necessidade"
tags: [requisito, chatbot, nlp, scikit-learn, rapidfuzz, fastapi, react]
---

# REQ-001 — Chatbot de Atendimento e Consulta de Patrimônio

**Status:** 🟡 Em análise  
**Tipo:** Nova funcionalidade  
**Módulo:** Chatbot  
**Origem:** Nova necessidade / Levantamento com usuários  

---

## 1. Contexto
O GIPAR gerencia o acervo laboratorial da instituição, composto atualmente por mais de 440 itens (placas de desenvolvimento, sensores, jumpers, componentes passivos, instrumentação e ferramentas). O atendimento no balcão do laboratório frequentemente enfrenta filas ou interrupções do trabalho dos técnicos para responder dúvidas repetitivas de alunos e bolsistas que necessitam saber se há peças livres para suas aulas práticas, projetos de extensão ou TCC.

## 2. Problema / Necessidade (Perspectiva do Usuário)
- **Persona Principal:** Aluno de graduação / pós-graduação e Bolsista de laboratório.
- **Cenário de Uso:** O aluno está diante do balcão ou na bancada de montagem com seu celular ou notebook e precisa obter respostas rápidas:
  1. Saber se um componente específico está livre e em que quantidade.
  2. Onde o item fica guardado (laboratório/armário) para facilitar a localização.
  3. Tirar dúvidas sobre prazos e se determinado item pode ser levado para fora da bancada.
  4. Saber o horário de funcionamento do laboratório para planejar a devolução.
- **Dores Atuais:** Ter que esperar o técnico consultar o sistema desktop, enfrentar interfaces com listagens cheias de filtros complexos, ou lidar com dúvidas sobre regras que poderiam ser sanadas instantaneamente.

## 3. Requisito
Como **Aluno ou Bolsista de laboratório**,  
quero **consultar disponibilidade, quantidades, localização física, regras de empréstimo e horários do laboratório via chat interativo em linguagem natural**,  
para **agilizar meu atendimento no balcão e obter respostas diretas e precisas sem depender de navegação manual por tabelas**.

## 4. Regras de Negócio Associadas
- `RN-008`: Tolerância a erros ortográficos (RapidFuzz >= 75%) e **Desambiguação Proativa** para buscas genéricas (ex: *"jumper"*, *"arduino"*), listando opções e quantidades.
- `RN-009`: Consulta em tempo real ao banco de dados MySQL (`equipamento`, `categoria`), com respostas estritas, claras e sem prolixidade.
- `RN-010`: Resposta padronizada e objetiva em exceções:
  - Item esgotado ou em manutenção: `"Item indisponível no momento."`
  - Item não encontrado: `"Item não cadastrado no acervo."`
- `RN-011`: Parametrização desacoplada de prazos de empréstimo e horários do laboratório em arquivo de configuração (`lab_rules.json`).

---

## 5. Comportamento Esperado e Fluxos do Usuário

### 5.1. Abertura da Janela e Saudação Inicial
- O aluno clica no botão flutuante no canto inferior direito da tela.
- A interface abre de forma limpa e direta, exibindo uma saudação textual objetiva:  
  `"Olá! Sou o assistente do laboratório. Como posso ajudar com os equipamentos hoje?"`  
- O cursor posiciona-se no campo de digitação, permitindo ao aluno escrever livremente.

### 5.2. Fluxo Principal: Consulta de Item Específico
1. **Pergunta do Aluno:** *"Tem Arduino Mega disponível?"*
2. **Processamento:**
   - Classificador identifica intenção: `consultar_disponibilidade`.
   - Extrator RapidFuzz mapeia: `Arduino mega2560`.
   - Consulta MySQL verifica: 42 unidades com status `DISPONIVEL`.
3. **Resposta do Bot:**  
   `"Sim! Temos 42 unidades de 'Arduino mega2560' disponíveis no laboratório."`

### 5.3. Fluxo de Desambiguação Proativa (Termo Genérico)
1. **Pergunta do Aluno:** *"Tem jumper pra bancada?"*
2. **Processamento:** O termo *"jumper"* gera múltiplos matches no acervo (`jumper femea x femea`, `jumper macho x macho`, `jumper macho x femea`).
3. **Resposta do Bot:**  
   `"Temos as seguintes opções de jumper disponíveis:"`  
   - `jumper femea x femea: 950 unidades disponíveis`  
   - `jumper macho x macho: 165 unidades disponíveis`  
   - `jumper macho x femea: 1 unidade disponível`  
   `"Qual dessas opções você precisa?"`

### 5.4. Fluxo de Regras e Horários
1. **Pergunta do Aluno:** *"Até que horas o laboratório fica aberto?"*
2. **Processamento:** Identifica intenção `horario_funcionamento` e lê parâmetros de `lab_rules.json`.
3. **Resposta do Bot:**  
   `"O laboratório funciona de Segunda a Sexta, das 08h às 18h."`

4. **Pergunta do Aluno:** *"Posso levar o multímetro pra casa?"*
5. **Processamento:** Identifica intenção `regras_emprestimo` e lê regras de retirada externa de `lab_rules.json`.
6. **Resposta do Bot:**  
   `"Equipamentos de medição e bancada são para uso exclusivo no laboratório. Para empréstimo externo de projetos, é necessária autorização do orientador."`

### 5.5. Fluxos de Exceção (Respostas Simples e Objetivas)
- **Item Esgotado / Em Manutenção:**  
  *Aluno:* *"Tem Placa de fenolite livre?"*  
  *Bot:* `"Item indisponível no momento."`
- **Item Não Localizado:**  
  *Aluno:* *"Vocês têm ferro de solda de 100W?"*  
  *Bot:* `"Item não cadastrado no acervo."`

---

## 6. Matriz de Exemplos de Perguntas e Respostas

| Pergunta do Aluno | Intenção Prevista | Entidade Extraída | Resposta do Bot |
| :--- | :--- | :--- | :--- |
| *"Bom dia, tudo bem?"* | `saudacao` | — | *"Olá! Como posso ajudar com os equipamentos do laboratório?"* |
| *"Tem cabo mini usb?"* | `consultar_disponibilidade` | `Cabo Mini USB` | *"Sim! Temos 5 unidades de 'Cabo Mini USB' disponíveis."* |
| *"Onde fica guardada a Ponte H?"* | `consultar_localizacao` | `Ponte H L298N` | *"A 'Ponte H L298N' está localizada no Armário de Robótica (23 unidades disponíveis)."* |
| *"Tem arduino?"* | `consultar_disponibilidade` | Múltiplos | *"Temos: 1) Arduino mega2560 (42 unid.), 2) Arduino uno (6 unid.). Qual você deseja?"* |
| *"Tem item_inexistente?"* | `consultar_disponibilidade` | Não encontrado | *"Item não cadastrado no acervo."* |
| *"Qual o prazo para devolver componentes?"* | `regras_emprestimo` | — | Resposta baseada nas regras parametrizadas em `lab_rules.json`. |
| *"O que você faz?"* | `ajuda` | — | *"Posso consultar a disponibilidade, quantidade e localização de itens do laboratório, além de tirar dúvidas sobre regras e horários."* |
| *"Valeu, obrigado!"* | `despedida` | — | *"De nada! Bons estudos e boas montagens no laboratório."* |

---

## 7. Critérios de Aceitação
- [ ] A interface abre de forma minimalista, com saudação simples e foco no campo de texto livre.
- [ ] Acurácia superior a 90% na classificação de intenções de alunos no balcão.
- [ ] Respostas para termos genéricos (`jumper`, `arduino`) apresentam desambiguação proativa com listagem e contagens de cada variação.
- [ ] Respostas de exceção seguem estritamente o padrão objetivo: `"Item indisponível no momento."` ou `"Item não cadastrado no acervo."`.
- [ ] Prazos e horários são lidos dinamicamente de `lab_rules.json`, sem hardcode no código-fonte.
- [ ] Tempo de resposta ponta a ponta inferior a 300ms.

---

## 8. Impacto no Sistema
- **Módulos afetados:** Backend (pacote `backend/chat/`), Frontend (`ChatWidget.jsx`).
- **Entidades afetadas:** `equipamento`, `categoria`.
- **Interfaces afetadas:** Layout global em `frontend/src/App.jsx`.
- **Banco de dados:** Leitura indexada em `equipamento(nome, status, quantidade)`.

## 9. Situação Atual
O banco MySQL está ativo com 445 itens carregados e a modelagem conceitual do usuário está 100% alinhada.

## 10. Solução / Implementação
- **NLP:** Scikit-Learn TF-IDF + Regressão Logística treinado no startup.
- **Fuzzy:** RapidFuzz com `token_sort_ratio` e desambiguação multi-item.
- **Configuração:** `lab_rules.json` para parametrização institucional.
- **UI:** Componente React 19 nativo com Tailwind/CSS e `lucide-react`.

## 11. Rastreabilidade
- **Requisitos anteriores:** N/A (Novo módulo).
- **Regras de Negócio:** `RN-008`, `RN-009`, `RN-010`, `RN-011`.
- **ADR:** `ADR-002` (NLP Scikit-Learn + RapidFuzz).
- **Implementação:** `backend/chat/` e `frontend/src/components/chat/ChatWidget.jsx`.
- **Testes:** `backend/tests/test_chatbot_nlp.py`.

## 12. Observações
<!-- MANUAL:START -->
_Espaço preservado para anotações manuais e complementos do desenvolvedor._
<!-- MANUAL:END -->

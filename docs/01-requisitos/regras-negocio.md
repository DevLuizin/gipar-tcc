# Catálogo de Regras de Negócio — GIPAR

Este documento centraliza todas as Regras de Negócio (**RN-XXX**) do GIPAR, servindo como base formal para requisitos, implementações, testes e validações com usuários.

---

## Módulo: Gestão de Patrimônio e Itens

### RN-001 — Unicidade de Tombamento e Identificação
- Todo item de patrimônio cadastrado no sistema deve possuir um número de tombamento ou código identificador único.
- Não é permitida a duplicação de tombamento ativo no banco de dados.

### RN-002 — Estados e Ciclo de Vida do Item
- Um item de acervo/laboratório pode transitar apenas entre os seguintes status:
  - `DISPONIVEL`: item apto para uso imediato, empréstimo ou reserva.
  - `EMPRESTADO`: item em posse de um solicitante (professor, aluno, técnico).
  - `RESERVADO`: item vinculado a uma reserva futura confirmada.
  - `MANUTENCAO`: item indisponível para empréstimo/reserva por avaria ou calibração.
  - `BAIXADO`: item retirado definitivamente do acervo ativo.
- Itens com status `MANUTENCAO` ou `BAIXADO` nunca podem ser ofertados como disponíveis em consultas ou reservas.

### RN-003 — Localização Física Obrigatória
- Todo item deve estar associado a um laboratório, sala ou armário físico pré-definido, garantindo rastreabilidade do patrimônio.

---

## Módulo: Empréstimos e Reservas

### RN-004 — Limite de Prazo e Conflito de Agendamento
- Um item não pode ser emprestado simultaneamente a mais de um usuário.
- Uma reserva só pode ser confirmada se não houver sobreposição temporal de datas/horários com outro empréstimo ou reserva ativa para o mesmo item.

### RN-005 — Bloqueio por Atraso na Devolução
- Usuários com devoluções em atraso ficam temporariamente suspensos de realizar novos empréstimos ou reservas até a regularização do item pendente.

---

## Módulo: Controle de Usuários e Perfis

### RN-006 — Níveis de Acesso e Permissões
- O sistema opera com perfis de acesso distintos:
  - `ADMINISTRADOR`: acesso irrestrito a configurações, cadastro de usuários, exclusão de itens e relatórios gerenciais.
  - `TECNICO`: gestão de itens, aprovação/baixa de empréstimos e manutenções.
  - `COMUM (Professor/Aluno)`: consulta ao acervo, solicitação de empréstimo/reserva e uso do Chatbot.

### RN-007 — Persistência de Notificações
- Notificações de sistema marcadas como lidas pelo usuário devem permanecer com status `lida` mesmo após encerramento e reinício de sessão (logout/login).
- A implementação desta regra será planejada em requisito próprio e não integra o escopo do `REQ-003`.

---

## Módulo: Chatbot Inteligente de Atendimento

### RN-008 — Tolerância a Erros e Desambiguação de Termos Genéricos
- O Chatbot deve identificar itens do acervo mesmo na presença de variações ortográficas, ausência de acentos ou erros de digitação leves, utilizando índice de similaridade de Levenshtein (RapidFuzz) com limiar mínimo de 75%.
- **Desambiguação Proativa:** Quando o usuário fizer uma busca por termo genérico (ex: *"jumper"*, *"arduino"*, *"cabo"*), o bot deve verificar todos os itens correspondentes no acervo, listar as variações encontradas com suas respectivas quantidades disponíveis e perguntar qual modelo específico o aluno deseja.

### RN-009 — Resposta Estrita e Objetiva Baseada no Estado Atual do Banco
- O Chatbot deve sempre consultar o estado do banco de dados MySQL em tempo real ao responder sobre disponibilidade, local ou quantidade de determinado item.
- As respostas devem ser concisas e diretas, informando com clareza a quantidade livre e o local físico do item, sem prolixidade ou especulações.

### RN-010 — Resposta Padronizada para Indisponibilidade e Itens Ausentes
- **Item Esgotado ou em Manutenção:** Quando o item pertencer ao catálogo, mas possuir quantidade disponível igual a zero (ou todos estiverem com status diferente de `DISPONIVEL`), o bot deve responder objetivamente:  
  `"Item indisponível no momento."`
- **Item Não Localizado:** Quando a similaridade calculada for inferior a 75% e nenhum item correspondente for encontrado no banco de dados, o bot deve responder de forma direta:  
  `"Item não cadastrado no acervo."`

### RN-011 — Parametrização Externa de Regras e Horários de Funcionamento
- Regras de prazo de empréstimo, permissões para retirada externa e horários de funcionamento do laboratório devem ser carregadas a partir de um arquivo de configuração/regras desacoplado do código-fonte (ex: `lab_rules.json`), permitindo sua edição direta pela coordenação do laboratório sem necessidade de alteração de código ou recompilação.

---

## Módulo: Interface de Usuário e Listagens

### RN-012 — Paginação, Ordenação e Busca Global em Listagens Tabulares
- As listagens abrangidas pelo `REQ-004` devem oferecer busca textual insensível a maiúsculas/minúsculas e acentuação gráfica.
- A busca e os filtros de domínio permanecem sob responsabilidade das páginas e devem ser aplicados antes do envio dos dados ao componente tabular.
- A listagem deve permitir ordenação bidirecional (ascendente e descendente) nas colunas configuradas.
- A paginação deve disponibilizar 10, 25, 50 e 100 itens por página.
- A aplicação de busca ou filtro e a alteração da quantidade de itens por página devem retornar a navegação à primeira página.
- Em telas pequenas, as colunas secundárias devem ser recolhidas sem impedir o acesso aos seus valores.

---

## Módulo: Usuários, Meu Perfil e Configurações

### RN-013 — Autoatendimento de Perfil e Troca de Senha com Reautenticação
- Todo usuário autenticado pode editar seu nome, nome de exibição, e-mail e avatar predefinido, sem alterar o próprio perfil de acesso ou status.
- O avatar deve ser selecionado de um catálogo fechado e versionado na aplicação; upload de fotografia e exibição de avatar na listagem administrativa não integram este requisito.
- A alteração de e-mail deve validar formato e unicidade, exigir a senha atual e informar que o e-mail é a credencial usada no login.
- A alteração de senha exige senha atual validada contra o hash `argon2`, nova senha com no mínimo 8 caracteres contendo letras e números e confirmação idêntica.
- Alterações de e-mail ou senha devem incrementar `token_version`, invalidar todos os JWTs anteriormente emitidos para o usuário, encerrar a sessão local e redirecionar para `/login`.

### RN-014 — Sistema de Temas e Acessibilidade Visual
- A aplicação deve preservar sem alteração visual o Padrão Institucional GIPAR e disponibilizar também Modo Escuro (Dark Mode), Azul Tecnológico (Ocean) e Alto Contraste.
- A seleção de tema deve alterar a interface em tempo real sem necessidade de recarregar a página.
- O MySQL é a fonte oficial da preferência de tema para permitir uso em diferentes dispositivos.
- O `localStorage` deve manter cache separado por usuário, usado somente para aplicação imediata durante a inicialização e posteriormente reconciliado com o valor do banco.
- A implementação deve usar tokens semânticos, mantendo o tema institucional como fallback, e só pode declarar conformidade WCAG após medição objetiva de contraste.

---

## Rastreabilidade das Regras de Negócio

| Regra | Módulo | Requisito Relacionado | ADR Relacionada | Status |
| :--- | :--- | :--- | :--- | :--- |
| `RN-001` | Patrimônio | `REQ-001`, Baseline Legada | `ADR-001` | 🟢 Validada |
| `RN-002` | Patrimônio | `REQ-001`, `REQ-004` | `ADR-001` | 🟢 Validada |
| `RN-003` | Patrimônio | `REQ-001`, `REQ-004` | — | 🟢 Validada |
| `RN-004` | Empréstimos | Baseline Legada | — | 🟢 Validada |
| `RN-005` | Empréstimos | Baseline Legada | — | 🟡 Em revisão |
| `RN-006` | Usuários | `REQ-003` | `ADR-001` | 🟢 Validada |
| `RN-007` | Notificações | Requisito futuro | — | 🟡 Planejada |
| `RN-008` | Chatbot | `REQ-001` | `ADR-002` | 🟢 Aprovada |
| `RN-009` | Chatbot | `REQ-001` | `ADR-002` | 🟢 Aprovada |
| `RN-010` | Chatbot | `REQ-001` | `ADR-002` | 🟢 Aprovada |
| `RN-011` | Chatbot | `REQ-001` | `ADR-002` | 🟢 Aprovada |
| `RN-012` | Listagens / UI | `REQ-004` | `ADR-005` | 🟢 Aprovada |
| `RN-013` | Perfil / Segurança | `REQ-003` | `ADR-006` | 🟢 Aprovada |
| `RN-014` | Temas / UI | `REQ-003` | `ADR-006` | 🟢 Aprovada |

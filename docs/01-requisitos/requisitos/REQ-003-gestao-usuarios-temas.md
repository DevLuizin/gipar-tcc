---
id: REQ-003
titulo: "Gestão Avançada de Usuários, Perfil e Temas do Sistema"
status: "🟡 Em análise"
tipo: "Melhoria / Correção"
modulo: "Usuários / Perfil"
origem: "Backlog de melhorias"
tags: [requisito, usuarios, autenticacao, perfil, temas, notificacoes, backend, frontend]
---

# REQ-003 — Gestão Avançada de Usuários, Perfil e Temas do Sistema

**Status:** 🟡 Em análise  
**Tipo:** Melhoria / Correção  
**Módulo:** Usuários / Perfil  
**Origem:** Backlog de melhorias  

## 1. Contexto
O GIPAR possui controle de autenticação básico com JWT. No entanto, o usuário não dispõe de uma tela dedicada de "Meu Perfil" para atualização de dados cadastrais e alteração de senha com validação de força. Além disso, as notificações apresentam um bug onde reaparecem como novas mesmo após serem marcadas como lidas, e a interface carece de personalização de temas visuais.

## 2. Problema / Necessidade
- Ausência de tela de autosserviço para o usuário atualizar sua senha e dados.
- Falha na persistência de leitura de notificações após novo login (`RN-007`).
- Necessidade de opções de temas visuais (ex: tema padrão institucional, modo escuro / dark mode e alto contraste).

## 3. Requisito
Como **usuário autenticado**,  
quero **acessar a tela de Meu Perfil para gerenciar meus dados, alterar minha senha, escolher o tema da interface e ter minhas notificações persistidas corretamente**,  
para **ter controle sobre minha conta, conforto visual e histórico confiável de avisos**.

## 4. Regra de Negócio
- `RN-006`: O perfil de acesso restringe quais abas e permissões o usuário visualiza no sistema.
- `RN-007`: Notificações marcadas como lidas devem persistir no banco e não voltar a gerar badges de novidade após novo login.
- A alteração de senha exige confirmação da senha anterior e respeito à política de segurança (mínimo de 8 caracteres com letras e números).

## 5. Comportamento Esperado

### Fluxo principal
1. Usuário clica no seu avatar/nome no cabeçalho e seleciona "Meu Perfil".
2. A tela exibe dados pessoais, histórico de empréstimos, aba de troca de senha e seletor de tema (Claro / Escuro / Alto Contraste).
3. Ao alternar o tema, a aplicação aplica imediatamente as variáveis CSS globais e salva a preferência no perfil/localStorage.
4. Notificações lidas são enviadas via endpoint `PUT /api/notificacoes/{id}/lida` e seu estado é persistido no MySQL.

### Exceções
- Senha atual informada incorretamente $\to$ O sistema bloqueia a alteração e exibe mensagem de erro.
- Nova senha em desacordo com as regras de complexidade $\to$ O formulário sinaliza os critérios pendentes.

## 6. Critérios de Aceitação
- [ ] Tela de "Meu Perfil" acessível para todos os perfis autenticados.
- [ ] Troca de senha funcional com hash seguro (bcrypt/argon2).
- [ ] No mínimo 2 a 4 temas visuais disponíveis (Claro Padrão, Dark Mode, etc.) com persistência.
- [ ] Notificação marcada como lida não deve reaparecer como não-lida ao deslogar e relogar.

## 7. Impacto no Sistema
- **Módulos afetados:** Backend (rotas `/api/usuarios/me`, `/api/usuarios/senha`, `/api/notificacoes`), Frontend (nova página `Perfil.jsx`, contexto de temas).
- **Entidades afetadas:** `Usuario`, `Notificacao`.
- **Interfaces afetadas:** Cabeçalho global, tela de perfil, central de notificações.
- **Banco de dados:** Coluna de `tema_preferido` ou tabela de preferências se necessário.

## 8. Situação Atual
A troca de senha e edição de perfil são restritas ou manuais, e as notificações não persistem adequadamente o status de leitura no banco.

## 9. Solução / Implementação
1. Criação do endpoint `PUT /api/usuarios/alterar-senha` com validação de hash da senha antiga.
2. Correção da query de atualização da tabela de notificações para gravar timestamp de leitura.
3. Criação do `ThemeContext` em React utilizando CSS Custom Properties (`--bg-primary`, `--text-primary`, etc.).

## 10. Rastreabilidade
- **Requisito anterior:** Baseline Legada.
- **Regras de negócio:** `RN-006`, `RN-007`.
- **ADR:** —
- **Implementação:** `backend/` e `frontend/src/pages/Perfil.jsx`.
- **Testes:** Teste unitário de troca de senha e teste E2E de persistência de notificação.

## 11. Observações
<!-- MANUAL:START -->
_Espaço preservado para anotações manuais e decisões pendentes._
<!-- MANUAL:END -->

---
id: REQ-003
titulo: "Gestão Avançada de Usuários, Meu Perfil e Sistema de Temas"
status: "🟢 Aprovado para Implementação"
tipo: "Melhoria / Usabilidade e Segurança"
modulo: "Usuários / Perfil e Configurações"
origem: "Backlog de melhorias e revisão técnica"
tags: [requisito, usuarios, autenticacao, perfil, configuracoes, temas, seguranca, backend, frontend]
---

# REQ-003 — Gestão Avançada de Usuários, Meu Perfil e Sistema de Temas

**Status:** 🟢 Aprovado para Implementação
**Tipo:** Melhoria / Usabilidade e Segurança
**Módulo:** Usuários / Perfil e Configurações
**Origem:** Backlog de melhorias e revisão técnica
**Documento de Planejamento:** [Plano de Implementação de Perfil e Configurações](../../plano-implementacao-perfil-configuracoes.md)
**Decisão Arquitetural:** [ADR-006 — Arquitetura de Temas e Gestão de Perfil](../../03-adrs/ADR-006-arquitetura-temas-e-gestao-perfil.md)

## 1. Contexto
O GIPAR possui no cabeçalho os itens "Meu Perfil" e "Configurações", mas ainda não dispõe das rotas correspondentes. O usuário autenticado também não possui autoatendimento para atualizar seus dados, escolher um avatar predefinido ou trocar sua senha. A interface utiliza o Padrão Institucional GIPAR e ainda não oferece temas alternativos persistidos entre dispositivos.

## 2. Problema / Necessidade
- Ausência das telas `/perfil` e `/configuracoes` integradas ao menu do usuário;
- Impossibilidade de o usuário atualizar nome, nome de exibição e e-mail;
- Ausência de troca de senha com validação da credencial atual e invalidação dos JWTs anteriores;
- Ausência de avatares predefinidos para personalização do cabeçalho e da tela de perfil;
- Ausência de temas alternativos para baixa luminosidade, preferência visual e maior contraste;
- Necessidade de preservar sem alterações visuais o Padrão Institucional GIPAR já existente.

## 3. Requisito
Como **usuário autenticado do GIPAR, independentemente do perfil de acesso**,
quero **gerenciar meus dados cadastrais, escolher um avatar predefinido, trocar minha senha e selecionar um tema visual**,
para **ter autonomia sobre minha conta e utilizar a interface de forma confortável em diferentes dispositivos**.

## 4. Regras de Negócio
- `RN-006`: O perfil de acesso (`ADMINISTRADOR`, `TECNICO` ou `COMUM`) é somente leitura no autoatendimento e deve ser exibido como identificação.
- `RN-013`: O usuário pode editar nome, nome de exibição, e-mail e avatar predefinido. A alteração de e-mail exige senha atual, formato válido e unicidade. A troca de senha exige senha atual, confirmação idêntica e no mínimo 8 caracteres contendo letras e números. Alterar e-mail ou senha invalida todos os JWTs anteriores e exige novo login.
- `RN-014`: O sistema oferece o Padrão Institucional GIPAR, preservado visualmente, e os temas Dark Mode, Ocean Blue e Alto Contraste. O MySQL é a fonte oficial da preferência, e o `localStorage` mantém cache separado por usuário para aplicação imediata.

## 5. Comportamento Esperado

### Fluxo 1: Meu Perfil (`/perfil`)
1. O usuário seleciona **Meu Perfil** no menu do cabeçalho;
2. A tela consulta `GET /api/usuarios/me` e exibe nome, nome de exibição, e-mail, perfil de acesso, avatar e data de cadastro;
3. O usuário pode selecionar um avatar de um catálogo fechado de imagens versionadas na aplicação;
4. O usuário pode atualizar nome e nome de exibição sem alterar suas permissões;
5. Se alterar o e-mail, deve informar a senha atual. A interface explica que o e-mail é a credencial de acesso e que será necessário entrar novamente;
6. Após alteração de e-mail bem-sucedida, os JWTs anteriores são invalidados, a sessão local é encerrada e o usuário é redirecionado para `/login`;
7. Na troca de senha, o usuário informa senha atual, nova senha e confirmação;
8. Após alteração de senha bem-sucedida, os JWTs anteriores são invalidados, a sessão local é encerrada e o usuário é redirecionado para `/login`.

### Fluxo 2: Configurações (`/configuracoes`)
1. O usuário seleciona **Configurações** no menu do cabeçalho;
2. A tela apresenta quatro opções: Padrão Institucional GIPAR, Dark Mode, Ocean Blue e Alto Contraste;
3. Selecionar um tema altera a interface sem recarregar a página;
4. A preferência é gravada no MySQL e armazenada localmente na chave específica do usuário;
5. Em outro dispositivo, após o login, o tema salvo no MySQL é recuperado e aplicado;
6. O Padrão Institucional GIPAR mantém a aparência atual do sistema e funciona como fallback.

### Exceções
- Senha atual incorreta na troca de senha ou alteração de e-mail → rejeitar a operação sem alterar dados;
- E-mail inválido ou já utilizado → rejeitar com mensagem específica;
- Nova senha fora da política → informar os critérios pendentes;
- Avatar ou tema fora do catálogo permitido → rejeitar a requisição;
- Falha ao persistir o tema → informar o erro e manter a preferência anteriormente confirmada pelo servidor;
- JWT com versão anterior à versão atual do usuário → responder `401 Unauthorized`.

## 6. Critérios de Aceitação
- [ ] Rotas `/perfil` e `/configuracoes` protegidas e acessíveis a todos os perfis autenticados.
- [ ] DTOs separados para resposta de perfil, atualização de perfil, alteração de senha e atualização de tema.
- [ ] Nome e nome de exibição atualizados sem permitir alteração de perfil de acesso ou status.
- [ ] Alteração de e-mail condicionada à senha atual, com validação de formato e unicidade.
- [ ] Catálogo de avatares predefinidos, sem upload de fotografias e sem coluna de avatar na listagem administrativa.
- [ ] Nova senha com pelo menos 8 caracteres, contendo letras e números, além de confirmação idêntica.
- [ ] Alteração de e-mail ou senha incrementa `token_version`, invalida JWTs anteriores e exige novo login.
- [ ] Padrão Institucional GIPAR preservado visualmente.
- [ ] Dark Mode, Ocean Blue e Alto Contraste implementados na mesma entrega.
- [ ] Preferência de tema persistida no MySQL e em cache local por usuário.
- [ ] Contraste dos quatro temas medido antes de declarar conformidade com WCAG.
- [ ] Interface responsiva em dispositivos móveis e desktop.

## 7. Impacto no Sistema
- **Banco de dados:** colunas `nome_exibicao`, `avatar`, `tema` e `token_version` na tabela `usuario`; atualização do `init.sql` e migration versionada para bancos existentes.
- **Backend:** DTOs Pydantic específicos; consulta do perfil autenticado; atualização de perfil; troca de senha; atualização de tema; validação de `token_version` na autenticação.
- **Frontend:** páginas `/perfil` e `/configuracoes`; catálogo local de avatares; atualização do contexto de autenticação; `ThemeContext`; tokens semânticos de estilo; integração com menu, cabeçalho e rotas permitidas.
- **Fora do escopo:** upload de fotografias, foto/avatar na listagem de usuários e preferências ou persistência de notificações.

## 8. Situação Atual
Os itens do menu exibem alertas temporários. O avatar mostra somente a inicial do nome, a sessão não oferece atualização do usuário e a interface utiliza cores fixas sem motor de temas. JWTs são validados apenas por assinatura e expiração, sem revogação por usuário.

## 9. Solução / Implementação
1. Atualizar o DDL de instalações novas e criar migration SQL versionada para volumes existentes;
2. Criar DTOs exclusivos para cada contrato de perfil;
3. Incluir `token_version` nos JWTs e comparar sua versão com o usuário ativo no banco;
4. Implementar os endpoints internos `/usuarios/me`, `/usuarios/me/senha` e `/usuarios/me/tema`, expostos externamente pelo proxy em `/api/usuarios/...`;
5. Implementar as páginas de perfil e configurações e integrá-las às rotas permitidas de todos os perfis;
6. Introduzir tokens semânticos preservando o visual institucional atual e, em seguida, implementar os três temas alternativos;
7. Validar os fluxos, a responsividade, a invalidação dos tokens e o contraste dos temas.

## 10. Rastreabilidade
- **Requisito anterior:** Baseline Legada.
- **Regras de negócio:** `RN-006`, `RN-013`, `RN-014`.
- **ADR:** [ADR-006 — Arquitetura de Temas e Gestão de Perfil](../../03-adrs/ADR-006-arquitetura-temas-e-gestao-perfil.md).
- **Plano de Implementação:** [docs/plano-implementacao-perfil-configuracoes.md](../../plano-implementacao-perfil-configuracoes.md).
- **Testes previstos:** contratos da API, autorização, atualização de sessão, política de senha, invalidação de JWT, catálogo de avatares, persistência multidispositivo do tema e validação visual.

## 11. Observações
<!-- MANUAL:START -->
_Espaço preservado para anotações manuais e decisões pendentes._
<!-- MANUAL:END -->

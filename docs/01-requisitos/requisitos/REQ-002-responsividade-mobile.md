---
id: REQ-002
titulo: "Responsividade Mobile da Interface Web"
status: "🟡 Em análise"
tipo: "Melhoria / UX"
modulo: "Frontend"
origem: "Diagnóstico de usabilidade"
tags: [requisito, frontend, css, responsividade, mobile, react]
---

# REQ-002 — Responsividade Mobile da Interface Web

**Status:** 🟡 Em análise  
**Tipo:** Melhoria / UX  
**Módulo:** Frontend  
**Origem:** Diagnóstico de usabilidade  

## 1. Contexto
A aplicação GIPAR foi desenvolvida inicialmente com foco em visualização desktop em telas de alta resolução. As tabelas de listagem, painéis de navegação e formulários de cadastro possuem larguras fixas ou comportamentos que quebram o layout em telas de smartphones e tablets.

## 2. Problema / Necessidade
Técnicos de laboratório e professores frequentemente utilizam celulares ou tablets nas bancadas dos laboratórios para consultar patrimônios, checar empréstimos e registrar movimentações no local. A ausência de responsividade prejudica gravemente a usabilidade em campo.

## 3. Requisito
Como **usuário em dispositivo móvel (celular ou tablet)**,  
quero **navegar pelas telas, tabelas e formulários do sistema de forma fluida e adaptada à tela**,  
para **gerenciar e consultar itens de laboratório diretamente do celular sem rolagem horizontal excessiva**.

## 4. Regra de Negócio
- A interface deve se adaptar fluidamente a viewports a partir de 360px de largura.
- Ações críticas (botões de login, busca, confirmação de empréstimo) devem respeitar áreas de toque adequadas (mínimo de 44x44px).

## 5. Comportamento Esperado

### Fluxo principal
1. Usuário acessa o GIPAR por um navegador mobile.
2. A barra lateral de navegação se converte em menu gaveta (drawer/hamburger).
3. As tabelas volumosas adotam rolagem horizontal contida ou layout em cartões (cards responsivos).
4. O modal do Chatbot se redimensiona para ocupar a tela inteira em modo mobile com fechamento facilitado.

### Exceções
- Em telas muito reduzidas (<360px), o layout deve priorizar informações essenciais (nome do item e status), ocultando colunas secundárias sob expansão.

## 6. Critérios de Aceitação
- [ ] Layout sem quebra visual ou overflow horizontal na janela principal entre 360px e 1920px.
- [ ] Menus e filtros acessíveis por toque sem sobreposição de componentes.
- [ ] Teste de usabilidade mobile aprovado nos navegadores Chrome Mobile e Safari iOS.

## 7. Impacto no Sistema
- **Módulos afetados:** Frontend React (`frontend/src/`).
- **Entidades afetadas:** Nenhuma (alteração restrita a estilos e componentes de apresentação).
- **Interfaces afetadas:** Todas as páginas (`pages/`) e componentes de tabela/menu (`components/`).
- **Banco de dados:** Sem alteração.

## 8. Situação Atual
A interface atual apresenta barras de rolagem desordenadas e elementos comprimidos quando o viewport é reduzido para dimensões de celular.

## 9. Solução / Implementação
1. Revisão do CSS com Media Queries em breakpoints padronizados (`sm: 640px`, `md: 768px`, `lg: 1024px`).
2. Implementação de componente `ResponsiveTable` que alterna entre tabela e cartões em telas móveis.
3. Componente de menu colapsável no cabeçalho.

## 10. Rastreabilidade
- **Requisito anterior:** Baseline Legada (melhoria identificada em diagnóstico).
- **Regras de negócio:** Diretrizes de Acessibilidade e Usabilidade.
- **ADR:** —
- **Implementação:** `frontend/src/`
- **Testes:** Validação visual em modo responsivo no Chrome DevTools.

## 11. Observações
<!-- MANUAL:START -->
_Espaço preservado para anotações manuais e decisões pendentes._
<!-- MANUAL:END -->

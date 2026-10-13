---
id: REQ-004
titulo: "Filtros de Pesquisa Dinâmicos e Paginação nas Listagens"
status: "🟡 Implementado — validação manual pendente"
tipo: "Melhoria / Usabilidade"
modulo: "Frontend / Listas"
origem: "Backlog de usabilidade"
tags: [requisito, frontend, react, tabulator, filtros, busca, paginacao]
---

# REQ-004 — Filtros de Pesquisa Dinâmicos e Paginação nas Listagens

**Status:** 🟡 Implementado — validação manual pendente

**Tipo:** Melhoria / Usabilidade

**Módulo:** Frontend / Listas

**Origem:** Backlog de usabilidade

**Documento de Planejamento:** [Plano de Implementação com Tabulator](../../plano-implementacao-datatable.md)

**Decisão Arquitetural:** [ADR-005 — Padronização de Listagens com Tabulator Client-Side](../../03-adrs/ADR-005-datatable-listagens-client-side.md)

## 1. Contexto

Com a importação de aproximadamente 445 itens de laboratório e o crescimento do volume de usuários e relatórios, as telas selecionadas precisam de busca rápida, ordenação, paginação configurável e comportamento adequado em telas pequenas.

## 2. Problema / Necessidade

As listagens atuais recebem todos os dados da API, aplicam filtros nas páginas e utilizam uma tabela sem paginação local. Isso dificulta a navegação por conjuntos maiores e exige rolagem extensa.

## 3. Requisito

Como **usuário do GIPAR**,
quero **pesquisar e filtrar os registros, ordenar as colunas e navegar por páginas com quantidade configurável**,
para **localizar informações sem recarregar a página e utilizar as listagens também em telas pequenas**.

## 4. Regras de Negócio

- A busca textual deve desconsiderar diferenças entre maiúsculas, minúsculas e acentuação (`RN-012`).
- A alteração da busca, dos filtros ou da quantidade de registros por página deve retornar a listagem à primeira página (`RN-012`).
- Os filtros de equipamentos devem respeitar os estados e regras de ciclo de vida (`RN-002`, `RN-003`).

## 5. Comportamento Esperado

### Fluxo principal

1. O usuário acessa uma das quatro telas incluídas no requisito.
2. A página mantém o componente `Pesquisa` para busca e filtros.
3. A página envia ao `TabulatorGipar` somente os registros correspondentes aos filtros atuais.
4. O usuário ordena uma coluna pelo cabeçalho.
5. O usuário escolhe 10, 25, 50 ou 100 registros por página e navega pelos controles do Tabulator.
6. Em telas pequenas, as colunas secundárias são recolhidas e podem ser consultadas nos detalhes da linha.

Na tela de relatórios, a busca textual será adicionada acima da pré-visualização e não alterará os filtros usados para gerar ou exportar o relatório.

### Exceções

- Quando não houver correspondências, a listagem deve apresentar um estado vazio sem erro de renderização.
- Valores ausentes não devem interromper a ordenação nem a apresentação das linhas.

## 6. Critérios de Aceitação

- [x] Dependência `tabulator-tables` adicionada diretamente ao frontend, sem wrapper React adicional.
- [x] Componente `TabulatorGipar` criado em `frontend/src/components/tabulatorGipar/`.
- [x] `TabelaGipar` preservada sem alterações para as telas fora do escopo.
- [x] Busca e filtros existentes preservados por meio de `Pesquisa`.
- [x] Busca textual sem distinção de caixa ou acentuação nas quatro telas.
- [x] Ordenação ascendente e descendente nas colunas configuradas.
- [x] Paginação local com opções de 10, 25, 50 e 100 registros.
- [x] Layout responsivo configurado com `responsiveLayout: "collapse"`.
- [x] Ações de edição, exclusão ou inativação preservadas onde já existem.
- [x] Busca textual simples adicionada à pré-visualização de relatórios.
- [x] Exportações de relatório em PDF e CSV preservadas no código.
- [ ] Validação manual concluída, além de `npm run lint` e `npm run build`.

## 7. Impacto no Sistema

- **Módulos afetados:** frontend React, novo componente `TabulatorGipar` e quatro páginas do escopo.
- **Telas afetadas:** equipamentos do administrador, usuários, equipamentos do estagiário e relatórios.
- **Dependências:** inclusão de `tabulator-tables` no frontend.
- **Backend e banco de dados:** sem alterações.

## 8. Situação Atual

As páginas utilizam `Pesquisa` e `TabelaGipar`. Os filtros são aplicados localmente, mas a tabela não oferece paginação própria. A pré-visualização de relatórios ainda não possui busca textual.

## 9. Solução / Implementação

1. adicionar a dependência oficial `tabulator-tables`;
2. criar `TabulatorGipar` com integração direta por `useRef` e `useEffect`;
3. configurar ordenação, paginação local e responsividade;
4. substituir somente a tabela nas quatro páginas incluídas;
5. manter `Pesquisa` e a lógica de filtros nas páginas;
6. acrescentar busca textual à pré-visualização de relatórios;
7. validar manualmente e executar lint e build.

Não fazem parte desta etapa: alterações no backend, migração das telas de empréstimos ou criação de infraestrutura de testes automatizados.

## 10. Rastreabilidade

- **Requisito anterior:** Baseline legada.
- **Regras de negócio:** `RN-002`, `RN-003`, `RN-012`.
- **ADR:** [ADR-005 — Padronização de Listagens com Tabulator Client-Side](../../03-adrs/ADR-005-datatable-listagens-client-side.md).
- **Plano de implementação:** [docs/plano-implementacao-datatable.md](../../plano-implementacao-datatable.md).
- **Implementação prevista:** `frontend/src/components/tabulatorGipar/TabulatorGipar.jsx` e quatro páginas do escopo.
- **Validação:** build concluído; lint direcionado concluído; lint geral e casos manuais pendentes.

## 11. Observações

<!-- MANUAL:START -->
_Espaço preservado para anotações manuais e decisões pendentes._
<!-- MANUAL:END -->

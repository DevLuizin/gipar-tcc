---
id: REQ-004
titulo: "Filtros de Pesquisa Dinâmicos e Paginação nas Listagens"
status: "🟡 Em análise"
tipo: "Melhoria / Usabilidade"
modulo: "Frontend / Listas"
origem: "Backlog de usabilidade"
tags: [requisito, frontend, react, tabelas, filtros, busca, paginacao]
---

# REQ-004 — Filtros de Pesquisa Dinâmicos e Paginação nas Listagens

**Status:** 🟡 Em análise  
**Tipo:** Melhoria / Usabilidade  
**Módulo:** Frontend / Listas  
**Origem:** Backlog de usabilidade  

## 1. Contexto
Com a importação dos 445 itens de laboratório e o crescimento do volume de empréstimos e usuários, as telas de listagem necessitam de recursos avançados de filtragem rápida, semelhantes aos recursos do antigo DataTables (busca textual instantânea por coluna, ordenação por cabeçalho e paginação configurável).

## 2. Problema / Necessidade
As listagens atuais carregam dados de forma estática ou com filtros restritos, dificultando a localização rápida de equipamentos por tombamento, categoria, laboratório ou status.

## 3. Requisito
Como **usuário do GIPAR (técnico ou administrador)**,  
quero **filtrar instantaneamente os registros por múltiplos campos (nome, tombamento, laboratório, status), ordenar colunas e navegar por páginas**,  
para **localizar qualquer item ou registro em menos de 3 segundos**.

## 4. Regra de Negócio
- A busca deve ser case-insensitive e desconsiderar acentuação gráfica.
- Filtros aplicados na listagem de itens devem respeitar o status dos itens (`RN-002`).

## 5. Comportamento Esperado

### Fluxo principal
1. Usuário digita um termo no campo de busca rápida da tabela de itens (ex: *"fonte"*).
2. A listagem filtra os registros em tempo real (client-side ou server-side via debounce de 300ms).
3. O usuário pode combinar a busca com dropdowns de Categoria e Laboratório.
4. O usuário clica na coluna "Data de Aquisição" para ordenar crescentemente ou decrescente.
5. A paginação ajusta o total de registros (10, 25, 50 ou 100 por página).

### Exceções
- Nenhum registro atende aos filtros $\to$ Exibir mensagem clara: *"Nenhum item encontrado para os filtros selecionados"* com botão de limpar filtros.

## 6. Critérios de Aceitação
- [ ] Campo de busca rápida com filtragem reativa instantânea.
- [ ] Dropdowns de filtro por status e categoria com opção de "Todos".
- [ ] Ordenação ascendente/descendente clicável nos cabeçalhos das colunas principais.
- [ ] Paginação funcional com controle de quantidade de itens visíveis por página.

## 7. Impacto no Sistema
- **Módulos afetados:** Frontend React (`components/common/DataTable.jsx`, páginas de listagem).
- **Entidades afetadas:** `Item`, `Usuario`, `Emprestimo`, `Reserva`.
- **Interfaces afetadas:** Telas de acervo, usuários e histórico.
- **Banco de dados:** Suporte a queries com parâmetros de `LIMIT`, `OFFSET` e `ORDER BY` caso a paginação seja feita no backend.

## 8. Situação Atual
Listagens básicas sem filtros combinados ou ordenação dinâmica de colunas.

## 9. Solução / Implementação
Desenvolver um componente reutilizável `DataTable.jsx` em React, inspirado no DataTables/TanStack Table, com:
- Campo de busca global com debounce;
- Filtros por facetas (status, laboratório);
- Ordenação e paginação controlada.

## 10. Rastreabilidade
- **Requisito anterior:** Baseline Legada.
- **Regras de negócio:** `RN-002`, `RN-003`.
- **ADR:** —
- **Implementação:** `frontend/src/components/common/DataTable.jsx`.
- **Testes:** Teste de renderização e filtro do componente React.

## 11. Observações
<!-- MANUAL:START -->
_Espaço preservado para anotações manuais e decisões pendentes._
<!-- MANUAL:END -->

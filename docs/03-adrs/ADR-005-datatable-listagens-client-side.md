# ADR-005: Padronização de Listagens com Tabulator Client-Side

**Status:** Aprovada
**Data:** 2026-10-12
**Decisores:** Luiz 
**Requisitos Relacionados:** REQ-004

---

## 1. Contexto do Problema

Com a carga inicial de aproximadamente 445 itens de laboratório e o aumento no volume de usuários e relatórios, as telas de listagem do GIPAR precisam de paginação, ordenação e navegação responsiva semelhantes às oferecidas pelo plugin jQuery DataTables.

O frontend utiliza React 19 e não possui jQuery. Também já dispõe dos dados completos fornecidos pelos endpoints FastAPI e dos filtros de pesquisa implementados nas próprias páginas. A solução deve aproveitar essa estrutura, evitar alterações no backend e acrescentar o mínimo possível de código próprio.

## 2. Decisão Adotada

Adotar a biblioteca **`tabulator-tables` 6.x**, integrada diretamente ao React, para implementar o componente **`TabulatorGipar`**.

O componente será responsável somente por:

1. renderizar os dados recebidos por propriedades;
2. ordenar as colunas configuradas;
3. paginar no navegador com opções de 10, 25, 50 e 100 registros;
4. apresentar o resumo e os controles de navegação fornecidos pelo Tabulator;
5. adaptar as colunas em telas pequenas com `responsiveLayout: "collapse"`;
6. preservar as ações de edição e exclusão por callbacks.

A busca textual e os filtros de domínio continuarão sob responsabilidade do componente `Pesquisa` e das páginas existentes. Em `Relatorios.jsx`, será adicionada uma instância de `Pesquisa` configurada apenas para busca textual sobre a pré-visualização.

A integração será feita diretamente com `tabulator-tables`, utilizando `useRef` e `useEffect`, sem wrapper React de terceiros. A instância deverá ser destruída no retorno do efeito para evitar vazamento de recursos.

O escopo fica limitado a:

- `frontend/src/pages/adm/equipamentos.jsx`;
- `frontend/src/pages/adm/Usuarios.jsx`;
- `frontend/src/pages/estagiario/equipamentos.jsx`;
- `frontend/src/pages/adm/Relatorios.jsx`.

A atual `TabelaGipar` permanecerá sem alterações e continuará sendo usada em `estagiario/emprestimos.jsx` e `adm/components/DashboardEmprestimos.jsx`.

## 3. Alternativas Consideradas

### Alternativa A: Paginação Server-Side no FastAPI e MySQL

- **Vantagens:** adequada para conjuntos de dados muito grandes e reduz o volume mantido no navegador.
- **Desvantagens:** exigiria alterar endpoints, consultas SQL, serviços do frontend e contratos existentes.
- **Motivo do descarte:** o volume atual pode ser processado no cliente e a alternativa aumentaria o escopo sem necessidade comprovada.

### Alternativa B: Componente Proprietário com Hook de DataTable

- **Vantagens:** controle integral sobre comportamento e interface.
- **Desvantagens:** exigiria implementar e manter manualmente paginação, ordenação, responsividade e seus casos de borda.
- **Motivo do descarte:** o Tabulator já fornece os recursos necessários e reduz a quantidade de código próprio.

### Alternativa C: Wrapper React para Tabulator

- **Vantagens:** interface declarativa pronta para uso em React.
- **Desvantagens:** acrescenta uma dependência intermediária e condiciona a compatibilidade entre React e Tabulator ao ciclo de manutenção do wrapper.
- **Motivo do descarte:** a integração direta é pequena e evita uma camada adicional.

### Alternativa D: Substituir a Implementação da `TabelaGipar`

- **Vantagens:** manteria um único nome de componente no projeto.
- **Desvantagens:** afetaria também as telas de empréstimos, que possuem clique em linha e ordenação controlada fora do escopo do REQ-004.
- **Motivo do descarte:** criar `TabulatorGipar` preserva o comportamento atual e reduz o risco da mudança.

## 4. Consequências e Impactos

### Consequências Positivas

- nenhuma alteração no backend ou no banco de dados;
- menor quantidade de lógica própria de tabela;
- manutenção dos filtros e fluxos já existentes nas páginas;
- paginação, ordenação e responsividade centralizadas;
- migração restrita às quatro telas aprovadas.

### Consequências Negativas e Trade-Offs

- inclusão de `tabulator-tables` nas dependências do frontend;
- convivência temporária entre `TabelaGipar` e `TabulatorGipar`;
- necessidade de adaptar formatadores visuais e callbacks ao contrato do Tabulator;
- eventual migração para paginação no servidor caso o volume de dados cresça significativamente.

## 5. Rastreabilidade e Conformidade

- **Requisito:** REQ-004 — Filtros de Pesquisa Dinâmicos e Paginação nas Listagens.
- **Regras de negócio:** RN-002, RN-003 e RN-012.
- **Implementação prevista:**
  - `frontend/src/components/tabulatorGipar/TabulatorGipar.jsx`;
  - `frontend/src/utils/normalizarTexto.js`;
  - quatro páginas definidas no escopo;
  - `frontend/package.json` e `frontend/package-lock.json`.
- **Validação prevista:** casos manuais documentados, `npm run lint` e `npm run build`.
- **Fora do escopo:** backend, banco de dados, telas de empréstimos e testes automatizados de frontend nesta etapa.

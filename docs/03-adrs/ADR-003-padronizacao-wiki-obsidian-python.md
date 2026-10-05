# ADR-003: Padronização da Wiki Determinística no Obsidian com Gerador em Python

**Status:** Aprovada  
**Data:** 2026-10-04  
**Decisores:** Equipe de Desenvolvimento GIPAR  
**Requisitos Relacionados:** Governança de Requisitos e Rastreabilidade  

---

## 1. Contexto do Problema
O desenvolvimento do GIPAR exige documentação técnica de alta precisão que mantenha rastreabilidade entre requisitos, regras de negócio, diagramas UML e código-fonte, servindo simultaneamente como base de conhecimento para o desenvolvedor e como índice para agentes de IA (Antigravity). No projeto PEISMED anterior, foi desenvolvido um gerador em Node.js (`generate-wiki.js`). Para o GIPAR, cujo backend é construído em Python (FastAPI), precisávamos definir a tecnologia e o modelo de governança da documentação sincronizada no Obsidian.

## 2. Decisão Adotada
1. Desenvolver um script determinístico nativo em Python (`docs/scripts/generate_wiki.py`), preservando a arquitetura comprovada do gerador do PEISMED:
   - Extração determinística de rotas FastAPI, modelos Pydantic, componentes React e tabelas MySQL;
   - Geração de notas em Markdown com frontmatter YAML padronizado;
   - Renderização de diagramas nativos em **Mermaid.js** (C4, DER e Sequência);
   - Preservação estrita de seções manuais do usuário delimitadas por `<!-- MANUAL:START -->` e `<!-- MANUAL:END -->`;
   - Manifesto `.wiki-manifest.json` com hashes SHA-256 e commit Git para detecção de arquivos modificados e remoção segura de órfãos (`--clean`);
   - Suporte a flags CLI: `--dry-run`, `--clean`, `--scope [full|backend|frontend]`.
2. Registrar o checkpoint de documentação de forma dupla:
   - Em constante no próprio script `generate_wiki.py`;
   - No callout de destaque da página inicial do cofre (`00 - Inicio/Pagina Inicial.md`).
3. Conectar o cofre do Obsidian ao Antigravity através do MCP server `obsidian`, permitindo consultas de baixo consumo de tokens via `obsidian-document-locator`.

## 3. Alternativas Consideradas
### Alternativa A: Manter o Script em Node.js (generate-wiki.js)
- **Vantagens:** Reutilização direta do código legado.
- **Desvantagens:** Exigiria ambiente Node.js no backend Python para parsing de AST e geraria dependências adicionais fora do ecossistema principal.
- **Motivo do descarte:** A equipe definiu em alinhamento que um script nativo em Python integra-se perfeitamente com a stack do backend FastAPI.

### Alternativa B: Edição 100% manual no Obsidian sem script gerador
- **Vantagens:** Não exige script.
- **Desvantagens:** Perda rápida de sincronia entre o código real e a documentação, erros de digitação e impossibilidade de manter um grafo de código atualizado a cada commit.
- **Motivo do descarte:** A automação determinística é essencial para sustentar a rastreabilidade contínua.

## 4. Consequências e Impactos
### Consequências Positivas
- Documentação técnica e funcional sempre consistente com o estado real do código.
- Notas manuais do desenvolvedor são 100% preservadas entre re-execuções.
- Agentes de IA consultam o cofre via MCP de forma precisa e rápida.

### Consequências Negativas / Trade-offs
- O script `generate_wiki.py` deve ser executado sempre que novas rotas, tabelas ou componentes forem criados.

## 5. Rastreabilidade e Conformidade
- **Implementação:** `docs/scripts/generate_wiki.py`, `AGENTS.md`.
- **Cofre Destino:** Configurado no MCP `@bitbonsai/mcpvault` apontando para o cofre GIPAR.

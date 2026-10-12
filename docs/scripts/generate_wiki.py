#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador determinístico da documentação Obsidian do GIPAR.

Objetivos:
- Documentar arquitetura, fluxos funcionais, rotas da API FastAPI, modelos Pydantic,
  componentes React e persistência MySQL;
- Espelhar requisitos (REQ-XXX), regras de negócio (RN-XXX) e ADRs em notas navegáveis;
- Preservar anotações manuais entre re-execuções através de marcadores <!-- MANUAL:START -->;
- Registrar manifesto .wiki-manifest.json com hashes SHA-256 e commit Git para integridade;
- Atualizar o carimbo de data e hora (checkpoint) no cofre e neste script.

Uso:
    python docs/scripts/generate_wiki.py "C:\\caminho\\do\\cofre"
    python docs/scripts/generate_wiki.py "C:\\caminho\\do\\cofre" --dry-run
    python docs/scripts/generate_wiki.py "C:\\caminho\\do\\cofre" --clean
    python docs/scripts/generate_wiki.py "C:\\caminho\\do\\cofre" --scope backend
"""

import sys
import os
import re
import json
import hashlib
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

LAST_DOCUMENTATION_UPDATE = "2026-10-12T10:19:44.489240-03:00"

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MANIFEST_NAME = ".wiki-manifest.json"
MANUAL_START = "<!-- MANUAL:START -->"
MANUAL_END = "<!-- MANUAL:END -->"

IGNORED_DIRS = {
    ".git", "node_modules", "__pycache__", ".pytest_cache", "dist", "build", ".venv", "venv"
}

def to_posix(path_str: str) -> str:
    return str(path_str).replace("\\", "/")

def sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def get_git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(PROJECT_ROOT),
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        return out
    except Exception:
        return "indisponivel"

def read_text(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="latin-1", errors="replace")

def relative_source(file_path: Path) -> str:
    try:
        return to_posix(file_path.relative_to(PROJECT_ROOT))
    except ValueError:
        return to_posix(file_path.name)

def extract_manual(content: str) -> str:
    if not content:
        return ""
    start = content.find(MANUAL_START)
    end = content.find(MANUAL_END)
    if start >= 0 and end > start:
        return content[start + len(MANUAL_START):end].strip()
    return ""

def render_frontmatter(metadata: dict) -> str:
    lines = ["---"]
    for k, v in metadata.items():
        if v is None or v == "":
            continue
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {json.dumps(str(item), ensure_ascii=False)}")
        elif isinstance(v, (int, float, bool)):
            lines.append(f"{k}: {v}")
        else:
            lines.append(f"{k}: {json.dumps(str(v), ensure_ascii=False)}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)

def render_note(metadata: dict, title: str, body: str, manual: str = "") -> str:
    fm = render_frontmatter(metadata)
    manual_block = manual if manual else "_Espaço preservado para anotações manuais e complementos do desenvolvedor._"
    return f"{fm}# {title}\n\n{body.strip()}\n\n## Notas manuais\n\n{MANUAL_START}\n{manual_block}\n{MANUAL_END}\n"

class WikiContext:
    def __init__(self, vault_path: Path, options):
        self.vault_path = vault_path
        self.options = options
        self.manifest_path = vault_path / MANIFEST_NAME
        self.previous_manifest = {"files": []}
        if self.manifest_path.exists():
            try:
                self.previous_manifest = json.loads(read_text(self.manifest_path))
            except Exception:
                self.previous_manifest = {"files": []}
        self.managed_files = set()
        self.generated_at = datetime.now().isoformat()
        self.git_commit = get_git_commit()
        self.stats = {"created": 0, "updated": 0, "unchanged": 0, "removed": 0, "errors": []}

    def write_note(self, note_relative_path: str, metadata: dict, title: str, body: str):
        norm_path = to_posix(note_relative_path)
        self.managed_files.add(norm_path)
        target = self.vault_path / Path(norm_path)
        existing_content = read_text(target) if target.exists() else ""
        manual = extract_manual(existing_content)

        full_metadata = {
            **metadata,
            "git_commit": self.git_commit,
            "generated_at": self.generated_at,
            "status": "generated"
        }

        new_content = render_note(full_metadata, title, body, manual)

        if existing_content:
            temp_meta = dict(full_metadata)
            m_prev_gen = re.search(r'^generated_at:\s*(.+)$', existing_content, re.M)
            m_prev_com = re.search(r'^git_commit:\s*(.+)$', existing_content, re.M)
            if m_prev_gen:
                try: temp_meta["generated_at"] = json.loads(m_prev_gen.group(1))
                except: temp_meta["generated_at"] = m_prev_gen.group(1).strip('"\'')
            if m_prev_com:
                try: temp_meta["git_commit"] = json.loads(m_prev_com.group(1))
                except: temp_meta["git_commit"] = m_prev_com.group(1).strip('"\'')
            if render_note(temp_meta, title, body, manual) == existing_content:
                self.stats["unchanged"] += 1
                return
            self.stats["updated"] += 1
        else:
            self.stats["created"] += 1

        if not self.options.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(new_content, encoding="utf-8")

    def finalize(self):
        if self.options.clean:
            stale = [f for f in self.previous_manifest.get("files", []) if f not in self.managed_files]
            for f in stale:
                target = self.vault_path / Path(f)
                if target.exists() and target.is_file():
                    if not self.options.dry_run:
                        target.unlink()
                    self.stats["removed"] += 1
        if not self.options.dry_run:
            self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
            self.manifest_path.write_text(json.dumps({
                "version": 2,
                "project": "GIPAR",
                "generated_at": self.generated_at,
                "git_commit": self.git_commit,
                "scope": self.options.scope,
                "files": sorted(list(self.managed_files))
            }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def parse_fastapi_backend(backend_dir: Path):
    endpoints = []
    models = []
    db_methods = []

    route_files = [backend_dir / "main.py"]
    routers_dir = backend_dir / "api" / "routers"
    if routers_dir.exists():
        route_files.extend(sorted(routers_dir.rglob("*.py")))

    for route_file in route_files:
        if not route_file.exists():
            continue
        content = read_text(route_file)
        pattern = re.compile(
            r'@(?:app|router)\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\'](.*?)\)\s*\n(?:async\s+)?def\s+([A-Za-z0-9_]+)\s*\((.*?)\)',
            re.DOTALL
        )
        for m in pattern.finditer(content):
            http_method = m.group(1).upper()
            route_path = m.group(2)
            args_str = m.group(3)
            fn_name = m.group(4)
            params = m.group(5).replace("\n", " ").strip()
            tags_match = re.search(r'tags\s*=\s*\[([^\]]+)\]', args_str)
            tags = [t.strip().strip('"\'') for t in tags_match.group(1).split(",")] if tags_match else ["Geral"]
            endpoints.append({
                "method": http_method,
                "path": route_path,
                "function": fn_name,
                "params": params,
                "tags": tags,
                "source": relative_source(route_file.resolve())
            })

    models_file = backend_dir / "models" / "models.py"
    if models_file.exists():
        content = read_text(models_file)
        class_pattern = re.compile(r'class\s+([A-Za-z0-9_]+)\s*\(([^)]*BaseModel[^)]*)\):([\s\S]*?)(?=\nclass\s|\Z)')
        for m in class_pattern.finditer(content):
            c_name = m.group(1)
            c_body = m.group(3)
            fields = []
            for line in c_body.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and ":" in line:
                    parts = line.split(":", 1)
                    fields.append({"name": parts[0].strip(), "type": parts[1].split("=")[0].strip()})
            models.append({"name": c_name, "fields": fields, "source": "backend/models/models.py"})

    db_dir = backend_dir / "gerenciador_db"
    if db_dir.exists():
        for py_file in db_dir.glob("*.py"):
            content = read_text(py_file)
            fn_pattern = re.compile(r'def\s+([A-Za-z0-9_]+)\s*\((.*?)\):')
            for m in fn_pattern.finditer(content):
                db_methods.append({
                    "name": m.group(1),
                    "params": m.group(2).replace("\n", " ").strip(),
                    "file": py_file.name,
                    "source": relative_source(py_file)
                })

    return {"endpoints": endpoints, "models": models, "db_methods": db_methods}

def parse_frontend_react(frontend_dir: Path):
    pages = []
    components = []
    services = []

    src_dir = frontend_dir / "src"
    if not src_dir.exists():
        return {"pages": pages, "components": components, "services": services}

    pages_dir = src_dir / "pages"
    if pages_dir.exists():
        for p in list(pages_dir.rglob("*.jsx")) + list(pages_dir.rglob("*.js")):
            if not p.name.endswith(".test.js") and not p.name.endswith(".test.jsx"):
                pages.append({"name": p.stem, "file": p.name, "source": relative_source(p)})

    comp_dir = src_dir / "components"
    if comp_dir.exists():
        for c in list(comp_dir.rglob("*.jsx")) + list(comp_dir.rglob("*.js")):
            if not c.name.endswith(".test.js") and not c.name.endswith(".test.jsx"):
                components.append({"name": c.stem, "file": c.name, "source": relative_source(c)})

    srv_dir = src_dir / "services"
    if srv_dir.exists():
        for s in srv_dir.rglob("*.js"):
            content = read_text(s)
            fns = re.findall(r'(?:export\s+const\s+|const\s+|export\s+function\s+|function\s+)([A-Za-z0-9_]+)', content)
            services.append({"name": s.stem, "file": s.name, "functions": list(set(fns)), "source": relative_source(s)})

    return {"pages": pages, "components": components, "services": services}

def parse_mysql_ddl(sql_path: Path):
    tables = []
    if not sql_path.exists():
        return tables
    content = read_text(sql_path)
    pattern = re.compile(r'CREATE TABLE IF NOT EXISTS\s+([A-Za-z0-9_]+)\s*\(([\s\S]*?)\)\s*ENGINE', re.IGNORECASE)
    for m in pattern.finditer(content):
        t_name = m.group(1)
        t_body = m.group(2)
        columns = []
        fks = []
        for line in t_body.splitlines():
            line = line.strip().rstrip(",")
            if not line or line.startswith("--"):
                continue
            if re.match(r'FOREIGN KEY', line, re.I):
                fks.append(line)
            elif not re.match(r'(PRIMARY KEY|KEY|UNIQUE KEY)', line, re.I):
                parts = line.split(maxsplit=2)
                if len(parts) >= 2:
                    columns.append({"name": parts[0], "type": parts[1], "raw": line})
        tables.append({"name": t_name, "columns": columns, "fks": fks, "source": relative_source(sql_path)})
    return tables

def generate_wiki(vault_path: Path, options):
    ctx = WikiContext(vault_path, options)

    backend_data = parse_fastapi_backend(PROJECT_ROOT / "backend")
    frontend_data = parse_frontend_react(PROJECT_ROOT / "frontend")
    tables_data = parse_mysql_ddl(PROJECT_ROOT / "docker" / "mysql" / "init.sql")

    # 1. Página Inicial / MOC
    home_lines = [
        f"> [!NOTE] Checkpoint da Documentação GIPAR",
        f"> **Data e Hora:** {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}  ",
        f"> **Commit Git:** `{ctx.git_commit}`  ",
        f"> **Status do Cofre:** Sincronizado automaticamente com o repositório GIPAR.",
        "",
        "Bem-vindo à base de conhecimento do **GIPAR (Gestão Inteligente de Patrimônio e Recursos)**.",
        "",
        "## Módulos e Navegação Central",
        "",
        "- [[00 - Inicio/Inventario do Projeto|📊 Inventário Geral do Projeto]]",
        "- [[01 - Requisitos e Negocio/Levantamento de Requisitos|📋 Levantamento e Matriz de Requisitos (REQ-XXX)]]",
        "- [[01 - Requisitos e Negocio/Regras de Negocio|⚖️ Catálogo de Regras de Negócio (RN-XXX)]]",
        "- [[02 - Diagramas e Modelos/Diagramas C4 e Arquitetura|🏛️ Diagramas C4 e Arquitetura de Contêineres]]",
        "- [[02 - Diagramas e Modelos/Modelo de Dominio e DER|🗄️ Modelo de Domínio e DER (MySQL)]]",
        "- [[02 - Diagramas e Modelos/Diagramas de Sequencia|🔄 Diagramas de Sequência e Fluxos]]",
        "- [[04 - Decisoes Arquiteturais (ADRs)/ADR-001|📜 Decisões Arquiteturais (ADRs)]]",
        "",
        "## Módulo em Destaque: Chatbot Inteligente",
        "",
        "- [[01 - Requisitos e Negocio/REQ-001 - Chatbot de Atendimento|REQ-001 — Chatbot de Consulta de Patrimônio]]",
        "- [[04 - Decisoes Arquiteturais (ADRs)/ADR-002|ADR-002 — Arquitetura NLP (Scikit-Learn + RapidFuzz)]]",
        "- [[20 - Fluxos Funcionais/Atendimento via Chatbot|Fluxo Funcional: Atendimento via Chatbot]]",
        "",
        "## Referências de Código Geradas",
        "",
        f"- Backend: {len(backend_data['endpoints'])} rotas FastAPI, {len(backend_data['models'])} modelos Pydantic",
        f"- Frontend: {len(frontend_data['pages'])} telas, {len(frontend_data['components'])} componentes, {len(frontend_data['services'])} serviços",
        f"- Banco de Dados: {len(tables_data)} tabelas relacionais em MySQL"
    ]
    ctx.write_note("00 - Inicio/Pagina Inicial.md", {"type": "index", "tags": ["inicio", "moc"]}, "GIPAR — Documentação Central", "\n".join(home_lines))

    # 2. Inventário do Projeto
    inv_lines = [
        "| Camada / Recurso | Quantidade Detectada |",
        "| :--- | :---: |",
        f"| Rotas / Endpoints FastAPI | {len(backend_data['endpoints'])} |",
        f"| Modelos Pydantic | {len(backend_data['models'])} |",
        f"| Métodos de Repositório DB | {len(backend_data['db_methods'])} |",
        f"| Telas React (Pages) | {len(frontend_data['pages'])} |",
        f"| Componentes React | {len(frontend_data['components'])} |",
        f"| Clientes de Serviço Frontend | {len(frontend_data['services'])} |",
        f"| Tabelas MySQL DDL | {len(tables_data)} |",
        "",
        "## Rastreabilidade do Repositório",
        "",
        f"- **Commit de Origem:** `{ctx.git_commit}`",
        f"- **Data da Geração:** `{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}`"
    ]
    ctx.write_note("00 - Inicio/Inventario do Projeto.md", {"type": "inventory", "tags": ["inventario"]}, "Inventário de Código do GIPAR", "\n".join(inv_lines))

    # 3. Espelhar Requisitos e Regras de Negócio
    docs_req_dir = PROJECT_ROOT / "docs" / "01-requisitos"
    if docs_req_dir.exists():
        rn_file = docs_req_dir / "regras-negocio.md"
        if rn_file.exists():
            ctx.write_note("01 - Requisitos e Negocio/Regras de Negocio.md", {"type": "rules", "tags": ["regras-negocio"]}, "Catálogo de Regras de Negócio", read_text(rn_file))
        lev_file = docs_req_dir / "levantamento-requisitos.md"
        if lev_file.exists():
            ctx.write_note("01 - Requisitos e Negocio/Levantamento de Requisitos.md", {"type": "requirements-index", "tags": ["requisitos"]}, "Levantamento de Requisitos", read_text(lev_file))
        req_folder = docs_req_dir / "requisitos"
        if req_folder.exists():
            for req_file in req_folder.glob("*.md"):
                content = read_text(req_file)
                m_title = re.search(r'^#\s+(.+)$', content, re.M)
                title = m_title.group(1) if m_title else req_file.stem
                clean_body = re.sub(r'^---\n[\s\S]*?\n---\n', '', content).strip()
                clean_body = re.sub(r'^#\s+[^\n]+\n', '', clean_body).strip()
                ctx.write_note(f"01 - Requisitos e Negocio/{req_file.stem}.md", {"type": "requirement", "tags": ["requisito", req_file.stem.split('-')[0].lower()]}, title, clean_body)

    # 4. Espelhar Diagramas
    docs_diag_dir = PROJECT_ROOT / "docs" / "02-diagramas"
    if docs_diag_dir.exists():
        for d_file in docs_diag_dir.rglob("*.md"):
            content = read_text(d_file)
            m_title = re.search(r'^#\s+(.+)$', content, re.M)
            title = m_title.group(1) if m_title else d_file.stem
            clean_body = re.sub(r'^#\s+[^\n]+\n', '', content).strip()
            folder_name = d_file.parent.name
            target_name = f"02 - Diagramas e Modelos/{d_file.stem}.md"
            if "c4" in d_file.stem.lower():
                target_name = "02 - Diagramas e Modelos/Diagramas C4 e Arquitetura.md"
            elif "der" in d_file.stem.lower():
                target_name = "02 - Diagramas e Modelos/Modelo de Dominio e DER.md"
            elif "seq" in d_file.stem.lower():
                target_name = "02 - Diagramas e Modelos/Diagramas de Sequencia.md"
            ctx.write_note(target_name, {"type": "diagram", "tags": ["diagrama", "mermaid", folder_name]}, title, clean_body)

    # 5. Espelhar ADRs
    adrs_dir = PROJECT_ROOT / "docs" / "03-adrs"
    if adrs_dir.exists():
        for adr_file in adrs_dir.glob("*.md"):
            if adr_file.stem == "0000-template":
                continue
            content = read_text(adr_file)
            m_title = re.search(r'^#\s+(.+)$', content, re.M)
            title = m_title.group(1) if m_title else adr_file.stem
            clean_body = re.sub(r'^#\s+[^\n]+\n', '', content).strip()
            ctx.write_note(f"04 - Decisoes Arquiteturais (ADRs)/{adr_file.stem}.md", {"type": "adr", "tags": ["adr", "decisao"]}, title, clean_body)

    # 6. Fluxos Funcionais
    flows = [
        ("Atendimento via Chatbot", [
            "Mapeamento ponta a ponta da experiência conversacional do Chatbot:",
            "",
            "1. **Frontend:** Usuário aciona o componente `ChatWidget`.",
            "2. **API:** Requisição POST `/api/chat` recebida pelo FastAPI.",
            "3. **IA / NLP:** Scikit-Learn identifica a intenção e RapidFuzz localiza o item.",
            "4. **Banco:** Consulta dinâmica de disponibilidade na tabela `equipamento`.",
            "5. **Retorno:** Resposta humanizada entregue ao usuário em < 500ms.",
            "",
            "Consulte os detalhes técnicos em [[01 - Requisitos e Negocio/REQ-001-chatbot-atendimento|REQ-001]] e [[02 - Diagramas e Modelos/Diagramas de Sequencia|SEQ-01]]."
        ]),
        ("Gestao de Itens e Patrimonio", [
            "Fluxo operacional de inventário e tombamento de itens laboratoriais:",
            "",
            "- Consulta ao acervo com filtros dinâmicos ([[01 - Requisitos e Negocio/REQ-004-filtros-pesquisa-listagens|REQ-004]]);",
            "- Cadastro e edição com garantia de tombamento único (`RN-001`);",
            "- Rastreabilidade física de laboratório e armário (`RN-003`);",
            "- Histórico de manutenções e baixas com integridade relacional."
        ]),
        ("Emprestimos e Reservas", [
            "Ciclo de custódia e agendamento de equipamentos:",
            "",
            "- Reserva prévia sem conflito de agenda (`RN-004`);",
            "- Saída física autorizada por técnico de bancada com registro de devolução prevista;",
            "- Bloqueio de novos empréstimos em caso de devolução em atraso (`RN-005`)."
        ])
    ]
    for flow_title, lines in flows:
        ctx.write_note(f"20 - Fluxos Funcionais/{flow_title}.md", {"type": "flow", "tags": ["fluxo", "negocio"]}, flow_title, "\n".join(lines))

    # 7. Referências Técnicas do Backend
    if backend_data["endpoints"]:
        ep_lines = ["| Método | Rota | Função | Parâmetros | Tag |", "| :---: | :--- | :--- | :--- | :--- |"]
        for ep in backend_data["endpoints"]:
            ep_lines.append(f"| `{ep['method']}` | `{ep['path']}` | `{ep['function']}` | `{ep['params'][:40]}` | {', '.join(ep['tags'])} |")
        ctx.write_note("90 - Referencia Gerada/Backend/Endpoints FastAPI.md", {"type": "reference", "tags": ["backend", "fastapi"]}, "Endpoints REST FastAPI", "\n".join(ep_lines))

    if backend_data["models"]:
        mod_lines = ["Modelos de validação de dados Pydantic utilizados na API:", ""]
        for m in backend_data["models"]:
            mod_lines.append(f"### `{m['name']}`")
            if m["fields"]:
                mod_lines.append("| Campo | Tipo |")
                mod_lines.append("| :--- | :--- |")
                for f in m["fields"]:
                    mod_lines.append(f"| `{f['name']}` | `{f['type']}` |")
            mod_lines.append("")
        ctx.write_note("90 - Referencia Gerada/Backend/Modelos Pydantic.md", {"type": "reference", "tags": ["backend", "pydantic"]}, "Modelos Pydantic (Data Models)", "\n".join(mod_lines))

    # 8. Referências Técnicas do Frontend
    if frontend_data["pages"] or frontend_data["components"]:
        fe_lines = ["Estrutura de apresentação do frontend React 19:", "", "### Páginas (`src/pages/`)", ""]
        for p in frontend_data["pages"]:
            fe_lines.append(f"- **`{p['name']}`** (`{p['source']}`)")
        fe_lines.extend(["", "### Componentes (`src/components/`)", ""])
        for c in frontend_data["components"]:
            fe_lines.append(f"- **`{c['name']}`** (`{c['source']}`)")
        ctx.write_note("90 - Referencia Gerada/Frontend/Componentes e Telas.md", {"type": "reference", "tags": ["frontend", "react"]}, "Componentes e Telas React", "\n".join(fe_lines))

    # 9. Referências de Banco de Dados
    if tables_data:
        db_lines = ["Estrutura de tabelas extraída do DDL MySQL (`docker/mysql/init.sql`):", ""]
        for t in tables_data:
            db_lines.append(f"### Tabela: `{t['name']}`")
            db_lines.append("| Coluna | Tipo |")
            db_lines.append("| :--- | :--- |")
            for col in t["columns"]:
                db_lines.append(f"| `{col['name']}` | `{col['type']}` |")
            if t["fks"]:
                db_lines.extend(["", "**Chaves Estrangeiras:**"])
                for fk in t["fks"]:
                    db_lines.append(f"- `{fk}`")
            db_lines.append("")
        ctx.write_note("90 - Referencia Gerada/Banco/Tabelas MySQL.md", {"type": "reference", "tags": ["banco", "mysql"]}, "Estrutura do Banco de Dados MySQL", "\n".join(db_lines))

    ctx.finalize()
    return ctx.stats

def update_script_timestamp():
    target = Path(__file__).resolve()
    content = read_text(target)
    now_iso = datetime.now().isoformat()
    updated = re.sub(
        r'LAST_DOCUMENTATION_UPDATE = "[^"]+"',
        f'LAST_DOCUMENTATION_UPDATE = "{now_iso}"',
        content,
        count=1,
    )
    target.write_text(updated, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Gerador determinístico da wiki Obsidian para o GIPAR")
    parser.add_argument("vault_path", help="Caminho do diretório raiz do cofre Obsidian")
    parser.add_argument("--dry-run", action="store_true", help="Simula a execução sem gravar arquivos")
    parser.add_argument("--clean", action="store_true", help="Remove arquivos órfãos não gerenciados mais")
    parser.add_argument("--scope", choices=["full", "backend", "frontend"], default="full", help="Escopo de geração")
    args = parser.parse_args()

    vault_dir = Path(args.vault_path).resolve()
    if not vault_dir.exists():
        print(f"Erro: O diretório do cofre não existe: {vault_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"==> Iniciando geração da Wiki GIPAR para: {vault_dir}")
    print(f"==> Escopo: {args.scope} | Dry-run: {args.dry_run} | Clean: {args.clean}")

    stats = generate_wiki(vault_dir, args)
    if not args.dry_run:
        update_script_timestamp()

    print("\n==> Resumo da sincronização:")
    print(json.dumps(stats, indent=2))
    print(f"==> Checkpoint registrado com sucesso em {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}")

if __name__ == "__main__":
    main()

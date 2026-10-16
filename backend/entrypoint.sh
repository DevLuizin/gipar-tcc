#!/bin/sh
set -e

echo "⏳ Aguardando banco de dados MySQL inicializar..."

python - << 'EOF'
import os
import time
import pymysql

host = os.getenv("DB_HOST") or os.getenv("host", "db")
user = os.getenv("DB_USER") or os.getenv("user", "root")
password = os.getenv("DB_PASSWORD") if os.getenv("DB_PASSWORD") is not None else os.getenv("password", "")
database = os.getenv("DB_NAME") or os.getenv("database", "gipar_db")

retries = 30
while retries > 0:
    try:
        con = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            connect_timeout=3
        )
        con.close()
        print("✅ Conexão com o MySQL estabelecida com sucesso!")
        break
    except Exception as e:
        print(f"Aguardando MySQL em {host}... ({e})")
        time.sleep(2)
        retries -= 1
else:
    print("❌ Tempo limite excedido ao aguardar o MySQL.")
    exit(1)
EOF

echo "🗃️ Aplicando migrations pendentes..."
python - << 'EOF'
import os
from pathlib import Path

import pymysql

diretorio = Path("/app/migrations")
if not diretorio.exists():
    print("ℹ️ Diretório de migrations não montado; nenhuma migration aplicada.")
    raise SystemExit(0)

config = {
    "host": os.getenv("DB_HOST") or os.getenv("host", "db"),
    "user": os.getenv("DB_USER") or os.getenv("user", "root"),
    "password": os.getenv("DB_PASSWORD") if os.getenv("DB_PASSWORD") is not None else os.getenv("password", ""),
    "database": os.getenv("DB_NAME") or os.getenv("database", "gipar_db"),
}

con = pymysql.connect(**config)
try:
    with con.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                nome VARCHAR(255) PRIMARY KEY,
                aplicado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """
        )
        con.commit()

        for caminho in sorted(diretorio.glob("*.sql")):
            cur.execute("SELECT 1 FROM schema_migrations WHERE nome = %s", (caminho.name,))
            if cur.fetchone():
                print(f"↪️ Migration já aplicada: {caminho.name}")
                continue

            linhas = [
                linha for linha in caminho.read_text(encoding="utf-8").splitlines()
                if not linha.lstrip().startswith("--")
            ]
            comandos = [comando.strip() for comando in "\n".join(linhas).split(";") if comando.strip()]
            try:
                for comando in comandos:
                    try:
                        cur.execute(comando)
                    except pymysql.err.OperationalError as erro:
                        if erro.args and erro.args[0] == 1060:
                            print("↪️ Coluna já existente; seguindo a migration.")
                            continue
                        raise
                cur.execute("INSERT INTO schema_migrations (nome) VALUES (%s)", (caminho.name,))
                con.commit()
                print(f"✅ Migration aplicada: {caminho.name}")
            except Exception:
                con.rollback()
                raise
finally:
    con.close()
EOF

echo "👤 Verificando/Criando usuário administrador padrão..."
python criar_admin.py || echo "⚠️ Aviso ao executar criar_admin.py (pode já existir)"
python teste_login.py || echo "⚠️ Aviso ao executar teste_login.py (pode já existir)"

echo "🚀 Iniciando servidor FastAPI (Uvicorn)..."
exec uvicorn main:app --host 0.0.0.0 --port 8000

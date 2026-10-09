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

echo "👤 Verificando/Criando usuário administrador padrão..."
python criar_admin.py || echo "⚠️ Aviso ao executar criar_admin.py (pode já existir)"
python teste_login.py || echo "⚠️ Aviso ao executar teste_login.py (pode já existir)"

echo "🚀 Iniciando servidor FastAPI (Uvicorn)..."
exec uvicorn main:app --host 0.0.0.0 --port 8000

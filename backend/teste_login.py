# scripts/inserir_usuarios.py
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os
import sys

# Adiciona o caminho do projeto para importar o seguranca
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seguranca import obter_hash_senha

load_dotenv()

config_db = {
    "host": os.getenv("DB_HOST") or os.getenv("host", "localhost"),
    "user": os.getenv("DB_USER") or os.getenv("user", "root"),
    "password": os.getenv("DB_PASSWORD") if os.getenv("DB_PASSWORD") is not None else os.getenv("password", ""),
    "database": os.getenv("DB_NAME") or os.getenv("database", "gipar_db"),
    "cursorclass": DictCursor
}

def inserir_usuarios():
    """Insere os usuários de demonstração com hashes gerados corretamente"""
    
    usuarios = [
        {
            "nome": "Administrador Sistema",
            "email": "admin@gipar.com",
            "senha": "admin123",
            "tipo_usuario": "ADMINISTRADOR"
        },
        {
            "nome": "Técnico Silva",
            "email": "tecnico@gipar.com",
            "senha": "tecnico123",
            "tipo_usuario": "TECNICO"
        },
        {
            "nome": "Usuário Comum",
            "email": "comum@gipar.com",
            "senha": "comum123",
            "tipo_usuario": "COMUM"
        }
    ]
    
    try:
        con = pymysql.connect(**config_db)
        cur = con.cursor()
        
        print("=" * 50)
        print("🌱 Inserindo usuários de demonstração...")
        print("=" * 50)
        
        for usuario in usuarios:
            # Verifica se já existe
            cur.execute("SELECT id FROM usuario WHERE email = %s", (usuario["email"],))
            if cur.fetchone():
                print(f"⏭️ Usuário {usuario['email']} já existe. Pulando...")
                continue
            
            # Gera o hash da senha usando a função do seu projeto
            senha_hash = obter_hash_senha(usuario["senha"])
            
            print(f"📝 Criando usuário: {usuario['email']}")
            print(f"   Senha: {usuario['senha']}")
            print(f"   Hash: {senha_hash[:30]}...")
            
            sql = """
                INSERT INTO usuario (nome, email, senha, tipo_usuario, ativo) 
                VALUES (%s, %s, %s, %s, TRUE)
            """
            cur.execute(sql, (
                usuario["nome"], 
                usuario["email"], 
                senha_hash, 
                usuario["tipo_usuario"]
            ))
            print(f"✅ Usuário {usuario['email']} criado com sucesso!\n")
        
        con.commit()
        print("=" * 50)
        print("✅ Todos os usuários foram inseridos com sucesso!")
        print("=" * 50)
        print("\n🔑 Credenciais de teste:")
        print("  ADMINISTRADOR: admin@gipar.com / admin123")
        print("  TECNICO: tecnico@gipar.com / tecnico123")
        print("  COMUM: comum@gipar.com / comum123")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if cur:
            cur.close()
        if con:
            con.close()

if __name__ == "__main__":
    inserir_usuarios()
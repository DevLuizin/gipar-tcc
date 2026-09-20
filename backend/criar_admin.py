import pymysql
import os
from dotenv import load_dotenv


load_dotenv()

#Todos os dados inseridos são exemplos, devem ser adaptados de acordo com o seu Banco
config_db = {
    'host': os.getenv('DB_HOST') or os.getenv('host', 'localhost'),
    'user': os.getenv('DB_USER') or os.getenv('user', 'root'),
    'password': os.getenv('DB_PASSWORD') or os.getenv('password', ''),
    'database': os.getenv('DB_NAME') or os.getenv('database', 'gipar_db'),
}

def cadastrar_admin():
    try:
        from seguranca import obter_hash_senha
    except ImportError:
        try:
            from gerenciador_db.usuario import obter_hash_senha
        except ImportError:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
            def obter_hash_senha(senha):
                return pwd_context.hash(senha)

    con = pymysql.connect(**config_db)
    cur = con.cursor()

    try:
        nome = "Administrador GIPAR"
        email = "adminTeste@gipar.com"
        senha_pura = "admin123"  
        senha_hasheada = obter_hash_senha(senha_pura)
        tipo_usuario = "ADMINISTRADOR"  
        ativo = True

  
        cur.execute("SELECT id FROM usuario WHERE email = %s", (email,))
        if cur.fetchone():
            print("Usuário administrador já existe no banco.")
            return

        sql = """
            INSERT INTO usuario (nome, email, senha, tipo_usuario, ativo) 
            VALUES (%s, %s, %s, %s, %s)
        """
        
        cur.execute(sql, (nome, email, senha_hasheada, tipo_usuario, ativo))
        con.commit()
        print("Administrador cadastrado com sucesso!")
        print(f"E-mail de acesso: {email}")
        print(f"Senha temporária: {senha_pura}")

    except Exception as e:
        con.rollback()
        print(f"Erro ao cadastrar administrador: {e}")
    finally:
        cur.close()
        con.close()

if __name__ == "__main__":
    cadastrar_admin()
"""Rotas de autenticação da API GIPAR."""

import traceback

import pymysql
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import config_db
from seguranca import criar_token_acesso, verificar_senha


router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    print("🔑 Iniciando processo de login...")
    con = None
    cur = None
    try:

        print("🔄 Conectando ao banco...")
        con = pymysql.connect(**config_db)
        cur = con.cursor()
        print("✅ Conectado ao banco!")

        # Busca o usuário
        print(f"🔍 Buscando usuário: {form_data.username}")
        sql = "SELECT id, nome, email, senha, tipo_usuario FROM usuario WHERE email = %s AND ativo = True"
        cur.execute(sql, (form_data.username,))
        usuario_db = cur.fetchone()

        if not usuario_db:
            print("❌ Usuário não encontrado!")
            raise HTTPException(status_code=401, detail="Email ou senha incorretos")

        print(f"✅ Usuário encontrado: {usuario_db['email']}")


        print("🔐 Verificando senha...")
        if not verificar_senha(form_data.password, usuario_db['senha']):
            print("❌ Senha incorreta!")
            raise HTTPException(status_code=401, detail="Email ou senha incorretos")
        print("✅ Senha correta!")


        perfil_map = {
            "ADMINISTRADOR": "admin",
            "TECNICO": "tecnico",
            "COMUM": "comum"
        }
        perfil_frontend = perfil_map.get(usuario_db['tipo_usuario'], "comum")


        print("🎫 Gerando token...")
        token_acesso = criar_token_acesso(dados={
            "sub": usuario_db['email'],
            "id": usuario_db['id'],
            "nome": usuario_db['nome'],
            "perfil": usuario_db['tipo_usuario']
        })
        print("✅ Token gerado com sucesso!")

        return {
            "access_token": token_acesso,
            "token_type": "bearer",
            "id": usuario_db['id'],
            "nome": usuario_db['nome'],
            "email": usuario_db['email'],
            "perfil": perfil_frontend,
            "tipo_usuario": usuario_db['tipo_usuario']
        }

    except HTTPException:
        raise

    except Exception as e:
        print("=" * 50)
        print("❌ ERRO NO LOGIN:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 50)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

    finally:
        if cur:
            cur.close()
            print("🔒 Cursor fechado")
        if con:
            con.close()
            print("🔒 Conexão fechada")




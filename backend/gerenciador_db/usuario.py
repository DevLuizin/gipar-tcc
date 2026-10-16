from fastapi import HTTPException
import pymysql
from pymysql.cursors import DictCursor
import traceback
from seguranca import obter_hash_senha, verificar_senha
from models.models import (
    AlterarSenhaRequest,
    AtualizarPerfilRequest,
    AtualizarTemaRequest,
    Usuario,
)

class UsuarioRepositorio:
    def __init__(self, db_config: dict):
        self.config_db = db_config
        self.config_db["cursorclass"] = DictCursor
    
    # ================================================================
    # MÉTODO PARA CRIAR USUÁRIO (COM TIPO_USUARIO)
    # ================================================================
    async def criar_usuario(self, usuario: Usuario):
            con = None
            cur = None

            try:
                con = pymysql.connect(**self.config_db)
                cur = con.cursor()

                # Verifica se o email já existe
                cur.execute("SELECT id FROM usuario WHERE email = %s", (usuario.email,))
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="E-mail já cadastrado")

                senha_hasheada = obter_hash_senha(usuario.senha)

                # ADICIONAMOS A COLUNA 'ativo' AQUI NO INSERT
                sql = """
                    INSERT INTO usuario (nome, email, senha, tipo_usuario, ativo) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                
                cur.execute(sql, (
                    usuario.nome,
                    usuario.email,
                    senha_hasheada,
                    usuario.tipo_usuario.value if hasattr(usuario.tipo_usuario, 'value') else usuario.tipo_usuario,
                    usuario.ativo  # <--- Passa o true/false vindo do frontend
                ))
                
                con.commit()
                return {"sucesso": True, "mensagem": "Usuário criado com sucesso"}

            except HTTPException:
                raise
            except Exception as e:
                con.rollback()
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                if cur:
                    cur.close()
                if con:
                    con.close()

    # ================================================================
    # MÉTODO PARA LISTAR USUÁRIOS
    # ================================================================
    async def listar_usuarios(self):
        con = None
        cur = None

        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()

            # 🔴 CORRIGIDO: Remove o filtro WHERE ativo = True
            sql = """
                SELECT id, nome, email, tipo_usuario, ativo, data_cadastro 
                FROM usuario 
                ORDER BY id
            """
            cur.execute(sql)
            usuarios = cur.fetchall()

            return {
                "sucesso": True,
                "quantidade": len(usuarios),
                "usuarios": usuarios
            }

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    # ================================================================
    # MÉTODO PARA LISTAR USUÁRIOS POR TIPO
    # ================================================================
    async def listar_usuarios_por_tipo(self, tipo: str):
        con = None
        cur = None

        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()

            # Filtra por tipo_usuario
            sql = """
                SELECT id, nome, email, tipo_usuario, ativo, data_cadastro 
                FROM usuario 
                WHERE ativo = True AND tipo_usuario = %s
                ORDER BY id
            """
            cur.execute(sql, (tipo,))
            usuarios = cur.fetchall()

            return {
                "sucesso": True,
                "quantidade": len(usuarios),
                "tipo": tipo,
                "usuarios": usuarios
            }

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    # ================================================================
    # MÉTODO PARA BUSCAR UM USUÁRIO POR ID
    # ================================================================
    async def buscar_usuario(self, usuario_id: int):
        con = None
        cur = None

        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()

            sql = """
                SELECT id, nome, email, tipo_usuario, ativo, data_cadastro 
                FROM usuario 
                WHERE id = %s
            """
            cur.execute(sql, (usuario_id,))
            usuario = cur.fetchone()

            if not usuario:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")

            return {
                "sucesso": True,
                "usuario": usuario
            }

        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    async def obter_perfil(self, usuario_id: int):
        con = None
        cur = None
        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()
            cur.execute(
                """
                SELECT id, nome, nome_exibicao, email, tipo_usuario,
                       avatar, tema, data_cadastro
                FROM usuario
                WHERE id = %s AND ativo = TRUE
                """,
                (usuario_id,),
            )
            usuario = cur.fetchone()
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            return usuario
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    async def atualizar_perfil(
        self,
        usuario_id: int,
        dados: AtualizarPerfilRequest,
    ):
        con = None
        cur = None
        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()
            cur.execute(
                """
                SELECT email, senha
                FROM usuario
                WHERE id = %s AND ativo = TRUE
                FOR UPDATE
                """,
                (usuario_id,),
            )
            usuario = cur.fetchone()
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")

            email_alterado = dados.email != usuario["email"].lower()
            if email_alterado:
                if not dados.senha_atual:
                    raise HTTPException(
                        status_code=400,
                        detail="Informe a senha atual para alterar o e-mail",
                    )
                if not verificar_senha(dados.senha_atual, usuario["senha"]):
                    raise HTTPException(status_code=400, detail="Senha atual incorreta")
                cur.execute(
                    "SELECT id FROM usuario WHERE email = %s AND id <> %s",
                    (dados.email, usuario_id),
                )
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="E-mail já cadastrado")

            incremento_versao = 1 if email_alterado else 0
            cur.execute(
                """
                UPDATE usuario
                SET nome = %s,
                    nome_exibicao = %s,
                    email = %s,
                    avatar = %s,
                    token_version = token_version + %s
                WHERE id = %s
                """,
                (
                    dados.nome,
                    dados.nome_exibicao,
                    dados.email,
                    dados.avatar.value if dados.avatar else None,
                    incremento_versao,
                    usuario_id,
                ),
            )
            con.commit()
            return {
                "perfil": await self.obter_perfil(usuario_id),
                "requer_novo_login": email_alterado,
            }
        except HTTPException:
            if con:
                con.rollback()
            raise
        except Exception as e:
            if con:
                con.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    async def alterar_senha(self, usuario_id: int, dados: AlterarSenhaRequest):
        con = None
        cur = None
        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()
            cur.execute(
                """
                SELECT senha
                FROM usuario
                WHERE id = %s AND ativo = TRUE
                FOR UPDATE
                """,
                (usuario_id,),
            )
            usuario = cur.fetchone()
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            if not verificar_senha(dados.senha_atual, usuario["senha"]):
                raise HTTPException(status_code=400, detail="Senha atual incorreta")

            cur.execute(
                """
                UPDATE usuario
                SET senha = %s, token_version = token_version + 1
                WHERE id = %s
                """,
                (obter_hash_senha(dados.nova_senha), usuario_id),
            )
            con.commit()
            return {
                "sucesso": True,
                "mensagem": "Senha alterada. Faça login novamente.",
                "requer_novo_login": True,
            }
        except HTTPException:
            if con:
                con.rollback()
            raise
        except Exception as e:
            if con:
                con.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    async def atualizar_tema(
        self,
        usuario_id: int,
        dados: AtualizarTemaRequest,
    ):
        con = None
        cur = None
        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()
            cur.execute(
                "UPDATE usuario SET tema = %s WHERE id = %s AND ativo = TRUE",
                (dados.tema.value, usuario_id),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            con.commit()
            return {"sucesso": True, "tema": dados.tema.value}
        except HTTPException:
            if con:
                con.rollback()
            raise
        except Exception as e:
            if con:
                con.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    # ================================================================
    # MÉTODO PARA ATUALIZAR USUÁRIO (COM TIPO_USUARIO)
    # ================================================================
    async def atualizar_usuario(self, usuario_id: int, usuario: Usuario):
        con = None
        cur = None

        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()

       
            cur.execute("SELECT id FROM usuario WHERE id = %s", (usuario_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Usuário não encontrado")

         
            cur.execute("SELECT id FROM usuario WHERE email = %s AND id != %s", (usuario.email, usuario_id))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Email já está em uso por outro usuário")

           
            senha_hasheada = obter_hash_senha(usuario.senha)

            
            sql = """
                UPDATE usuario 
                SET nome = %s, email = %s, senha = %s, tipo_usuario = %s, ativo = %s 
                WHERE id = %s
            """
            
        
            cur.execute(sql, (
                usuario.nome, 
                usuario.email, 
                senha_hasheada, 
                usuario.tipo_usuario.value if hasattr(usuario.tipo_usuario, 'value') else usuario.tipo_usuario,
                usuario.ativo, 
                usuario_id
            ))
            con.commit()

            return {
                "sucesso": True,
                "mensagem": "Usuário atualizado com sucesso"
            }

        except HTTPException:
            raise
        except Exception as e:
            con.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    # ================================================================
    # MÉTODO PARA INATIVAR USUÁRIO
    # ================================================================
    async def inativar_usuario(self, usuario_id: int):
        con = None
        cur = None

        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()

           
            cur.execute("SELECT id FROM usuario WHERE id = %s", (usuario_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Usuário não encontrado")

           
            cur.execute("""
                SELECT COUNT(*) as total 
                FROM usuario 
                WHERE tipo_usuario = 'ADMINISTRADOR' AND ativo = True
            """)
            total_admins = cur.fetchone()['total']
            
            cur.execute("SELECT tipo_usuario FROM usuario WHERE id = %s", (usuario_id,))
            usuario_tipo = cur.fetchone()['tipo_usuario']
            
            if usuario_tipo == 'ADMINISTRADOR' and total_admins <= 1:
                raise HTTPException(status_code=400, detail="Não é possível inativar o último administrador do sistema")

            
            sql = "UPDATE usuario SET ativo = False WHERE id = %s"
            cur.execute(sql, (usuario_id,))
            con.commit()

            return {
                "sucesso": True,
                "mensagem": "Usuário inativado com sucesso"
            }

        except HTTPException:
            raise
        except Exception as e:
            con.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    # ================================================================
    # MÉTODO PARA REATIVAR USUÁRIO
    # ================================================================
    async def reativar_usuario(self, usuario_id: int):
        con = None
        cur = None

        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()

            sql = "UPDATE usuario SET ativo = True WHERE id = %s"
            cur.execute(sql, (usuario_id,))
            
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuário não encontrado.")
                
            con.commit()

            return {
                "sucesso": True,
                "mensagem": "Usuário reativado com sucesso"
            }

        except HTTPException:
            raise
        except Exception as e:
            con.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    # ================================================================
    # MÉTODO PARA ALTERAR TIPO DE USUÁRIO (apenas ADMIN)
    # ================================================================
    async def alterar_tipo_usuario(self, usuario_id: int, novo_tipo: str, admin_id: int):
        """Altera o tipo de usuário. Apenas administradores podem fazer isso."""
        con = None
        cur = None

        try:
            con = pymysql.connect(**self.config_db)
            cur = con.cursor()

            # 1. Verifica se o admin existe e é ADMINISTRADOR
            cur.execute("SELECT tipo_usuario FROM usuario WHERE id = %s AND ativo = True", (admin_id,))
            admin = cur.fetchone()
            if not admin or admin['tipo_usuario'] != 'ADMINISTRADOR':
                raise HTTPException(status_code=403, detail="Apenas administradores podem alterar tipos de usuário")

            # 2. Verifica se o usuário alvo existe
            cur.execute("SELECT id, tipo_usuario FROM usuario WHERE id = %s", (usuario_id,))
            usuario_alvo = cur.fetchone()
            if not usuario_alvo:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")

            # 3. Não permite alterar o próprio tipo (evita perder acesso)
            if usuario_id == admin_id:
                raise HTTPException(status_code=400, detail="Não é possível alterar seu próprio tipo de usuário")

            # 4. Verifica se o novo tipo é válido
            tipos_validos = ['ADMINISTRADOR', 'TECNICO', 'COMUM']
            if novo_tipo not in tipos_validos:
                raise HTTPException(status_code=400, detail="Tipo de usuário inválido")

            # 5. Verifica se o usuário alvo não é o último administrador
            if usuario_alvo['tipo_usuario'] == 'ADMINISTRADOR':
                cur.execute("""
                    SELECT COUNT(*) as total 
                    FROM usuario 
                    WHERE tipo_usuario = 'ADMINISTRADOR' AND ativo = True
                """)
                total_admins = cur.fetchone()['total']
                if total_admins <= 1:
                    raise HTTPException(
                        status_code=400, 
                        detail="Não é possível alterar o último administrador do sistema"
                    )

            # 6. Altera o tipo
            sql = "UPDATE usuario SET tipo_usuario = %s WHERE id = %s"
            cur.execute(sql, (novo_tipo, usuario_id))
            con.commit()

            return {
                "sucesso": True,
                "mensagem": f"Tipo de usuário alterado para {novo_tipo} com sucesso",
                "usuario_id": usuario_id,
                "novo_tipo": novo_tipo
            }

        except HTTPException:
            raise
        except Exception as e:
            con.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()

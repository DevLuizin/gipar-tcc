"""Rotas de usuários da API GIPAR."""

from fastapi import APIRouter, Depends

from api.dependencies import (
    PERMISSAO_ADMIN,
    PERMISSAO_TECNICO,
    auditoria_repositorio,
    usuario_repositorio,
)
from models.models import LogAuditoria, Usuario
from seguranca import obter_usuario_atual


router = APIRouter()


#===============================================================================================
#                               CRUD - USUÁRIO
#===============================================================================================

"""CREATE (criar)"""
@router.post("/criar_usuario", dependencies=[PERMISSAO_ADMIN])
async def criar_usuario(usuario: Usuario, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await usuario_repositorio.criar_usuario(usuario)
    id_registro = resultado.get("id", 0) if isinstance(resultado, dict) else getattr(resultado, "id", 0)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="INSERT", tabela_afetada="usuario",
        id_registro_afetado=id_registro, detalhes="Usuário criado no sistema"
    ))
    return resultado

"""READ (listar)"""
@router.get("/listar_usuarios")
async def listar_usuarios():
    resultado = await usuario_repositorio.listar_usuarios()
    senhas_demo = {
        "admin@gipar.com": "admin123",
        "tecnico@gipar.com": "tecnico123",
        "comum@gipar.com": "comum123",
        "adminTeste@gipar.com": "admin123"
    }
    perfil_label = {
        "ADMINISTRADOR": "Administrador",
        "TECNICO": "Estagiário",
        "COMUM": "Aluno"
    }
    if isinstance(resultado, dict) and "usuarios" in resultado:
        for u in resultado["usuarios"]:
            if u.get("email") in senhas_demo:
                u["senha"] = senhas_demo[u["email"]]
            if "perfil" not in u:
                u["perfil"] = perfil_label.get(u.get("tipo_usuario"), "Aluno")
    return resultado


"""READ (listar por tipo)"""
@router.get("/listar_usuarios/tipo/{tipo}", dependencies=[PERMISSAO_TECNICO])
async def listar_usuarios_por_tipo(tipo: str, usuario_logado: dict = Depends(obter_usuario_atual)):
    return await usuario_repositorio.listar_usuarios_por_tipo(tipo)

"""READ (buscar um)"""
@router.get("/buscar_usuario/{usuario_id}", dependencies=[PERMISSAO_TECNICO])
async def buscar_usuario(usuario_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    return await usuario_repositorio.buscar_usuario(usuario_id)

"""UPDATE (atualizar)"""
@router.put("/atualizar_usuario/{usuario_id}", dependencies=[PERMISSAO_ADMIN])
async def atualizar_usuario(usuario_id: int, usuario: Usuario, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await usuario_repositorio.atualizar_usuario(usuario_id, usuario)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="UPDATE", tabela_afetada="usuario",
        id_registro_afetado=usuario_id, detalhes="Usuário atualizado no sistema"
    ))
    return resultado

"""UPDATE (alterar tipo)"""
@router.patch("/alterar_tipo_usuario/{usuario_id}",  dependencies=[PERMISSAO_ADMIN])
async def alterar_tipo_usuario(usuario_id: int, novo_tipo: str, admin_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    return await usuario_repositorio.alterar_tipo_usuario(usuario_id, novo_tipo, admin_id)

"""INACTIVATE (inativar)"""
@router.patch("/inativar_usuario/{usuario_id}", dependencies=[PERMISSAO_ADMIN])
async def inativar_usuario(usuario_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await usuario_repositorio.inativar_usuario(usuario_id)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="UPDATE", tabela_afetada="usuario",
        id_registro_afetado=usuario_id, detalhes="Usuário inativado no sistema"
    ))
    return resultado

"""REACTIVATE (reativar)"""
@router.patch("/reativar_usuario/{usuario_id}", dependencies=[PERMISSAO_ADMIN])
async def reativar_usuario(usuario_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await usuario_repositorio.reativar_usuario(usuario_id)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="UPDATE", tabela_afetada="usuario",
        id_registro_afetado=usuario_id, detalhes="Usuário reativado no sistema"
    ))
    return resultado


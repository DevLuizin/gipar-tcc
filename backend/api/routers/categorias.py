"""Rotas de categorias da API GIPAR."""

from fastapi import APIRouter, Depends

from api.dependencies import (
    PERMISSAO_ADMIN,
    auditoria_repositorio,
    categoria_repositorio,
)
from models.models import Categoria, LogAuditoria
from seguranca import obter_usuario_atual


router = APIRouter()


#===============================================================================================
#                               CRUD - CATEGORIA
#===============================================================================================

"""CREATE (criar)"""
@router.post("/criar_categoria", dependencies=[PERMISSAO_ADMIN])
async def criar_categoria(categoria: Categoria,
    usuario_logado: dict = Depends(obter_usuario_atual)):

    resultado = await categoria_repositorio.criar_categoria(categoria)
    novo_log = LogAuditoria(
        id_usuario=usuario_logado["id"],
        acao="INSERT",
        tabela_afetada="categoria",
        id_registro_afetado=resultado.get("id", 0) if isinstance(resultado, dict) else 0,
        detalhes=f"Categoria criada no sistema"
    )
    await auditoria_repositorio.registrar_log(novo_log)

    return resultado

"""READ (listar)"""
@router.get("/listar_categorias")
async def listar_categorias(usuario_logado: dict = Depends(obter_usuario_atual)):
    return await categoria_repositorio.listar_categorias()

"""UPDATE (atualizar)"""
@router.put("/atualizar_categoria/{categoria_id}",  dependencies=[PERMISSAO_ADMIN])
async def atualizar_categoria(categoria_id: int, categoria: Categoria, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await categoria_repositorio.atualizar_categoria(categoria_id, categoria)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="UPDATE", tabela_afetada="categoria",
        id_registro_afetado=categoria_id, detalhes="Categoria atualizada no sistema"
    ))
    return resultado

"""DELETE (apagar)"""
@router.delete("/excluir_categoria/{categoria_id}",dependencies=[PERMISSAO_ADMIN])
async def excluir_categoria(categoria_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await categoria_repositorio.excluir_categoria(categoria_id)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="DELETE", tabela_afetada="categoria",
        id_registro_afetado=categoria_id, detalhes="Categoria excluída do sistema"
    ))
    return resultado


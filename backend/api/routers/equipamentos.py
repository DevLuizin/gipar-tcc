"""Rotas de equipamentos da API GIPAR."""

from fastapi import APIRouter, Depends

from api.dependencies import (
    PERMISSAO_ADMIN,
    PERMISSAO_TECNICO,
    auditoria_repositorio,
    equipamento_repositorio,
    historico_repositorio,
)
from models.models import Equipamento, HistoricoMovimentacao, LogAuditoria
from seguranca import obter_usuario_atual


router = APIRouter()


#===============================================================================================
#                               CRUD - EQUIPAMENTO
#===============================================================================================

"""CREATE (criar)"""
@router.post("/criar_equipamento", dependencies=[PERMISSAO_TECNICO])
async def criar_equipamento(equipamento: Equipamento, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await equipamento_repositorio.criar_equipamento(equipamento)
    id_registro = resultado.get("id", 0) if isinstance(resultado, dict) else getattr(resultado, "id", 0)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="INSERT", tabela_afetada="equipamento",
        id_registro_afetado=id_registro, detalhes="Equipamento criado no sistema"
    ))
    await historico_repositorio.registrar_movimentacao(HistoricoMovimentacao(
        id_equipamento=id_registro,
        id_usuario_acao=usuario_logado["id"],
        descricao_motivo="Equipamento cadastrado no sistema"
    ))
    return resultado

"""READ (listar)"""
@router.get("/listar_equipamentos")
async def listar_equipamentos( usuario_logado: dict = Depends(obter_usuario_atual)):
    return await equipamento_repositorio.listar_equipamentos()

"""UPDATE (atualizar)"""
@router.put("/atualizar_equipamento/{equipamento_id}", dependencies=[PERMISSAO_TECNICO])
async def atualizar_equipamento(equipamento_id: int, equipamento: Equipamento, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await equipamento_repositorio.atualizar_equipamento(equipamento_id, equipamento)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="UPDATE", tabela_afetada="equipamento",
        id_registro_afetado=equipamento_id, detalhes="Equipamento atualizado no sistema"
    ))
    return resultado

"""INACTIVATE (inativar)"""
@router.patch("/inativar_equipamento/{equipamento_id}", dependencies=[PERMISSAO_TECNICO])
async def inativar_equipamento(equipamento_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await equipamento_repositorio.inativar_equipamento(equipamento_id)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="UPDATE", tabela_afetada="equipamento",
        id_registro_afetado=equipamento_id, detalhes="Equipamento inativado no sistema"
    ))
    return resultado

"""REACTIVATE (reativar)"""
@router.patch("/reativar_equipamento/{equipamento_id}", dependencies=[PERMISSAO_TECNICO])
async def reativar_equipamento(equipamento_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await equipamento_repositorio.reativar_equipamento(equipamento_id)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="UPDATE", tabela_afetada="equipamento",
        id_registro_afetado=equipamento_id, detalhes="Equipamento reativado no sistema"
    ))
    return resultado

"""DELETE (excluir permanentemente)"""
@router.delete("/excluir_equipamento/{equipamento_id}", dependencies=[PERMISSAO_ADMIN])
async def excluir_equipamento(equipamento_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await equipamento_repositorio.excluir_equipamento(equipamento_id)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"],
        acao="DELETE",
        tabela_afetada="equipamento",
        id_registro_afetado=equipamento_id,
        detalhes="Equipamento excluído permanentemente do sistema"
    ))
    return resultado


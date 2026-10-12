"""Rotas de reservas da API GIPAR."""

from fastapi import APIRouter, Depends

from api.dependencies import (
    PERMISSAO_TECNICO,
    auditoria_repositorio,
    reserva_repositorio,
)
from models.models import LogAuditoria, Reserva
from seguranca import obter_usuario_atual


router = APIRouter()


#===============================================================================================
#                               CRUD - RESERVA
#===============================================================================================

@router.post("/criar_reserva", dependencies=[PERMISSAO_TECNICO])
async def criar_reserva(reserva: Reserva, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await reserva_repositorio.criar_reserva(reserva)
    id_registro = resultado.get("id", 0) if isinstance(resultado, dict) else getattr(resultado, "id", 0)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="INSERT", tabela_afetada="reserva",
        id_registro_afetado=id_registro, detalhes="Reserva criada no sistema"
    ))
    return resultado

@router.get("/listar_reservas")
async def listar_reservas(usuario_logado: dict = Depends(obter_usuario_atual)):
    return await reserva_repositorio.listar_reservas(usuario_logado=usuario_logado)

@router.put("/atualizar_reserva/{reserva_id}", dependencies=[PERMISSAO_TECNICO])
async def atualizar_reserva(reserva_id: int, reserva: Reserva, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await reserva_repositorio.atualizar_reserva(reserva_id, reserva)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="UPDATE", tabela_afetada="reserva",
        id_registro_afetado=reserva_id, detalhes="Reserva atualizada no sistema"
    ))
    return resultado

@router.delete("/excluir_reserva/{reserva_id}", dependencies=[PERMISSAO_TECNICO])
async def excluir_reserva(reserva_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await reserva_repositorio.excluir_reserva(reserva_id)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="DELETE", tabela_afetada="reserva",
        id_registro_afetado=reserva_id, detalhes="Reserva excluída do sistema"
    ))
    return resultado


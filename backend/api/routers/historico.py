"""Rotas de histórico da API GIPAR."""

from fastapi import APIRouter, Depends

from api.dependencies import PERMISSAO_TECNICO, historico_repositorio
from seguranca import obter_usuario_atual


router = APIRouter()


#===============================================================================================
#                               CRUD - HISTÓRICO
#===============================================================================================

"""READ (listar)"""
@router.get("/listar_historico", dependencies=[PERMISSAO_TECNICO])
async def listar_historico(id_equipamento: int = None, usuario_logado: dict = Depends(obter_usuario_atual)):
    return await historico_repositorio.listar_historico(id_equipamento)


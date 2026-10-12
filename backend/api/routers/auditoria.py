"""Rotas de auditoria da API GIPAR."""

from fastapi import APIRouter

from api.dependencies import PERMISSAO_ADMIN, auditoria_repositorio


router = APIRouter()


@router.get("/listar_logs", dependencies=[PERMISSAO_ADMIN])
async def listar_logs(tabela: str = None, id_usuario: int = None):
    return await auditoria_repositorio.listar_logs(tabela, id_usuario)


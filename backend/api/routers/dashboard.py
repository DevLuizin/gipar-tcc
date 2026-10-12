"""Rotas de dashboard da API GIPAR."""

from fastapi import APIRouter, Depends

from api.dependencies import PERMISSAO_TECNICO, dashboard_service
from seguranca import obter_usuario_atual


router = APIRouter()


@router.get("/dashboard/estatisticas", dependencies=[PERMISSAO_TECNICO])
async def obter_estatisticas_dashboard(usuario_logado: dict = Depends(obter_usuario_atual)):
    return await dashboard_service.obter_estatisticas()


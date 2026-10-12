"""Rotas de manutenções da API GIPAR."""

import pymysql
from fastapi import APIRouter, Depends

from api.dependencies import (
    PERMISSAO_TECNICO,
    auditoria_repositorio,
    config_db,
    historico_repositorio,
    manutencao_repositorio,
)
from models.models import (
    HistoricoMovimentacao,
    LogAuditoria,
    Manutencao,
    ManutencaoUpdate,
    StatusEquipamento,
)
from seguranca import obter_usuario_atual


router = APIRouter()


#===============================================================================================
#                               CRUD - MANUTENÇÃO
#===============================================================================================

@router.post("/criar_manutencao", dependencies=[PERMISSAO_TECNICO])
async def criar_manutencao(manutencao: Manutencao, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await manutencao_repositorio.criar_manutencao(manutencao)
    id_registro = resultado.get("id", 0) if isinstance(resultado, dict) else getattr(resultado, "id", 0)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="INSERT", tabela_afetada="manutencao",
        id_registro_afetado=id_registro, detalhes="Manutenção criada no sistema"
    ))


    con = None
    cur = None
    status_atual_enum = StatusEquipamento.DISPONIVEL
    try:
        con = pymysql.connect(**config_db)
        cur = con.cursor()
        cur.execute("SELECT status FROM equipamento WHERE id = %s", (manutencao.id_equipamento,))
        equipamento = cur.fetchone()
        if equipamento:
            status_atual_str = equipamento['status']
            if status_atual_str == "DISPONIVEL":
                status_atual_enum = StatusEquipamento.DISPONIVEL
            elif status_atual_str == "EM_USO":
                status_atual_enum = StatusEquipamento.EM_USO
            elif status_atual_str == "RESERVADO":
                status_atual_enum = StatusEquipamento.RESERVADO
            elif status_atual_str == "EM_MANUTENCAO":
                status_atual_enum = StatusEquipamento.EM_MANUTENCAO
            elif status_atual_str == "INATIVO":
                status_atual_enum = StatusEquipamento.INATIVO
    except Exception as e:
        print(f"Erro ao buscar status do equipamento: {e}")
    finally:
        if cur:
            cur.close()
        if con:
            con.close()

    await historico_repositorio.registrar_movimentacao(HistoricoMovimentacao(
        id_equipamento=manutencao.id_equipamento,
        id_usuario_acao=usuario_logado["id"],
        status_anterior=status_atual_enum,
        status_novo=StatusEquipamento.EM_MANUTENCAO,
        descricao_motivo=f"Manutenção registrada (ID {id_registro})"
    ))

    return resultado

@router.get("/listar_manutencoes")
async def listar_manutencoes(usuario_logado: dict = Depends(obter_usuario_atual)):
    return await manutencao_repositorio.listar_manutencoes()

"""UPDATE (atualizar) - CORRIGIDO com modelo de atualização parcial"""
@router.put("/atualizar_manutencao/{manutencao_id}", dependencies=[PERMISSAO_TECNICO])
async def atualizar_manutencao(
    manutencao_id: int,
    manutencao: ManutencaoUpdate,
    usuario_logado: dict = Depends(obter_usuario_atual)
):
    """
    Endpoint para atualizar uma manutenção existente.
    Aceita atualização parcial (apenas os campos enviados).
    """
    resultado = await manutencao_repositorio.atualizar_manutencao(manutencao_id, manutencao)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"],
        acao="UPDATE",
        tabela_afetada="manutencao",
        id_registro_afetado=manutencao_id,
        detalhes="Manutenção atualizada no sistema"
    ))
    return resultado

"""DELETE (apagar)"""
@router.delete("/excluir_manutencao/{manutencao_id}", dependencies=[PERMISSAO_TECNICO])
async def excluir_manutencao(manutencao_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await manutencao_repositorio.excluir_manutencao(manutencao_id)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"],
        acao="DELETE",
        tabela_afetada="manutencao",
        id_registro_afetado=manutencao_id,
        detalhes="Manutenção excluída do sistema"
    ))
    return resultado




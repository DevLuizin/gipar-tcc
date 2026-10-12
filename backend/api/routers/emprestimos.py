"""Rotas de empréstimos da API GIPAR."""

import traceback

import pymysql
from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import (
    PERMISSAO_TECNICO,
    auditoria_repositorio,
    config_db,
    emprestimo_repositorio,
    historico_repositorio,
)
from models.models import (
    Emprestimo,
    EmprestimoUpdate,
    HistoricoMovimentacao,
    LogAuditoria,
    StatusEquipamento,
)
from seguranca import obter_usuario_atual


router = APIRouter()


#===============================================================================================
#                               CRUD - EMPRÉSTIMO
#===============================================================================================

@router.post("/criar_emprestimo", dependencies=[PERMISSAO_TECNICO])
async def criar_emprestimo(emprestimo: Emprestimo, usuario_logado: dict = Depends(obter_usuario_atual)):
    emprestimo.id_tecnico_saida = usuario_logado["id"]
    resultado = await emprestimo_repositorio.criar_emprestimo(emprestimo)
    id_registro = resultado.get("id", 0) if isinstance(resultado, dict) else getattr(resultado, "id", 0)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="INSERT", tabela_afetada="emprestimo",
        id_registro_afetado=id_registro, detalhes="Empréstimo criado no sistema"
    ))
    await historico_repositorio.registrar_movimentacao(HistoricoMovimentacao(
        id_equipamento=emprestimo.id_equipamento,
        id_usuario_acao=usuario_logado["id"],
        descricao_motivo=f"Empréstimo criado (ID {id_registro})"
    ))
    return resultado

@router.get("/listar_emprestimos")
async def listar_emprestimos(apenas_ativos: bool = False, usuario_logado: dict = Depends(obter_usuario_atual)):
    return await emprestimo_repositorio.listar_emprestimos(apenas_ativos=apenas_ativos, usuario_logado=usuario_logado)

"""UPDATE (atualizar)"""
@router.put("/atualizar_emprestimo/{emprestimo_id}", dependencies=[PERMISSAO_TECNICO])
async def atualizar_emprestimo(
    emprestimo_id: int,
    emprestimo: EmprestimoUpdate,
    usuario_logado: dict = Depends(obter_usuario_atual)
):
    """
    Endpoint para atualizar um empréstimo existente.
    Aceita atualização parcial (apenas os campos enviados).
    """
    resultado = await emprestimo_repositorio.atualizar_emprestimo(emprestimo_id, emprestimo)

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"],
        acao="UPDATE",
        tabela_afetada="emprestimo",
        id_registro_afetado=emprestimo_id,
        detalhes="Empréstimo atualizado no sistema"
    ))

    return resultado

"""UPDATE (devolver)"""
@router.put("/devolver_emprestimo/{emprestimo_id}", dependencies=[PERMISSAO_TECNICO])
async def devolver_emprestimo(emprestimo_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await emprestimo_repositorio.registrar_devolucao(emprestimo_id, usuario_logado["id"])

    await auditoria_repositorio.registrar_log(LogAuditoria(
        id_usuario=usuario_logado["id"], acao="UPDATE", tabela_afetada="emprestimo",
        id_registro_afetado=emprestimo_id, detalhes="Devolução de equipamento registrada"
    ))
    return resultado

"""ESSE CRUD NÃO POSSUI A FUNÇÃO DELETE, POIS O REGISTRO DE EMPRÉSTIMO DEVE SER MANTIDO
PARA FINS DE HISTÓRICO, LOGS E RELATÓRIOS."""

"""UPDATE (cancelar)"""
@router.patch("/cancelar_emprestimo/{emprestimo_id}", dependencies=[PERMISSAO_TECNICO])
async def cancelar_emprestimo(emprestimo_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    con = None
    cur = None
    try:
        con = pymysql.connect(**config_db)
        cur = con.cursor()

        cur.execute("SELECT id, id_equipamento, status FROM emprestimo WHERE id = %s", (emprestimo_id,))
        emprestimo = cur.fetchone()
        if not emprestimo:
            raise HTTPException(status_code=404, detail="Empréstimo não encontrado")

        if emprestimo['status'] in ['DEVOLVIDO', 'CANCELADO']:
            raise HTTPException(status_code=400, detail="Empréstimo já está finalizado")
        sql = "UPDATE emprestimo SET status = 'CANCELADO' WHERE id = %s"
        cur.execute(sql, (emprestimo_id,))
        con.commit()


        cur.execute("""
            UPDATE equipamento SET status = 'DISPONIVEL'
            WHERE id = %s
        """, (emprestimo['id_equipamento'],))
        con.commit()

        await auditoria_repositorio.registrar_log(LogAuditoria(
            id_usuario=usuario_logado["id"],
            acao="UPDATE",
            tabela_afetada="emprestimo",
            id_registro_afetado=emprestimo_id,
            detalhes=f"Empréstimo cancelado - status alterado para CANCELADO"
        ))

        await historico_repositorio.registrar_movimentacao(HistoricoMovimentacao(
            id_equipamento=emprestimo['id_equipamento'],
            id_usuario_acao=usuario_logado["id"],
            status_anterior=StatusEquipamento.EM_USO,
            status_novo=StatusEquipamento.DISPONIVEL,
            descricao_motivo=f"Empréstimo cancelado (ID {emprestimo_id})"
        ))

        return {
            "sucesso": True,
            "mensagem": "Empréstimo cancelado com sucesso"
        }

    except HTTPException:
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




"""Rotas de sistema da API GIPAR."""

import traceback

import pymysql
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.dependencies import config_db
from seguranca import obter_usuario_atual
from servicos.email_service import enviar_email


router = APIRouter()


@router.get("/")
async def home():

    return {
        "mensagem": "Bem-vindo à API do GIPAR!",
        "versao": "2.0",
        "instrucoes": "Acesse /docs para usar a interface web",
        "endpoints": {
            "GET /": "Esta mensagem",
            "POST /criar_categoria": "Criar categoria",
            "GET /listar_categorias": "Listar categorias",
            "PUT /atualizar_categoria/{categoria_id}": "Atualizar categoria",
            "DELETE /excluir_categoria/{categoria_id}": "Excluir categoria",
            "POST /criar_usuario": "Criar usuário",
            "GET /listar_usuarios": "Listar usuários",
            "PUT /atualizar_usuario/{usuario_id}": "Atualizar usuário",
            "PATCH /inativar_usuario/{usuario_id}": "Inativar usuário",
            "PATCH /reativar_usuario/{usuario_id}": "Reativar usuário",
            "POST /criar_equipamento": "Criar equipamento",
            "GET /listar_equipamentos": "Listar equioamentos",
            "PUT /atualizar_equipamento/{equipamento_id}": "Atualizar equipamento",
            "PATCH /inativar_equipamento/{equipamento_id}": "Inativar equipamento",
            "PATCH /reativar_equipamento/{equipamento_id}": "Reativar equipamento",
            "POST /criar_manutencao": "Criar manutenção",
            "GET /listar_manutencoes": "Listar manuteções",
            "PUT /atualizar_manutencao/{manutencao_id}": "Atualizar manutenção",
            "DELETE /excluir_manutecao/{manutencao_id}": "Excluir manutenção",
            "POST /criar_reserva": "Criar reserva",
            "GET /listar_reservas": "Listar reservas",
            "PUT /atualizar_reserva/{reserva_id}": "Atualizar reserva",
            "DELETE /excluir_reserva/{reserva_id}": "Excluir reserva",
            "POST /criar_emprestimo": "Criar empréstimo",
            "GET /listar_emprestimos": "Listar empréstimos",
            "PUT /atualizar_emprestimo/{emprestimo_id}": "Atualizar empréstimo",
            "PATCH /registrar_devolucao/{emprestimo_id}": "Registrar devolução",
            "GET /listar_historico": "Listar histórico",
            "GET /dashboard/estatisticas": "Estatísticas do dashboard",
        }
    }



#===============================================================================================
#                               SERVIÇOS EXTRAS
#===============================================================================================

@router.get("/diagnostico/manutencao/{manutencao_id}")
async def diagnosticar_manutencao(manutencao_id: int, usuario_logado: dict = Depends(obter_usuario_atual)):
    con = None
    cur = None
    try:
        con = pymysql.connect(**config_db)
        cur = con.cursor()

        cur.execute("SELECT * FROM manutencao WHERE id = %s", (manutencao_id,))
        manutencao = cur.fetchone()

        if not manutencao:
            raise HTTPException(status_code=404, detail="Manutenção não encontrada")

        return {
            "manutencao": manutencao,
            "tipo_atual": manutencao.get('tipo'),
            "status_atual": manutencao.get('status'),
            "campos": list(manutencao.keys()) if manutencao else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


async def obter_estatisticas(self):
    con = None
    cur = None
    try:
        con = pymysql.connect(**self.config_db)
        cur = con.cursor()

        cur.execute("SELECT COUNT(*) as total FROM equipamento WHERE ativo = 1")
        total_equipamentos = cur.fetchone()['total']

        cur.execute("SELECT COUNT(*) as total FROM usuario WHERE ativo = 1")
        total_usuarios = cur.fetchone()['total']


        cur.execute("""
            SELECT COUNT(*) as total
            FROM manutencao
            WHERE status IN ('PENDENTE', 'EM_ANDAMENTO')
        """)
        em_manutencao = cur.fetchone()['total']


        cur.execute("""
            SELECT COUNT(*) as total
            FROM manutencao
            WHERE tipo = 'CORRETIVA'
            AND status IN ('PENDENTE', 'EM_ANDAMENTO')
        """)
        corretivas = cur.fetchone()['total']


        cur.execute("""
            SELECT COUNT(*) as total
            FROM manutencao
            WHERE tipo = 'PREVENTIVA'
            AND status IN ('PENDENTE', 'EM_ANDAMENTO')
        """)
        preventivas = cur.fetchone()['total']


        cur.execute("""
            SELECT COUNT(*) as total
            FROM manutencao
            WHERE status = 'CONCLUIDO'
        """)
        concluidas = cur.fetchone()['total']


        cur.execute("""
            SELECT COUNT(*) as total
            FROM emprestimo
            WHERE status = 'ATIVO'
        """)
        emprestimos_ativos = cur.fetchone()['total']

        return {
            "total_equipamentos": total_equipamentos,
            "total_usuarios": total_usuarios,
            "em_manutencao": em_manutencao,
            "corretivas": corretivas,
            "preventivas": preventivas,
            "concluidas": concluidas,
            "emprestimos_ativos": emprestimos_ativos
        }
    except Exception as e:
        print(f"Erro no dashboard: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur:
            cur.close()
        if con:
            con.close()
class EmailRequest(BaseModel):
    destinatario: str
    assunto: str
    corpo: str

@router.post("/testar-email")
async def testar_email(req: EmailRequest):
    try:
        sucesso = enviar_email(req.destinatario, req.assunto, req.corpo)
        if sucesso:
            return {"sucesso": True, "mensagem": f"E-mail enviado com sucesso para {req.destinatario}!"}
        else:
            raise HTTPException(status_code=500, detail="Falha ao enviar e-mail. Verifique o console do servidor.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




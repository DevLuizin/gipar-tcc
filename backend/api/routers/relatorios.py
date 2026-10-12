"""Rotas de relatórios da API GIPAR."""

import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fpdf import FPDF

from api.dependencies import (
    PERMISSAO_TECNICO,
    categoria_repositorio,
    emprestimo_repositorio,
    equipamento_repositorio,
    manutencao_repositorio,
    reserva_repositorio,
    usuario_repositorio,
)
from seguranca import obter_usuario_atual


router = APIRouter()


"""GERAR RELATÓRIO (CSV E PDF) COM FILTRO DE DATAS"""
@router.get("/relatorios/emprestimos", dependencies=[PERMISSAO_TECNICO])
async def relatorio_emprestimos(
    formato: str = "csv",
    data_inicial: str = None,
    data_final: str = None,
    usuario_logado: dict = Depends(obter_usuario_atual)
):
    resultado = await emprestimo_repositorio.listar_emprestimos()
    emprestimos = resultado.get("emprestimos", [])


    if data_inicial and data_final:
        emprestimos_filtrados = []
        for emp in emprestimos:
            data_ret = str(emp.get("data_retirada", ""))[:10]
            if data_ret and data_inicial <= data_ret <= data_final:
                emprestimos_filtrados.append(emp)
        emprestimos = emprestimos_filtrados

    # Se pedirem CSV:
    if formato.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(["ID", "Equipamento", "Patrimonio", "Usuario", "Data Retirada", "Status"])

        for emp in emprestimos:
            writer.writerow([
                emp.get("emprestimo_id", ""),
                emp.get("nome_equipamento", ""),
                emp.get("codigo_patrimonio", ""),
                emp.get("nome_usuario", ""),
                emp.get("data_retirada", ""),
                emp.get("status", "")
            ])

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=relatorio_emprestimos.csv"}
        )

    #  Se pedirem PDF:
    elif formato.lower() == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)


        pdf.cell(200, 10, txt="Relatorio de Emprestimos", ln=True, align='C')
        pdf.ln(5)


        pdf.set_font("Arial", 'B', 10)
        pdf.cell(15, 10, "ID", 1)
        pdf.cell(45, 10, "Equipamento", 1)
        pdf.cell(35, 10, "Patrimonio", 1)
        pdf.cell(45, 10, "Usuario", 1)
        pdf.cell(25, 10, "Data", 1)
        pdf.cell(25, 10, "Status", 1)
        pdf.ln()


        pdf.set_font("Arial", size=9)
        for emp in emprestimos:
            pdf.cell(15, 10, str(emp.get("emprestimo_id", "")), 1)
            pdf.cell(45, 10, str(emp.get("nome_equipamento", ""))[:20], 1)
            pdf.cell(35, 10, str(emp.get("codigo_patrimonio", ""))[:15], 1)
            pdf.cell(45, 10, str(emp.get("nome_usuario", ""))[:20], 1)
            pdf.cell(25, 10, str(emp.get("data_retirada", ""))[:10], 1)
            pdf.cell(25, 10, str(emp.get("status", ""))[:10], 1)
            pdf.ln()
        pdf_bytes = bytes(pdf.output(dest='S'))

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=relatorio_emprestimos.pdf"}
        )


    else:
        raise HTTPException(status_code=400, detail="Formato invalido. Use ?formato=csv ou ?formato=pdf")


"""GERAR RELATÓRIO DE EQUIPAMENTOS (CSV E PDF)"""
@router.get("/relatorios/equipamentos", dependencies=[PERMISSAO_TECNICO])
async def relatorio_equipamentos(formato: str = "csv", usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await equipamento_repositorio.listar_equipamentos()
    equipamentos = resultado.get("equipamentos", [])

    if formato.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(["ID", "Patrimonio", "Nome", "Modelo"])
        for eq in equipamentos:
            writer.writerow([eq.get("id", ""), eq.get("codigo_patrimonio", ""), eq.get("nome", ""), eq.get("modelo", "")])
        return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=relatorio_equipamentos.csv"})
    elif formato.lower() == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Relatorio de Equipamentos", ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Arial", size=9)
        for eq in equipamentos:
            pdf.cell(0, 10, f"ID: {eq.get('id')} | Pat: {eq.get('codigo_patrimonio')} | Nome: {eq.get('nome')} | Mod: {eq.get('modelo')}", 1, 1)
        return Response(content=bytes(pdf.output(dest='S')), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=relatorios.pdf"})
    raise HTTPException(status_code=400, detail="Formato invalido")

"""GERAR RELATÓRIO DE USUÁRIOS (CSV E PDF)"""
@router.get("/relatorios/usuarios", dependencies=[PERMISSAO_TECNICO])
async def relatorio_usuarios(formato: str = "csv", usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await usuario_repositorio.listar_usuarios()
    usuarios = resultado.get("usuarios", [])
    if formato.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(["ID", "Nome", "Email", "Tipo"])
        for u in usuarios:
            writer.writerow([u.get("id", ""), u.get("nome", ""), u.get("email", ""), u.get("tipo_usuario", "")])
        return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=relatorio_usuarios.csv"})
    elif formato.lower() == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Relatorio de Usuarios", ln=True, align='C')
        for u in usuarios:
            pdf.cell(0, 10, f"ID: {u.get('id')} | Nome: {u.get('nome')} | Email: {u.get('email')} | Tipo: {u.get('tipo_usuario')}", 1, 1)
        return Response(content=bytes(pdf.output(dest='S')), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=usuarios.pdf"})
    raise HTTPException(status_code=400, detail="Formato invalido")

"""GERAR RELATÓRIO DE MANUTENÇÕES (CSV E PDF)"""
@router.get("/relatorios/manutencoes", dependencies=[PERMISSAO_TECNICO])
async def relatorio_manutencoes(formato: str = "csv", data_inicial: str = None, data_final: str = None, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await manutencao_repositorio.listar_manutencoes()
    manutencoes = resultado.get("manutencoes", [])

    if data_inicial and data_final:
        manutencoes_filtradas = []
        for m in manutencoes:
            data_ab = str(m.get("data_abertura", ""))[:10]
            if data_ab and data_inicial <= data_ab <= data_final:
                manutencoes_filtradas.append(m)
        manutencoes = manutencoes_filtradas

    if formato.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(["ID", "Equipamento", "Defeito", "Abertura"])
        for m in manutencoes:
            writer.writerow([m.get("id", ""), m.get("id_equipamento", ""), m.get("descricao_defeito", ""), m.get("data_abertura", "")])
        return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=relatorio_manutencoes.csv"})
    elif formato.lower() == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Relatorio de Manutencoes", ln=True, align='C')
        for m in manutencoes:
            pdf.cell(0, 10, f"ID: {m.get('id')} | Eqp: {m.get('id_equipamento')} | Defeito: {str(m.get('descricao_defeito'))[:30]} | Data: {m.get('data_abertura')}", 1, 1)
        return Response(content=bytes(pdf.output(dest='S')), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=manutencoes.pdf"})
    raise HTTPException(status_code=400, detail="Formato invalido")

"""GERAR RELATÓRIO DE RESERVAS (CSV E PDF)"""
@router.get("/relatorios/reservas", dependencies=[PERMISSAO_TECNICO])
async def relatorio_reservas(formato: str = "csv", data_inicial: str = None, data_final: str = None, usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await reserva_repositorio.listar_reservas()
    reservas = resultado.get("reservas", [])

    if data_inicial and data_final:
        reservas_filtradas = []
        for r in reservas:
            data_res = str(r.get("data_reserva", ""))[:10]
            if data_res and data_inicial <= data_res <= data_final:
                reservas_filtradas.append(r)
        reservas = reservas_filtradas

    if formato.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(["ID", "Equipamento", "Usuario", "Data"])
        for r in reservas:
            writer.writerow([r.get("id", ""), r.get("id_equipamento", ""), r.get("id_usuario", ""), r.get("data_reserva", "")])
        return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=relatorio_reservas.csv"})
    elif formato.lower() == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Relatorio de Reservas", ln=True, align='C')
        for r in reservas:
            pdf.cell(0, 10, f"ID: {r.get('id')} | Eqp: {r.get('id_equipamento')} | Usu: {r.get('id_usuario')} | Data: {r.get('data_reserva')}", 1, 1)
        return Response(content=bytes(pdf.output(dest='S')), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=reservas.pdf"})
    raise HTTPException(status_code=400, detail="Formato invalido")

"""GERAR RELATÓRIO DE CATEGORIAS (CSV E PDF)"""
@router.get("/relatorios/categorias", dependencies=[PERMISSAO_TECNICO])
async def relatorio_categorias(formato: str = "csv", usuario_logado: dict = Depends(obter_usuario_atual)):
    resultado = await categoria_repositorio.listar_categorias()
    categorias = resultado.get("categorias", [])
    if formato.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(["ID", "Nome", "Descricao"])
        for c in categorias:
            writer.writerow([c.get("id", ""), c.get("nome", ""), c.get("descricao", "")])
        return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=relatorio_categorias.csv"})
    elif formato.lower() == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Relatorio de Categorias", ln=True, align='C')
        for c in categorias:
            pdf.cell(0, 10, f"ID: {c.get('id')} | Nome: {c.get('nome')} | Desc: {str(c.get('descricao'))[:40]}", 1, 1)
        # 🔴 CORREÇÃO: bytes(...) no lugar de .encode('latin1')
        return Response(content=bytes(pdf.output(dest='S')), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=categorias.pdf"})
    raise HTTPException(status_code=400, detail="Formato invalido")




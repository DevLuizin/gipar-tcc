"""Testes de caracterização do contrato HTTP público da API."""

from main import app


EXPECTED_ROUTES = {
    ("GET", "/"),
    ("POST", "/criar_categoria"),
    ("GET", "/listar_categorias"),
    ("PUT", "/atualizar_categoria/{categoria_id}"),
    ("DELETE", "/excluir_categoria/{categoria_id}"),
    ("POST", "/criar_usuario"),
    ("GET", "/usuarios/me"),
    ("PUT", "/usuarios/me"),
    ("PUT", "/usuarios/me/senha"),
    ("PUT", "/usuarios/me/tema"),
    ("GET", "/listar_usuarios"),
    ("GET", "/listar_usuarios/tipo/{tipo}"),
    ("GET", "/buscar_usuario/{usuario_id}"),
    ("PUT", "/atualizar_usuario/{usuario_id}"),
    ("PATCH", "/alterar_tipo_usuario/{usuario_id}"),
    ("PATCH", "/inativar_usuario/{usuario_id}"),
    ("PATCH", "/reativar_usuario/{usuario_id}"),
    ("POST", "/criar_equipamento"),
    ("GET", "/listar_equipamentos"),
    ("PUT", "/atualizar_equipamento/{equipamento_id}"),
    ("PATCH", "/inativar_equipamento/{equipamento_id}"),
    ("PATCH", "/reativar_equipamento/{equipamento_id}"),
    ("DELETE", "/excluir_equipamento/{equipamento_id}"),
    ("POST", "/criar_manutencao"),
    ("GET", "/listar_manutencoes"),
    ("PUT", "/atualizar_manutencao/{manutencao_id}"),
    ("DELETE", "/excluir_manutencao/{manutencao_id}"),
    ("POST", "/criar_reserva"),
    ("GET", "/listar_reservas"),
    ("PUT", "/atualizar_reserva/{reserva_id}"),
    ("DELETE", "/excluir_reserva/{reserva_id}"),
    ("POST", "/criar_emprestimo"),
    ("GET", "/listar_emprestimos"),
    ("PUT", "/atualizar_emprestimo/{emprestimo_id}"),
    ("PUT", "/devolver_emprestimo/{emprestimo_id}"),
    ("PATCH", "/cancelar_emprestimo/{emprestimo_id}"),
    ("GET", "/relatorios/emprestimos"),
    ("GET", "/relatorios/equipamentos"),
    ("GET", "/relatorios/usuarios"),
    ("GET", "/relatorios/manutencoes"),
    ("GET", "/relatorios/reservas"),
    ("GET", "/relatorios/categorias"),
    ("GET", "/listar_historico"),
    ("GET", "/diagnostico/manutencao/{manutencao_id}"),
    ("POST", "/testar-email"),
    ("POST", "/login"),
    ("GET", "/listar_logs"),
    ("GET", "/dashboard/estatisticas"),
    ("POST", "/chat"),
    ("POST", "/chat/reload"),
    ("POST", "/api/chat"),
    ("POST", "/api/chat/reload"),
}


def test_contrato_de_rotas_deve_ser_preservado():
    rotas = {
        (metodo, rota.path)
        for rota in app.routes
        for metodo in (rota.methods or set())
        if rota.path not in {"/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"}
        and metodo not in {"HEAD", "OPTIONS"}
    }

    assert rotas == EXPECTED_ROUTES

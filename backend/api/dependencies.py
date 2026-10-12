"""Dependências compartilhadas pelos routers da API."""

import os

from dotenv import load_dotenv
from fastapi import Depends
from pymysql.cursors import DictCursor

from gerenciador_db.auditoria import AuditoriaRepositorio
from gerenciador_db.categoria import CategoriaRepositorio
from gerenciador_db.emprestimo import EmprestimoRepositorio
from gerenciador_db.equipamento import EquipamentoRepositorio
from gerenciador_db.historico import HistoricoRepositorio
from gerenciador_db.manutencao import ManutencaoRepositorio
from gerenciador_db.reserva import ReservaRepositorio
from gerenciador_db.usuario import UsuarioRepositorio
from seguranca import verificar_permissao
from servicos.dashboard import DashboardService


load_dotenv()

config_db = {
    "host": os.getenv("host") or os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("user") or os.getenv("DB_USER", "root"),
    "password": (
        os.getenv("password")
        if os.getenv("password") is not None
        else os.getenv("DB_PASSWORD", "")
    ),
    "database": os.getenv("database") or os.getenv("DB_NAME", "gipar_db"),
    "cursorclass": DictCursor,
}

categoria_repositorio = CategoriaRepositorio(config_db)
usuario_repositorio = UsuarioRepositorio(config_db)
equipamento_repositorio = EquipamentoRepositorio(config_db)
manutencao_repositorio = ManutencaoRepositorio(config_db)
reserva_repositorio = ReservaRepositorio(config_db)
emprestimo_repositorio = EmprestimoRepositorio(config_db)
auditoria_repositorio = AuditoriaRepositorio(config_db)
historico_repositorio = HistoricoRepositorio(config_db)
dashboard_service = DashboardService(config_db)

emprestimo_repositorio.set_historico_repositorio(historico_repositorio)
manutencao_repositorio.set_historico_repositorio(historico_repositorio)
reserva_repositorio.set_historico_repositorio(historico_repositorio)
emprestimo_repositorio.set_reserva_repositorio(reserva_repositorio)

PERMISSAO_ADMIN = Depends(verificar_permissao(["ADMINISTRADOR"]))
PERMISSAO_TECNICO = Depends(
    verificar_permissao(["ADMINISTRADOR", "TECNICO"])
)
PERMISSAO_TODOS = Depends(
    verificar_permissao(["ADMINISTRADOR", "TECNICO", "COMUM"])
)

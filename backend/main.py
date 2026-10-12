"""Ponto de entrada e composição da API GIPAR."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from chat.router import router as chat_router
except ModuleNotFoundError as err:
    if err.name in ("chat", "chat.router"):
        from backend.chat.router import router as chat_router
    else:
        raise

from api.routers import (
    auth,
    auditoria,
    categorias,
    dashboard,
    emprestimos,
    equipamentos,
    historico,
    manutencoes,
    relatorios,
    reservas,
    sistema,
    usuarios,
)


app = FastAPI(debug=False)
logger = logging.getLogger("uvicorn.error")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(
        f"Erro interno não tratado na rota {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": (
                "Ocorreu um erro interno no servidor. "
                "Tente novamente mais tarde."
            )
        },
    )


origens_config = os.getenv("CORS_ORIGINS", "")
origens_permitidas = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:80",
    "http://localhost",
    "http://127.0.0.1",
]
if origens_config:
    origens_permitidas.extend(
        origem.strip()
        for origem in origens_config.split(",")
        if origem.strip()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_permitidas,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Módulo de Chatbot Inteligente (REQ-001)
app.include_router(chat_router)
app.include_router(chat_router, prefix="/api")

app.include_router(sistema.router)
app.include_router(categorias.router)
app.include_router(usuarios.router)
app.include_router(equipamentos.router)
app.include_router(manutencoes.router)
app.include_router(reservas.router)
app.include_router(emprestimos.router)
app.include_router(relatorios.router)
app.include_router(historico.router)
app.include_router(auth.router)
app.include_router(auditoria.router)
app.include_router(dashboard.router)
